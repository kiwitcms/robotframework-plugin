*** Settings ***
Documentation   A simple suite for integration test purposes
Library         OperatingSystem

*** Test Cases ***
Hello World Scenario
    [Documentation]    This will be the text in DB
    Should Be Equal    "Hello"    "Hello"
