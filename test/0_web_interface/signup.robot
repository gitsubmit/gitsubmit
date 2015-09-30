*** Settings ***
Resource          ../resources/resource.robot
Library           ../libraries/SmokeLib.py
Test Teardown     Close Browser

*** Test Cases ***
Valid Signup
    [Tags]  not_implemented
    Given Browser is opened to signup page page
    When User "demo" signs up with password "longenoughpass" and email "email"
    Then welcome page should be open

Invalid Signup - Blank User
    [Tags]  not_implemented
    Given Browser is opened to signup page page
    When User "" signs up with password "longenoughpass" and email "email"
    Then login page should be open

Invalid Signup - Blank Password
    [Tags]  not_implemented
    Given Browser is opened to signup page page
    When User "demo" signs up with password "" and email "email"
    Then login page should be open

Invalid Signup - Blank Email
    [Tags]  not_implemented
    Given Browser is opened to signup page page
    When User "demo" signs up with password "longenoughpass" and email ""
    Then login page should be open

Invalid Signup - Password Less Than 6 Characters
    [Tags]  not_implemented
    Given Browser is opened to signup page page
    When User "demo" signs up with password "pass" and email "email"
    Then login page should be open

*** Keywords ***
Browser is opened to signup page
    Open Browser To Signup Page page

Window dimensions are set to
    [Arguments]   ${width}    ${height}
    set window size  ${width}  ${height}

User "${username}" signs up with password "${password}" and email "${email}"
    Input username    ${username}
    Input password    ${password}
    Input Email       ${email}
    Submit Signup