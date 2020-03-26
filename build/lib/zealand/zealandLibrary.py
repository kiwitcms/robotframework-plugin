import os.path
import tempfile
import tcms_api
import datetime

class zealandLibrary:
    
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
     
    def __init__(self,url,username,password,plan_id=0):
        self.rpc_client = tcms_api.TCMS(url,username,password).exec
        self.plan_id = plan_id       
        self.test_run_id =0
        self.test_case_statuses= {}
        self.products= {}
        self.builds= {}
        self.categories= {}
        #RobotFramework ha PASS E FAIL come risultato dei test: Kiwi ha come identificativo PASSED e FAILED
        self.test_exec_statuses = {'IDLE':1,'RUNNING': 2,'PAUSED':3, 'PASS': 4, 'FAIL': 5 ,'BLOCKED': 6,'ERROR': 7, 'WAIVED': 8}
        self.test_case_list= []
        self.NOW = datetime.datetime.now().isoformat().replace('T',' ')[:19]
        self.set_categories()
        self.set_builds()
        self.set_products()
        self.set_test_case_statuses()
        
    def set_test_plan(self,plan_id):
        self.plan_id= plan_id
    
    def set_categories(self):
        categories= self.rpc_client.Category.filter({})
        for category in categories:
            self.categories[category['name']]= category['id']
    
    def set_builds(self):
        builds= self.rpc_client.Build.filter({})
        for build in builds:
            self.builds[build['product']] = build['build_id']
        
    def set_test_case_statuses(self):
        case_statuses=self.rpc_client.TestCaseStatus.filter({})
        for case in case_statuses:
            self.test_case_statuses[case['name']]=case['id']
    
    def set_products(self):
        products= self.rpc_client.Product.filter({})
        for product in products:
            self.products[product['name']]=product['id']
        
    def create_test_run(self,notes=''): 
        targetPlan=self.rpc_client.TestPlan.filter({'plan_id':self.plan_id})[0]
        test_run=self.rpc_client.TestRun.create({
            'start_date': datetime.datetime.strptime(self.NOW, '%Y-%m-%d %H:%M:%S'),
            'plan': targetPlan['plan_id'],
            'product' : self.products['DocFly'],
            'manager' : targetPlan['author_id'],
            'product_version' : targetPlan['product_version_id'],
            'type': targetPlan['type'],
            'build' :  self.builds['DocFly'],
            'summary' : targetPlan['name'],
            'notes': notes
            })
        self.test_run_id= test_run['run_id']
        for test in self.rpc_client.TestCase.filter({'plan': self.plan_id,'case_status':self.test_case_statuses.get('CONFIRMED')}):
            self.rpc_client.TestRun.add_case(test_run['run_id'],test['case_id'])
        return test_run['run_id']   
    
    def add_proposed_test_to_run(self,test_doc,test_name,test_category):
        test_to_add=self.rpc_client.TestCase.create({
            'is_automated': True,
            'text': test_doc,
            'summary' : test_name,
            'author_id': self.rpc_client.User.filter({})[0]['id'],
            'case_status': self.test_case_statuses.get('PROPOSED'),
            'category': self.categories.get(test_category),
            'priority': 5,
            'product': self.products.get('DocFly'),
            'plan':self.plan_id
            })
        self.rpc_client.TestPlan.add_case(self.plan_id,test_to_add['case_id'])
        
    def check_test_case(self,test_tags,test_status,test_name,test_doc):
        test_id=int(test_tags[0])
        test_category=test_tags[1]
        test_case_run=self.rpc_client.TestExecution.filter({'run_id':self.test_run_id,'case_id': test_id})
        if(test_case_run):
            self.test_case_list.append({'id': test_case_run[0]['case_run_id'],'status': test_status, 'doc': test_doc })
        else:
            is_already_proposed=self.rpc_client.TestCase.filter({'plan':self.plan_id,'summary': test_name, 'case_status': self.test_case_statuses.get('PROPOSED') })
            if(is_already_proposed):
                return
            else:
                self.add_proposed_test_to_run(test_doc,test_name,test_category)
    
    def update_testExecutions(self):
        for test_run in self.rpc_client.TestRun.get_cases(self.test_run_id):
            x=[t for t in self.test_case_list if t['id'] == test_run['case_run_id']]
            if(x== []):
                self.rpc_client.TestExecution.update(test_run['case_run_id'],{'status':self.test_exec_statuses.get('WAIVED')})
                self.rpc_client.TestExecution.add_comment(test_run['case_run_id'],'Test not executed and updated with Waived status')
            else:
                self.rpc_client.TestExecution.update(x[0]['id'],{'status':self.test_exec_statuses.get(x[0]['status'])})
                message= x[0]['doc'] + '\n Test executed with status:' + x[0]['status'] 
                self.rpc_client.TestExecution.add_comment(x[0]['id'],message)
        self.close_test_run()
       
    def close_test_run(self):
        stop_date =  datetime.datetime.strptime(self.NOW, '%Y-%m-%d %H:%M:%S')
        self.rpc_client.TestRun.update(self.test_run_id,{'stop_date':stop_date,'default_tester':self.rpc_client.User.filter({})[0]['id']})

    #Need to be fixed
    def add_report_to_plan(self,path):
        filename=os.path.basename(path)
        self.rpc_client.TestPlan.add_attachment(self.plan_id,filename,'html')
        
    
if __name__ == "__main__":
    z=zealandLibrary()
