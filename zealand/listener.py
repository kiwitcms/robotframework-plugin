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

    def default_tester_id(self):
        """
            If ${build_user_email} is specified witin the suite then use it,
            otherwise default to the user connecting via API!
        """
        user_email = self.built_in.get_variable_value('${build_user_email}')
        result = None

        if user_email:
            result = self.rpc.User.filter({'email': user_email})

        if result:
            return result[0]['id']

        return super().default_tester_id()

    def external_plan_id(self):
        """
            If existing ${plan_id} is specified witin the suite then use it!
        """
        plan_id = self.built_in.get_variable_value('${plan_id}')
        if plan_id:
            return int(plan_id)

        return super().external_plan_id()

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

    def test_run_update(self, attrs):
        """
            Update the currently active TestRun with more information coming
            out from the Robot Framework test suite.
        """
        self.rpc.TestRun.update(self.run_id, {
            'notes': attrs['doc'],
        })

    def rf_test_case_get_or_create(self, attrs):
        """
            A richer version of Backend.test_case_get_or_create() which
            allows searching for existing test cases in different ways:

                1. use pre-existing TestCase if specified in the .robot file
                2. try searching by TC.script && TC.arguments matching the
                   .robot file and test name
                3. search by summary if nothing else works

            Then update the TestCase in DB with more information we can
            obtain from Robot Framework.
        """
        created = False
        test_case = None
        source_file = attrs['suite']['source'].replace(self.cwd, '')

        # search by explicitly specified pre-existing TestCase
        for tag in attrs['tags']:
            tag = tag.lower()
            if tag.startswith('tc-'):
                try:
                    test_case_id = int(tag.replace('tc-', ''))

                    # see if this exists in the DB
                    result = self.rpc.TestCase.filter({'pk': test_case_id})
                    if result:
                        test_case = result[0]
                    break
                except ValueError:
                    pass

        # search by TC.script
        if test_case is None:
            result = self.rpc.TestCase.filter({
                'is_automated': True,
                'script': source_file,
                'arguments': attrs['name'],
                'category__product': self.product_id,
            })
            if result:
                test_case = result[0]

        # search or create by summary if everything else didn't work
        if test_case is None:
            test_case, created = super().test_case_get_or_create(
                attrs['longname'])

        if created:
            notes = attrs['suite']['doc'] or \
                'Created by kiwitcms-robotframework-plugin'

            self.rpc.TestCase.update(
                test_case['id'],
                {
                    'text': attrs['doc'],
                    'notes': notes,
                    'script': source_file,
                    'arguments': attrs['name'],
                },
            )

        return test_case, created

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

    backend_class = RFBackend
    ROBOT_LISTENER_API_VERSION = 2

    # will always trigger at least 1 TR to be created
    test_plan_id = -1

    def __init__(self):
        self.suite = None
        self.backend = self.backend_class(prefix='[RF] ')

    def start_suite(self, name, attrs):  # pylint: disable=unused-argument
        """
            If a pre-existing TP was specified then create a TR for it,
            possibly creating multiple TRs if various suites specify different
            TPs. Otherwise create a new TP + TR to collect the results.
        """
        # skip test suites with empty test list b/c we don't want empty TRs
        if not attrs['tests']:
            return

        external_plan_id = self.backend.external_plan_id()
        # will return 0 if nothing configured ^^^

        # .robot file(s) indicate we need to start a new TR
        # because there is a TestPlan explicitly specified!
        if external_plan_id:
            self.test_plan_id = external_plan_id

        # this is where we create a new TR. All results will be reported
        # in this TR until some of the suite(s) overrides this
        if self.test_plan_id != self.backend.plan_id:
            self.backend.configure()
            self.test_plan_id = self.backend.plan_id

            self.backend.test_run_update(attrs)

        self.suite = attrs

    def end_test(self, name, attrs):  # pylint: disable=unused-argument
        attrs.update({
            'name': name,
            'suite': self.suite,
        })

        test_case, _ = self.backend.rf_test_case_get_or_create(attrs)
        test_case_id = test_case['id']

        self.backend.add_test_case_to_plan(test_case_id, self.backend.plan_id)
        test_execution_id = self.backend.add_test_case_to_run(
            test_case_id,
            self.backend.run_id)

        comment = attrs['message'] or \
            'Result recorded via kiwitcms-robotframework-plugin'
        status_id = self.backend.get_status_id(attrs['status'])

        self.backend.update_test_execution(test_execution_id,
                                           status_id,
                                           comment)

    def end_suite(self, name, attrs):  # pylint: disable=unused-argument
        """
            A suite ends so call finish_test_run().

            If there are more suites which report their results within
            the same TR this will be called multiple times changing
            TR.stop_date every time.

            If we're actually reporting the results to multiple TRs then
            each one of them will be finished accordingly.
        """
        if self.backend.run_id:
            self.backend.finish_test_run()
