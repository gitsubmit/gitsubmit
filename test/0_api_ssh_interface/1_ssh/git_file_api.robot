*** Settings ***
Documentation     Test suite that contains tests related to the Git File API / Classes
Resource          resource.robot
Library           LocalActionsLib
Library           APIClientLib
Library           Collections
Suite Setup       get filesystem from docker instance

*** Test Cases ***
Can read a file from known repo using master
    should be able to read file file1.txt from known repo

Can read a nested file from known repo using master
    should be able to read file dir_a/file_a1.txt from known repo

Can read a directory from known repo using master
    Should be able to read directory dir_a from known repo

*** Keywords ***
Should be able to read file ${file} from known repo
    ${obj}=  get project file or dir from api  ${ROOT_URL}  test_class  test_project  master  ${file}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${headers}=  get from dictionary  ${obj}  headers
    dictionary should not contain key  ${headers}  is_tree
    ${content}=  get from dictionary  ${obj}  data
    should contain  ${content}  some data

Should be able to read directory ${directory} from known repo
    ${obj}=  get project file or dir from api  ${ROOT_URL}  test_class  test_project  master  ${directory}
    ${code}=  get from dictionary  ${obj}  status_code
    should be equal as integers  ${code}  200
    ${headers}=  get from dictionary  ${obj}  headers
    dictionary should contain key  ${headers}  is_tree
    ${content}=  get from dictionary  ${obj}  data

Get filesystem from docker instance
    do get filesystem from docker  ${TEMP_PATH}