*** Settings ***
Documentation     A test suite with tests pertaining to the ssh key portion of the API
Resource          ../../resources/resource.robot
Library           ../../libraries/SSHKeyLib.py
Library           ../../libraries/HTTPClientLib.py
Library           Collections

*** Test Cases ***
Can list SSH keys of existing user
    HTTP Status Of Get URL Should Be    ${ROOT_URL}/${TEST_USERNAME}/ssh_keys/    200

Can add and delete an SSH key from an existing user
    Given the test user is authenticated
    ${valid_key}=    a valid key is sent to api for user "${TEST_USERNAME}"
    Then key "${valid_key}" can be deleted from the user "${TEST_USERNAME}"

Cannot add an SSH key to user if it already exists
    Given the test user is authenticated
    ${valid_key}=    a valid key is sent to api for user "${TEST_USERNAME}"
    Then same key "${valid_key}" cannot be added to user "${TEST_USERNAME}" again

Cannot add an invalid SSH key to user
    Given the test user is authenticated
    Then user "${TEST_USERNAME}" cannot add invalid public key

Cannot delete last key from user
    Given all keys but one deleted from user "${TEST_USERNAME}"
    Then user "${TEST_USERNAME}" cannot delete the last key


*** Keywords ***
Get list of keys associated with user "${username}"
    ${request}=    get url    ${ROOT_URL}/${username}/ssh_keys/
    ${request_json}=    get http json content from request    ${request}
    dictionary should contain key    ${request_json}    keys
    @{keylist}=    get from dictionary    ${request_json}    keys
    [Return]    @{keylist}

Get number of keys associated with user "${username}"
    ${keylist}=    get list of keys associated with user "${username}"
    ${keylist_length}=    get length    ${keylist}
    [Return]    ${keylist_length}

all keys but one deleted from user "${username}"
    ${number_of_keys}=   get number of keys associated with user "${username}"
    @{list}=    get list of keys associated with user "${username}"
    :FOR    ${index}    IN RANGE    1    ${number_of_keys}
    \    ${delete_payload}=    create dictionary    pkey=@{list}[${index}]
    \    HTTP Status Of Delete URL Should Be    ${ROOT_URL}/${username}/ssh_keys/    ${delete_payload}    200

a valid key is sent to api for user "${username}"
    ${initial_keylist_length}=   get number of keys associated with user "${username}"
    ${key_dict}=    create bogus key
    ${pkey_contents}=    get from dictionary    ${key_dict}    pubkey_contents
    ${payload}=    create dictionary    pkey_contents=${pkey_contents}
    HTTP Status Of Post URL Should Be    ${ROOT_URL}/${username}/ssh_keys/    ${payload}    200
    ${keylist_length_after_insert}=    get number of keys associated with user "${username}"
    ${expected_length}=    evaluate    ${initial_keylist_length} + 1
    should be equal as integers    ${keylist_length_after_insert}    ${expected_length}
    [Return]      ${pkey_contents}

same key "${duplicate}" cannot be added to user "${username}" again
    ${keylist_length_before_insert}=    get number of keys associated with user "${username}"
    ${payload}=    create dictionary    pkey_contents=${duplicate}
    HTTP Status Of Post URL Should Be    ${ROOT_URL}/${username}/ssh_keys/    ${payload}    400
    ${keylist_length_after_insert}=    get number of keys associated with user "${username}"
    should be equal as integers    ${keylist_length_before_insert}    ${keylist_length_after_insert}


key "${valid_key}" can be deleted from the user "${username}"
    ${key_string}=    convert ssh key to colon string    ${valid_key}
    ${initial_keylist_length}=    get number of keys associated with user "${username}"
    ${delete_payload}=    create dictionary    pkey=${key_string}
    HTTP Status Of Delete URL Should Be    ${ROOT_URL}/${username}/ssh_keys/    ${delete_payload}    200
    ${keylist_length_after_delete}=    get number of keys associated with user "${username}"
    ${expected_length}=    evaluate    ${initial_keylist_length} - 1
    should be equal as integers    ${keylist_length_after_delete}    ${expected_length}

user "${username}" cannot add invalid public key
    ${initial_keylist_length}=   get number of keys associated with user "${username}"
    ${payload}=    create dictionary    pkey_contents=this is not a valid public key ya nerd
    HTTP Status Of Post URL Should Be    ${ROOT_URL}/${username}/ssh_keys/    ${payload}    400
    ${keylist_length_after_insert}=    get number of keys associated with user "${username}"
    should be equal as integers    ${keylist_length_after_insert}    ${initial_keylist_length}

user "${username}" cannot delete the last key
    @{keylist}=    get list of keys associated with user "${username}"
    ${delete_payload}=    create dictionary    pkey=@{keylist}[0]
    HTTP Status Of Delete URL Should Be    ${ROOT_URL}/${username}/ssh_keys/    ${delete_payload}    400