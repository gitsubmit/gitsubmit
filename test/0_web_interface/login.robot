*** Settings ***
Documentation     A test suite with a single Gherkin style test.
Resource          ../resources/resource.robot
Library           ../libraries/HTTPClientLib.py
Test Teardown     Close Browser

*** Test Cases ***
Page Is Responsive
    [Tags]  not_implemented
    Given browser is opened to landing page
    When Window dimensions are set to  1920  1080
    Then no operation
    # do something to check that page responded
    capture page screenshot
    Given browser is opened to landing page
    When Window dimensions are set to  600  1080
    Then no operation
    # do something to check that page responded
    capture page screenshot
    Given browser is opened to landing page
    When Window dimensions are set to  400  1080
    Then no operation
    # do something to check that page responded
    capture page screenshot

Valid Login
    [Tags]  not_implemented
    Given browser is opened to login page
    When user "demo" logs in with password "mode"
    Then welcome page should be open

*** Keywords ***
Browser is opened to login page
    Open browser to login page

Browser is opened to landing page
    Open browser to landing page

Window dimensions are set to
    [Arguments]   ${width}    ${height}
    set window size  ${width}  ${height}

User "${username}" logs in with password "${password}"
    Input username    ${username}
    Input password    ${password}
    Submit credentials