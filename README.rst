ZealandLibary & ZealandListener
========================
La seguente libreria permette di creare partendo da una suite di test di RobotFramework una run di test su kiwi dove vengono salvati i risutltati dei singoli casi di test eseguiti.
Il collegamento tra la suite e la libreria viene gestito da un listener di RobotFramework chiamato ZealandListener.

Cosa è necessario per utilizzare la libreria:
    1. Un apposito server su Kiwi dove poter caricare i test case, test plan e test run.
    2. Eclipse con RobotFramework installato. Guida https://github.com/NitorCreations/RobotFramework-EclipseIDE/wiki/Installation 
    3. Anaconda per creare un ambiente(environment) dove poter installare le librerie necessarie per eseguire la suite di test di RF. https://www.anaconda.com/distribution/
    

**INSTALLAZIONE**
==========================
Scaricare la libreria dal seguente link: **TO_ADD**.

    1. Aprire Anaconda creare o selezionare un environment dove scaricare la libreria e aprire il terminale.
    
    2. Digitare il seguente comando: pip install path (Path dove è installata la libreria).

**Per fare funzionare il seguente pacchetto in maniera corretta sono necessari dei prerequisiti e delle modifiche da eseguire in ognuno degli elementi citati**
=======================================

**KIWI**
---------------------------------------
Prima di eseguire i test su RobotFramework abbiamo bisogno che su KIWI sia stato creato almeno un piano di test.
Per completezza sarebbe più utile avere già tutti i singoli casi di test già all'interno del piano così da avere un integrazione migliore tra la suite e la run.


**ROBOT FRAMEWORK**
-------------------------------
E' necessario aggiungere sul progetto di RF il certificato del server di KIWI che viene utilizzato.
Sul progetto di RobotFramework sarà necessario aggiungere sul file di red l'enviroment dove è stata installata la libreria.
Sia la Suite di test che i singoli casi di test dovranno essere strutturati nella seguente maniera:
    - Ogni suite deve conteneere le seguenti variabili: 
            1. **${plan_id}**: L'identificativo del piano di test di Kiwi dove sono contenuti i singoli casi di test. 
            
            2. **${product}**: Il nome del prodotto a cui è associato il piano di test.
    - I Tag dei singoli casi di test devono essere un dizionario che contiene i seguenti dati:
            1. **kiwi_id**: L'identificativo del caso di test all'interno del test plan su KIWI.
            2. **category**: La categoria del test case (API/WEB).
            3. **jid**: L'identificativo del test case su Jira (Mettere jid=None se non viene utilizzato Jira).

Per eseguire il listener è necessario aggiungere nella configurazione di RobotFramework il seguente comando:

 --variable kiwi_url:your-url/xml-rpc/ --variable kiwi_username:your-username --variable kiwi_password:your-password --listener /Users/User/Anaconda3/envs/env_name/Lib/site-packages/zealand/zealandListener.py 

Le variabili che vengono passate servono per collegarsi al server KIWI: sostituire your-url,your-username,your-password con l'url del tuo server,l'username e password necessarie per accedervi


Funzionamento della libreria
===================================
All'inizio della suite di test viene creato la test run su KIWI passando come variabili ${plan_id} e ${product} e vengono aggiunti alla run tutti i test case presenti all'interno della run con stato **CONFIRMED**.
Alla fine dell'esecuzione di ogni test viene eseguito un primo controllo se il test case è stato aggiunto nella run. Se è stato aggiunto aggiorno il test presente nella run modificando lo stato di esecuzione del test (Passato,Fallito) aggiungendo un commento. Se è presente il jid nei tag viene aggiunto come tag al test su KIWI.
Se il test non è presente nella run viene controllato se il test è presente nel piano in caso **PROPOSED**. Se il test case non è presente viene aggiunto con status **PROPOSED**.
Se un test case presente nella run di KIWI non è stato eseguito su RF esso viene aggiornato con status **WAIVED**, mentre se un test case è considerato  manuale viene aggiornato con Se un test case presente nella run di KIWI è con automated=false viene aggiornato con Status RUNNING e aggiunto un commento che lo identifica come test manuale da eseguire successivamente.
Alla fine della suite viene aggiunto il tag della build di jenkins (se è eseguito su jenkins) e chiusa la run solamente se non sono presenti test manuali.







    
