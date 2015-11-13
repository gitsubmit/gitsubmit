
__authors__ = ["shawkins", "Tsintsir", "sonph", "LeBat"]  # add yourself!

# internal (project libs)
from config import GITOLITE_ADMIN_PATH, DATABASE_PORT, STATIC_REPOS_ROOT
from db import UsernameAlreadyTakenError, EmailAlreadyTakenError
from git_browser import GitRepo
from gitolite import GitoliteWrapper, UserDoesNotExistError, KeyDoesNotExistError, \
    CannotDeleteOnlyKeyError, KeyAlreadyExistsError
from db import  ClassDoesNotExistError, UrlNameAlreadyTakenError, DatabaseWrapper, ProjectDoesNotExistError

# base (python packages)

# external (pip packages)
from flask import Flask, jsonify, request, Response
from sshpubkeys import InvalidKeyException

app = Flask(__name__)
app.debug = True  # TODO: unset this after release!


def configured_main(custom_gitolite_path, custom_repository_root_path, database_port):
    """ For testing versions of the API, we can point to a different gitolite admin directory, and a different database.
    Note that if this is not called (instead, gunicorn is invoked with app:app) then all defaults remain.

    :param custom_gitolite_path: path to local git instance of gitolite
    :param database_port: integer of port where mongodb is served
    :return: wsgi app instance
    """

    # first, set these attributes as global, so that in later uses, we get THESE versions
    global GITOLITE_ADMIN_PATH, DATABASE_PORT, STATIC_REPOS_ROOT
    GITOLITE_ADMIN_PATH = custom_gitolite_path
    DATABASE_PORT = database_port
    STATIC_REPOS_ROOT = custom_repository_root_path

    # gunicorn requires that whatever method we call returns the wsgi app, so:
    return app


@app.route('/')
def hello_world():
    return jsonify({"hello": "world"})


@app.route('/<username>/ssh_keys/', methods=['GET'])
def list_ssh_keys(username):
    """ covered by test 1_users / `Can list user's SSH keys` """
    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)
    if not gw.user_exists(username):
        return jsonify({"error": "username not found!", "exception": None}), 404
    return jsonify(keys=gw.get_list_of_pretty_key_strings(username))


@app.route('/login/', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    result = dbw.login(username, password)
    if not result:
        return jsonify({"error": "bad login credentials!", "exception": None}), 400
    # TODO: authentication: return token from login
    return jsonify({"token": result}), 200


@app.route('/<username>/ssh_keys/', methods=['POST'])
def post_new_ssh_key(username):
    """ covered by 1_users / `User can add an ssh key` """
    if False:  # TODO: ensure that username exists
        return jsonify({"error": "username does not exist"}), 404

    if False:  # TODO: ensure user is authed and is self
        return jsonify({"error": "Unauthorized"}), 401

    pkey_contents = request.form.get("pkey_contents")

    if not pkey_contents:
        return jsonify({"error": "No key was given!"}), 400

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)

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
    """ covered by 1_users / `User can delete an existing key from themselves` """
    if False:  # TODO: ensure user is authed and is self
        return jsonify({"error": "Unauthorized"}), 401

    pkey = request.form.get("pkey")

    gw = GitoliteWrapper(GITOLITE_ADMIN_PATH)

    try:
        result = gw.remove_key_from_user_by_pretty_string(username, pkey)
    except KeyDoesNotExistError as e:
        return jsonify({"error": "Key does not exist for user!", "exception": str(e)}), 404
    except CannotDeleteOnlyKeyError as e:
        return jsonify({"error": "Can't delete the only key on the account!", "exception": str(e)}), 400
    if not result:
        return jsonify({"error": "Key was not found under user!", "exception": None}), 404
    return list_ssh_keys(username)

@app.route('/<username>/update/', methods=['POST'])
def update_user_info():
    dbw = DatabaseWrapper()
    username = "konrad" #TODO: get currently logged in user
    new_email = request.form.get("email")
    dbw.update_email(username, new_email)
    return jsonify(email_added=new_email)


@app.route('/signup/', methods=['POST'])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    first_name = request.form.get("firstname")
    last_name = request.form.get("lastname")

    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.create_user(username, password,email, first_name, last_name)
    except UsernameAlreadyTakenError as e:
        return jsonify({"error": "Username is already taken!", "exception": str(e)}), 400
    except EmailAlreadyTakenError as e:
        return jsonify({"error": "Email is already taken!", "exception": str(e)}), 400
    result = dbw.login(username, password)
    return jsonify({"token": result}), 200

@app.route('/<username>/update_password/<temp_password_key>/', methods=['POST'])
def update_user_password():
    dbw = DatabaseWrapper()
    username = "konrad"
    new_password = request.form.get("password")
    dbw.update_password(username, new_password)
    return jsonify(password_added=new_password)


@app.route('/classes/')
def list_classes():
    """ covered by test 0_classes / `Can list classses` """
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify(classes=dbw.get_all_classes())


@app.route('/classes/', methods=["POST"])
def new_class():
    """ covered by test 0_classes / `Can create classes` """
    class_name = request.form.get("class_name")
    url_name = request.form.get("url_name")
    description = request.form.get("description")

    owner = "spencer"  # TODO: get currently logged in user
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        c = dbw.create_class(url_name, class_name, description, owner)
        print c
        return jsonify(class_created=url_name)
    except UrlNameAlreadyTakenError as e:
        return jsonify({"error": "Url name was already taken!", "exception": str(e)}), 403


@app.route('/classes/<class_url>/projects/')
def list_projects(class_url):
    """ covered by test 2_projects / `Can list projects in a class` """
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify(projects=dbw.get_all_projects_for_class(class_url))


@app.route('/classes/<class_url>/owner/')
def class_owner(class_url):
    """ covered by test 0_classes / `Can get the owner of a class`"""
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        class_obj = dbw.get_class_or_error(class_url)
        return jsonify(owner=class_obj["owner"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/teachers/')
def class_teachers(class_url):
    """ covered by test 0_classes / `Can get the teachers of a class`"""
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        class_obj = dbw.get_class_or_error(class_url)
        return jsonify(teachers=class_obj["teachers"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/students/')
def class_students(class_url):
    """ civered by test 0_classes / `Can list students in a class` """
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        class_obj = dbw.get_class_or_error(class_url)
        return jsonify(students=class_obj["students"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/student/', methods=["POST"])
def add_student(class_url):
    """ covered by test 0_classes / `Student can enroll in a class` """
    student = request.form.get("username")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)

    try:
        dbw.add_student_to_class(class_url, student)
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404
    except UserDoesNotExistError as e:
        return jsonify({"error": "username not found!", "exception": str(e)}), 404

    return jsonify(class_updated=dbw.get_class_or_error(class_url))


@app.route('/classes/<class_url>/teacher/', methods=["POST"])
def add_teacher(class_url):
    """ covered by test 0_classes / `Teacher can add other teachers to class they own` """
    teacher = request.form.get("username")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)

    try:
        dbw.add_teacher_to_class(class_url, teacher)
    except ClassDoesNotExistError as e:
        return jsonify({"error": "class not found!", "exception": str(e)}), 404
    except UserDoesNotExistError as e:
        return jsonify({"error": "username not found!", "exception": str(e)}), 404

    return jsonify(class_updated=dbw.get_class_or_error(class_url))


@app.route('/classes/<class_url>/projects/<project_url>/owner/')
def get_project_owner(class_url, project_url):
    """ covered by test 2_projects / `Can get owner of a project` """
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        project_obj = dbw.get_project_or_error(class_url, project_url)
        return jsonify(owner=project_obj["owner"])
    except ClassDoesNotExistError as e:
        return jsonify({"error": "project not found!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/projects/', methods=["POST"])
def new_project(class_url):
    """ covered by test 2_projects / `Teacher can create new project` """
    project_name = request.form.get("project_name")
    url_name = request.form.get("url_name")
    description = request.form.get("description")
    team_based = request.form.get("team_based") in ["True", "true", "Yes", "yes"]
    max_size = int(request.form.get("max_members"))
    due_date = request.form.get("due_date")  # TODO: check formatting from js

    owner = "spencer"  # TODO: get currently logged in user

    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.create_project(url_name, project_name, description, class_url, team_based, due_date, owner, max_size)
        return jsonify(project_created=url_name)
    except UrlNameAlreadyTakenError as e:
        return jsonify({"error": "Url name was already taken!", "exception": str(e)}), 403
    except ClassDoesNotExistError as e:
        return jsonify({"error": "Class does not exist!", "exception": str(e)}), 404


@app.route('/classes/<class_url>/projects/<project_url>/due_date/', methods=["POST"])
def new_project_due_date(class_url, project_url):
    """ covered by test 2_projects / `Can update due date in a project` """
    due_date = request.form.get("date")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return jsonify(project_updated=dbw.update_project_due_date(class_url, project_url, due_date))


@app.route('/classes/<class_name>/projects/<project_name>/make_submission/', methods=["POST"])
def make_submission(class_name, project_name):
    owner = request.form.get("owner")
    url_name = '/' + owner + '/submissions/' + project_name + '/'
    parent_url = '/' + class_name + '/projects/' + project_name + '/'
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.create_submission(url_name, project_name, parent_url, owner)
        return jsonify(submission_made=url_name)
    except UrlNameAlreadyTakenError as e:
        return jsonify({"error": "Url name was already taken!", "exception": str(e)}), 403
    except ProjectDoesNotExistError as e:
        return jsonify({"error": "That project does not exist!", "exception": str(e)}), 404
    except ClassDoesNotExistError as e:
        return jsonify({"error": "Class does not exist!", "exception": str(e)}), 404


@app.route('/<username>/submissions/<submission_name>/contributors/', methods=['POST'])
def add_contributor(username, submission_name):
    new_contributor = request.form.get("username")
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.add_contributor(username, submission_name, new_contributor)
        return jsonify(contributor_added=new_contributor)
    except StandardError as e:
        return jsonify({"error": "Placeholder error until exceptions are raised by the backend.", "exception": str(e)}), 404


@app.route('/<username>/submissions/<submission_name>/contributors/<removed_username>', methods=['DELETE'])
def remove_contributor(username, submission_name, removed_username):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    try:
        dbw.remove_contributor(username, submission_name, removed_username)
        return jsonify(contributor_removed=removed_username)
    except StandardError as e:
        return jsonify({"error": "Placeholder error until exceptions are raised by the backend.", "exception": str(e)}), 404


@app.route('/<username>/submissions/<submission_name>/contributors/', methods=['GET'])
def get_contributors(username, submission_name):
    dbw = DatabaseWrapper(GITOLITE_ADMIN_PATH, DATABASE_PORT)
    return dbw.get_contributors(username, submission_name)


# Note: this is not a routed method
def get_file_or_directory(local_path, commit_path, filepath):
    repo = GitRepo(local_path)
    object = repo.get_file_or_directory(commit_path, filepath)

    resp = Response(mimetype="text/plain")

    if object["type"] == "tree":
        resp.headers['is_tree'] = True
        response_content = ""
        for item in object["file_list"]:
            response_content += item["name"]
            if item["type"] == "tree":
                response_content += "/"
            response_content += "\n"
        resp.set_data(response_content)
    else:
        resp.set_data(object["content"])
    return resp


@app.route('/<username>/submissions/<submission_name>/source/<commit_path>/<path:filepath>')
def get_submission_file_or_directory(username, submission_name, commit_path, filepath):
    git_repo_path = username + "/submissions/" + submission_name
    local_path = STATIC_REPOS_ROOT + "/" + git_repo_path + ".git"
    return get_file_or_directory(local_path, commit_path, filepath)


@app.route('/classes/<class_url>/projects/<project_url>/source/<commit_path>/<path:filepath>')
def get_project_file_or_directory(class_url, project_url, commit_path, filepath):
    git_repo_path = class_url + "/" + project_url
    local_path = STATIC_REPOS_ROOT + "/" + git_repo_path + ".git"
    return get_file_or_directory(local_path, commit_path, filepath)
