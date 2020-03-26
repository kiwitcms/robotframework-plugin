ZealandLibrary & Zealand Listener
=================================

The tcms_api is changed: now it need 3 parameters:
	-'https://tcms.server/xml-rpc/'
	-'your_username'
	-'your_password'

(You need to add the certificate for the connection with the server)

This library is used for create a Test Run on Kiwi TCMS after a test suite is executed on RobotFramework.
The interaction between the library and RobotFramework test suite is handled by a RobotFramework listener called ZealandListener.
What we need:
- A test plan on Kiwi TCMS with all the test cases we need to execute on RobotFramework.Test cases must be marked as Confirmed
- A variable in the RobotFramework file with the id of Kiwi test plan called ${plan_Id}
- A variable in the RobotFramework file with the name of the product of Kiwi test plan calln ${product}

- A specified test case structure on RobotFramework: the [Tags] must have as first argument the id of the test case on kiwi and
  the second argument is the category. (You can add test that is not in the test plan but their structure must be the same)

In RobotFramework configuration you need to add the listener:
--lister absolute_path_of_the_listener

What you need to change in the Listener in order to work:
Add these  3 arguments:
	-url:'https://tcms.server/xml-rpc/'
	-username:'your_username'
	-password:'your_password'
	
How it works:
The ZealandLibrary create the connection with the client with the tcms API by using this function:
      self.rpc_client = tcms_api.TCMS('https://your-kiwiTCMS-link/xml-rpc/','username','password').exec
The ZealandListener at the start of the suite do the following thinks:
	-Get the value of the variable with the plan_id ${testPlanId} 
	-Get the product name of what are yoy testing
	-Call the ZealandLibrary function create_test_run which create the test_run.
	-After the test run is created we add all the test_case with status CONFIRMED of the test plan in the run.

After the end of the test execution the listener call the zealandLibrary function check_test_case.
With the test_id,plan_id we check if the test is in status CONFIRMED and we put the information of the test (tags,status,name,documentation) on a  list that will be used later.
This control is not made on the test inside the test_run but on all test case in kiwi because if the tester create a test in RobotFramework we want to add it in the test_plan
If the test is not in status CONFIRMED we check if the test was already proposed. If it's not PROPOSED we add in the test_plan with status: PROPOSED.

After the end of the suite the listener call the ZealandLibrary function update_test_run.
The function check if  the id of every test in the run is the list we created before.
If it's in the list this means that the test was executed and his status is updated.
If it's in not in the list this means that the test was not executed and his status will become : WAIVED.
After this control the test run is closed.


==================================
Struttura Generale da usare su RobotFramework: 
    E' Necessario avere l'identificativo del test plan e i singoli identificativi 
    dei singoli test_case associati al piano di test
    Create un dictionary con le informazioni dei test case da usare: nel dictionary
    per ora aggiungere 
       kiwi_id: identificativo del test
       category: tipo di categoria del test (API, WEB)
    SUITE SETUP
    All'inizio dell'esecuzione della suite di test viene invocata la keyword: 
    Create Test Run dove viene creata la Run di test: in particolare viene preso
    passato l' identificativo del piano di test e viene creata la run aggiungendo
    ogni test case con stato CONFIRMED presente nel piano di test.
    TEST TEARDOWN
    Alla fine dell'esecuzione di un singolo test viene invocata la keyword ADD TEST CASE
    passando i tag del test, il nome ,la documentazione associata e il suo stato.
    I tag del test sono l'identificativo e il tipo di categoria.
    Tramite l'identificativo del test case , del test plan controllo se il test e' presente
    nella run controllando sempre che lo stato sia CONFIRMED. Se e' presente esso viene creato
    un dictionary e aggiunto in una lista. Il dictionary ha la seguente struttura:
        id: identificativo della test case run
        status: lo stato del test( PASS,FAILED) 
        doc: documentazione del test 
    Se il test non e' presente nella run esso viene aggiunto nel test plan con lo status PROPOSED.
    SUITE TEARDOWN
    Alla fine della suite viene eseguito un controllo su tutti i test case presenti nella run:
    se il test case e' presente nella lista precedente esso viene aggiornato con lo stato del test
    eseguito. Se il test case non e' presente nella lista significa che non e' stato eseguito 
    e quindi viene aggiornato il suo stato con WAIVED
