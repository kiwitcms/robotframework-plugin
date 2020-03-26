import os
from zealandLibrary import zealandLibrary
from robot.libraries.BuiltIn import BuiltIn


class zealandListener:
    
    url='https://testlispakiwi.rlarchive.it/xml-rpc/'
    username='zealand'
    password='zealand'
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LISTENER_API_VERSION = 2
         
    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.zealandLibrary= zealandLibrary(self.url,self.username,self.password)
        self.test_plan=0
    
    def start_suite(self, name, attrs):
        self.test_plan=BuiltIn().get_variable_value('${plan_Id}')
        if (self.test_plan == None):
            return 
        else:
            self.zealandLibrary.set_test_plan(self.test_plan)
            self.zealandLibrary.create_test_run(attrs['doc'])

    def end_test(self, name, attrs):
        self.zealandLibrary.check_test_case(attrs['tags'],attrs['status'],name,attrs['doc'])
        
    def end_suite(self,name,attrs):
        self.zealandLibrary.update_testExecutions()
    
    '''
    Non viene invocata alla fine della creazione del report. 
    Capire il motivo
    
    def output_file(self,path):
        self.zealandLibrary.add_report_to_plan(path)
    
    def close(self):
        output_dir = BuiltIn().get_variable_value('${OUTPUT FILE}')
        syslog= BuiltIn().get_variables('${ROBOT_SYSLOG_FILE}')
        print(syslog['OUTPUT_FILE'])
        fp=open(syslog['OUTPUT_FILE'])
        print(fp.read())
        #self.zealandLibrary.add_report_to_plan(output_dir)
    '''