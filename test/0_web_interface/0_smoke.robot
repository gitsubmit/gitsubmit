*** Settings ***
Documentation     A test suite with a single Gherkin style smoke test.
Resource          ../resources/resource.robot
Test Teardown     Close Browser


*** Test Cases ***
Test Webserver Is Alive
    [Tags]  smoke_test
    Given testing webserver is running
    Then HTTP Status Of Get URL Should Be  ${ROOT_URL}   200
