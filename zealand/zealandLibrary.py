import ast
import datetime

import tcms_api


class zealandLibrary:

    _shared_state = {}

    def __init__(self, url, username, password, plan_id=0):
        self.__dict__ = self._shared_state
        self.rpc_client = tcms_api.TCMS(url, username, password).exec
        self.plan_id = plan_id
        self.product = ''
        self.test_run_id = 0
        self.test_case_statuses = {}
        self.products = {}
        self.builds = {}
        self.categories = {}
        self.priority = {}
        self.node = ''
        # RobotFramework has PASS & FAIL, Kiwi TCMS has PASSED e FAILED
        # todo: this mapping isn't very good b/c statuses are now dynamic and
        # can be deleted or names can be changed/translated. We can use
        # positive/negative/0 weight instead
        self.test_exec_statuses = {
            'IDLE': 1,
            'RUNNING': 2,
            'PAUSED': 3,
            'PASS': 4,
            'FAIL': 5,
            'BLOCKED': 6,
            'ERROR': 7,
            'WAIVED': 8}
        self.NOW = datetime.datetime.now().isoformat().replace('T', ' ')[:19]
        self.set_test_case_statuses()
        self.set_priority()
        self.set_products()

    def set_node(self, node):
        self.node = node

    def set_test_plan(self, plan_id):
        self.plan_id = plan_id

    def set_categories(self):
        categories = self.rpc_client.Category.filter(
            {'product_id': self.products.get(self.product)})
        for category in categories:
            self.categories[category['name']] = category['id']

    def set_builds(self):
        builds = self.rpc_client.Build.filter(
            {'product_id': self.products.get(self.product)})
        for build in builds:
            self.builds[build['product']] = build['id']

    def set_test_case_statuses(self):
        case_statuses = self.rpc_client.TestCaseStatus.filter({})
        for case in case_statuses:
            self.test_case_statuses[case['name']] = case['id']

    def set_products(self):
        products = self.rpc_client.Product.filter({})
        for product in products:
            self.products[product['name']] = product['id']

    def set_priority(self):
        priorities = self.rpc_client.Priority.filter({})
        for priority in priorities:
            self.priority[priority['value']] = priority['id']

    def create_test_run(self, product, test_executor_email, notes=''):
        self.product = product
        self.set_categories()
        self.set_builds()
        executor = self.rpc_client.User.filter({'email': test_executor_email})
        executor_id = ''
        if executor != []:
            executor_id = executor[0]['id']
        targetPlan = self.rpc_client.TestPlan.filter({'id': self.plan_id})[0]
        test_run = self.rpc_client.TestRun.create({
            'start_date': datetime.datetime.strptime(self.NOW,
                                                     '%Y-%m-%d %H:%M:%S'),
            'plan': targetPlan['id'],
            'product': self.products.get(self.product),
            'manager': targetPlan['author_id'],
            'default_tester': executor_id if not '' else None,
            'product_version': targetPlan['product_version_id'],
            'type': targetPlan['type'],
            'build':  self.builds.get(self.product),
            'summary': targetPlan['name'],
            'notes': notes
        })
        self.test_run_id = test_run['id']
        self.rpc_client.TestRun.add_tag(
            test_run['id'],
            'Il nodo Jenkins che ha eseguito la run : {0}'.format(self.node))
        for test in self.rpc_client.TestCase.filter({
                'plan': self.plan_id,
                'case_status': self.test_case_statuses.get('CONFIRMED')}):
            self.rpc_client.TestRun.add_case(self.test_run_id, test['id'])
        return test_run['id']

    def add_proposed_test_to_run(self, test_doc, test_name, test_category):
        test_to_add = self.rpc_client.TestCase.create({
            'is_automated': True,
            'text': test_doc,
            'summary': test_name,
            'author': self.rpc_client.User.filter({})[0]['id'],
            'case_status': self.test_case_statuses.get('PROPOSED'),
            'category': self.categories.get(test_category),
            'priority': 5,
            'requirement': 'Need to be reviewed',
            'product': self.products.get(self.product),
            'plan': self.plan_id
        })
        self.rpc_client.TestPlan.add_case(self.plan_id, test_to_add['id'])

    def check_test_case_and_update(self,
                                   test_tags,
                                   test_status,
                                   test_name,
                                   test_doc,
                                   test_message):
        tags = ast.literal_eval(test_tags)
        test_id = int(tags['kiwi_id'])
        test_category = tags['category']
        test_case_run = self.rpc_client.TestExecution.filter(
            {'run_id': self.test_run_id, 'case_id': test_id})
        if(test_case_run):
            test_case_to_update = {
                'execution_id': test_case_run[0]['id'],
                'status': test_status,
                'doc': test_doc,
                'message': test_message,
                'case_id': test_id,
                'jid': tags['jid']
            }
            self.update_testExecutions(test_case_to_update)
        else:
            # FIXME:: NON FUNZIONA CORRETTAMENTE
            is_already_proposed = self.rpc_client.TestCase.filter({
                'plan': self.plan_id,
                'id': test_id,
                'case_status': self.test_case_statuses.get('PROPOSED')
            })
            if(is_already_proposed != []):
                self.add_proposed_test_to_run(
                    test_doc, test_name, test_category)

    def update_testExecutions(self, updated_test):
        test_list = []
        for t in self.rpc_client.TestRun.get_cases(self.test_run_id):
            if t['execution_id'] == updated_test['execution_id']:
                test_list.append(t)

        x = list({v['id']: v for v in test_list}.values())
        if(x == []):
            self.rpc_client.TestExecution.update(
                updated_test['execution_id'],
                {'status': self.test_exec_statuses.get('WAIVED')})
            self.rpc_client.TestExecution.add_comment(
                updated_test['execution_id'],
                'Test not executed and updated with Waived status')
        else:
            if(x[0]['status'] == 'IDLE'):
                new_status = self.test_exec_statuses.get(
                    updated_test['status'])
                self.rpc_client.TestExecution.update(
                    x[0]['execution_id'],
                    {'status': new_status})
                message = 'Test executed with status:' + \
                    updated_test['status'] + '\n' + updated_test['message']
                self.rpc_client.TestExecution.add_comment(
                    x[0]['execution_id'], message)
                # Find a better way to handle it
                if updated_test['jid']:
                    self.rpc_client.TestCase.add_tag(
                        x[0]['id'], updated_test['jid'])

    def close_test_run(self, jenkins_tag):
        manual_test = [t for t in self.rpc_client.TestRun.get_cases(
            self.test_run_id) if t['is_automated'] is not True]
        if not manual_test:
            stop_date = datetime.datetime.strptime(
                self.NOW, '%Y-%m-%d %H:%M:%S')
            if jenkins_tag is not None:
                self.rpc_client.TestRun.add_tag(self.test_run_id, jenkins_tag)
            self.rpc_client.TestRun.update(
                self.test_run_id,
                {
                    'stop_date': stop_date,
                    'default_tester': self.rpc_client.User.filter({})[0]['id']
                })
        else:
            for test in manual_test:
                self.rpc_client.TestExecution.add_comment(
                    test['execution_id'], 'Test da eseguire manualmente')
                self.rpc_client.TestExecution.update(
                    test['execution_id'],
                    {'status': self.test_exec_statuses.get('RUNNING')})
