__authors__ = ["shawkins", "Tsintsir", "sonph", "LeBat"]  # add yourself!

# internal (project libs)
from config import GITOLITE_ADMIN_PATH
from gitolite import GitoliteWrapper, UserDoesNotExistError, KeyDoesNotExistError, \
    CannotDeleteOnlyKeyError, KeyAlreadyExistsError

# base (python packages)

# external (pip packages)
from flask import Flask, jsonify
from flask import request
from sshpubkeys import InvalidKeyException

app = Flask(__name__)
app.debug = True  # TODO: unset this after release!


@app.route('/')
def hello_world():
    return jsonify({"hello": "world"})


@app.route('/<username>/ssh_keys/', methods=['GET'])
def list_ssh_keys(username):
    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    if not gw.user_exists(username):
        return jsonify({"error": "username not found!", "exception": None}), 404
    return jsonify(keys=gw.get_list_of_pretty_key_strings(username))


@app.route('/<username>/ssh_keys/', methods=['POST'])
def post_new_ssh_key(username):
    if False:  # TODO: ensure that username exists
        return jsonify({"error": "username does not exist"}), 404

    if False:  # TODO: ensure user is authed and is self
        return jsonify({"error": "Unauthorized"}), 401

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    pkey_contents = request.form.get("pkey_contents")

    if not pkey_contents:
        return jsonify({"error": "No key was given!"}), 400

    try:
        pretty_key_hex = gw.add_pkey_to_user(username, pkey_contents)
        return jsonify(key_added=pretty_key_hex)
    except InvalidKeyException as e:
        return jsonify({"error": "Public key was invalid format", "exception": str(e)}), 400
    except KeyAlreadyExistsError as e:
        return jsonify({"error": "Public key already exists", "exception": str(e)}), 400
    except UserDoesNotExistError as e:
        return jsonify({"error": "username not found!", "exception": str(e)}), 404


@app.route('/<username>/ssh_keys/', methods=['DELETE'])
def remove_key_from_user(username):
    if False:  # TODO: ensure user is authed and is self
        return jsonify({"error": "Unauthorized"}), 401

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    pkey = request.form.get("pkey")

    try:
        result = gw.remove_key_from_user_by_pretty_string(username, pkey)
    except KeyDoesNotExistError as e:
        return jsonify({"error": "Key does not exist for user!", "exception": str(e)}), 404
    except CannotDeleteOnlyKeyError as e:
        return jsonify({"error": "Can't delete the only key on the account!", "exception": str(e)}), 400
    if not result:
        return jsonify({"error": "Key was not found under user!", "exception": None}), 404
    return list_ssh_keys(username)
