import os
from zealandLibrary import zealandLibrary
from robot.libraries.BuiltIn import BuiltIn

class zealandListener:
    
    _shared_state = {}
    ROBOT_LISTENER_API_VERSION = 2
         
    def __init__(self):
        self.__dict__ = self._shared_state
        self.url= ''
        self.username=''
        self.password=''
        self.test_plan=0
        self.suite_name=''
        self.node= ''
    
    def start_suite(self, name, attrs):
        self.test_plan=BuiltIn().get_variable_value('${plan_Id}')
        if (self.test_plan is not None and self.suite_name is not name):
            self.suite_name=name
            self.url= BuiltIn().get_variable_value('${kiwi_url}')
            self.username= BuiltIn().get_variable_value('${kiwi_username}')
            self.password= BuiltIn().get_variable_value('${kiwi_password}')
            self.zealandLibrary= zealandLibrary(self.url,self.username,self.password)
            self.zealandLibrary.set_test_plan(self.test_plan)
            self.zealandLibrary.set_node(BuiltIn().get_variable_value('${node_name}'))
            self.zealandLibrary.create_test_run(BuiltIn().get_variable_value('${product}'),BuiltIn().get_variable_value('${build_user_email}'),attrs['doc'])
        else:
            return

    def end_test(self, name, attrs):
        self.zealandLibrary.check_test_case_and_update(attrs['tags'][0],attrs['status'],name,attrs['doc'],attrs['message'])
        
    def end_suite(self,name,attrs):
        if(name==self.suite_name):
            jenkins_tag=BuiltIn().get_variable_value('${jenkins_tag}')
            self.zealandLibrary.close_test_run(jenkins_tag)