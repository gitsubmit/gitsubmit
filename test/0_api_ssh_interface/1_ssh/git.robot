*** Settings ***
Documentation     Test suite that contains tests related to git actions
Resource          resource.robot
Library           LocalActionsLib


*** Test Cases ***
Can clone repo
    [Tags]  api  database  classes
    Given testing webserver is running
    Then should be able to clone a test repo

Can push to repo
    [Tags]  api  database  classes
    Given testing webserver is running
    Then should be able to push to test repo

*** Keywords ***
should be able to clone a test repo
    clone known project  ${TEMP_PATH}
    known project should exist  ${TEMP_PATH}

should be able to push to test repo
    generate complex file structure in known repo  ${TEMP_PATH}
    add files commit and push in known repo  ${TEMP_PATH}
    untracked files should not exist in known repo  ${TEMP_PATH}

