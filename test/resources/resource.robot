*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported Selenium2Library.
...
...               Based on example code at: https://bitbucket.org/robotframework/webdemo/src/6a95fc3744c7?at=master
Library           Selenium2Library
Library           ../libraries/HTTPClientLib.py

*** Variables ***
${SERVER}         localhost:5555
${BROWSER}        Chrome
${DELAY}          0
${VALID USER}     demo
${VALID PASSWORD}    demopass
${ROOT_URL}         http://${SERVER}/
${LOGIN URL}        http://${SERVER}/login
${DASHBOARD URL}    http://${SERVER}/dash
${ERROR URL}        http://${SERVER}/error
${SIGNUP URL}       http://${SERVER}/signup
${TEST_USERNAME}    test_user

*** Keywords ***
Open Browser To Landing Page
    Open Browser To URL     ${ROOT_URL}
    Landing Page Should Be Open

Open Browser To Login Page
    Open Browser To URL    ${LOGIN URL}
    Login Page Should Be Open

Open Browser To Signup Page
    Open Browser To URL    ${SIGNUP URL}
    Signup Page Should Be Open

Open Browser To URL
    [Arguments]  ${URL}
    Open Browser    ${URL}    ${BROWSER}
    set window size    1920    1080
    Set Selenium Speed    ${DELAY}

Login Page Should Be Open
    Title Should Be    Login - GitSubmit

Signup Page Should Be Open
    Title Should Be    Signup - GitSubmit

Landing Page Should Be Open
    Title Should Be    Welcome - GitSubmit

Go To Login Page
    Go To    ${LOGIN URL}
    Login Page Should Be Open

Input Username
    [Arguments]    ${username}
    Input Text    username_field    ${username}

Input Password
    [Arguments]    ${password}
    Input Text    password_field    ${password}

Input Email
    [Arguments]    ${email}
    Input Text    email_field    ${email}

Submit Credentials
    Click Button    login_button

Submit Signup
    Click Button    signup_button

Welcome Page Should Be Open
    Location Should Be    ${SIGNUP URL}
    Title Should Be    GitSubmit - Sign Up

HTTP Status Of Get URL Should Be
    [Arguments]  ${URL}   ${CODE}
    ${request}=     get url    ${URL}
    ${return_code}=    get http status from request    ${request}
    ${return_content}=    get http content from request    ${request}
    should be equal as integers  ${CODE}  ${return_code}

HTTP Status Of Post URL Should Be
    [Arguments]  ${URL}    ${PAYLOAD}    ${CODE}
    ${request}=     post to url    ${URL}    ${PAYLOAD}
    ${return_code}=    get http status from request    ${request}
    ${return_content}=    get http content from request    ${request}
    should be equal as integers  ${CODE}  ${return_code}


HTTP Status Of Delete URL Should Be
    [Arguments]  ${URL}    ${PAYLOAD}    ${CODE}
    ${request}=     delete url    ${URL}    ${PAYLOAD}
    ${return_code}=    get http status from request    ${request}
    ${return_content}=    get http content from request    ${request}
    should be equal as integers  ${CODE}  ${return_code}

testing webserver is running
    no operation
    # this is a test prereq but
    # lol gherkin

the test user is authenticated
    no operation
    # TODO: this

