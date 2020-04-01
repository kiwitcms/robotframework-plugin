import os

from robot.libraries.BuiltIn import BuiltIn
from tcms_api.plugin_helpers import Backend


class RFBackend(Backend):
    """
        Kiwi TCMS plugin backend which has richer integration with
        Robot Framework internals than standard backend!
    """
    built_in = BuiltIn()
    cwd = os.getcwd() + os.sep

    def get_run_id(self):
        """
            If ${build_user_email} is specified witin the suite then use it,
            otherwise default to the user connecting via API!

            If ${node_name} is specified then tag the TR with "node: X" tag!
        """
        run_id = super().get_run_id()

        user_email = self.built_in.get_variable_value('${build_user_email}')
        result = None

        if user_email:
            result = self.rpc.User.filter({'email': user_email})

        if result:
            self.rpc.TestRun.update(run_id, {
                'default_tester': result[0]['id'],
            })

        node_name = self.built_in.get_variable_value('${node_name}')
        if node_name:
            self.rpc.TestRun.add_tag(run_id, 'node: %s' % node_name)

        return run_id

    def get_plan_id(self, run_id):
        """
            If existing ${plan_id} is specified witin the suite then use it!
        """
        plan_id = self.built_in.get_variable_value('${plan_id}')
        if plan_id:
            return plan_id

        return super().get_plan_id(run_id)

    def get_product_id(self, plan_id):
        """
            If existing ${product} is specified witin the suite then use it.
            Otherwise fall back to discovering the name from the environment!
        """
        product_name = self.built_in.get_variable_value('${product}')
        if product_name:
            result = self.rpc.Product.filter({'name': product_name})
            if result:
                return result[0]['id'], product_name

        return super().get_product_id(plan_id)

    def test_case_update(self, test_case_id, attrs):
        """
            Update TestCase in DB with more information we can
            obtain from Robot Framework.
        """
        # todo: parent method needs to indicate whether or not
        # a TC is newly created so we can update it with more info here
        # not update it every single time
        source_file = attrs['suite']['source'].replace(self.cwd, '')

        return self.rpc.TestCase.update(
            test_case_id,
            {
                'text': attrs['doc'],
                'notes': 'Created by kiwitcms-robotframework-plugin',
                'script': source_file
            },
        )

    def get_status_id(self, name):
        # translate b/w RF -> Kiwi TCMS statuses
        # we should make the inherited method add the status if missing
        # b/c after v8.0 statuses can be customized
        name = {
            'PASS': 'PASSED',
            'FAIL': 'FAILED',
        }[name]
        return super().get_status_id(name)


class KiwiTCMS:
    """
        Listener class for Robot Framework which can be passed to
        `robot --listener`
    """

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.suite = None

        self.backend = RFBackend(prefix='[RF] ')
        self.backend.configure()

    def start_suite(self, name, attrs):  # pylint: disable=unused-argument
        self.suite = attrs

    def end_test(self, name, attrs):  # pylint: disable=unused-argument
        attrs.update({'suite': self.suite})

        test_case = self.backend.test_case_get_or_create(attrs['longname'])
        test_case = self.backend.test_case_update(test_case['id'], attrs)
        test_case_id = test_case['id']

        self.backend.add_test_case_to_plan(test_case_id, self.backend.plan_id)
        test_execution_id = self.backend.add_test_case_to_run(
            test_case_id,
            self.backend.run_id)

        comment = 'Result recorded via kiwitcms-robotframework-plugin'

        status_id = self.backend.get_status_id(attrs['status'])

        # todo: get comment/traceback from RF is any
        self.backend.update_test_execution(test_execution_id,
                                           status_id,
                                           comment)
