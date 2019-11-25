import pymongo
from flask import Flask, jsonify, abort, make_response, request, url_for, session
from flask import render_template, redirect
import json
import re
import os
import hashlib
from flask_cors import CORS
from database_backend import backend_db_service
from git_backend import git_service
from pathlib import Path
import requests
from distutils.dir_util import copy_tree

app = Flask(__name__)
CORS(app)
backend_db = backend_db_service()
backend_git = git_service()

# Text editor and test server microservice.
IP_TO_CONTAINER_MICROSERVICE = "http://127.0.0.1:5001/"
URL_TO_CODE_EDITOR = IP_TO_CONTAINER_MICROSERVICE + "code_editor"
URL_TO_CODE_EDITOR_PASSWORD = IP_TO_CONTAINER_MICROSERVICE + "code_editor_password"
URL_TO_DEPLOYMENT_SERVER = IP_TO_CONTAINER_MICROSERVICE + "deploy"
# Users folders are created here.
BASE_DIRECTORY_FOR_USER_FOLDERS = Path(os.path.expanduser('~'), "SE")
#Same directory as this file.
PATH_TO_INITIAL_FOLDERS = Path(os.path.realpath(__file__)).parents[0]/"initial_folders"

# Copies initial folder to user folder.
def copy_initial_folder(folder_path, project_id):
    if 'flask' in project_id:
        copy_tree(PATH_TO_INITIAL_FOLDERS/'flask_initial', folder_path)
    if 'express' in project_id:
        copy_tree(PATH_TO_INITIAL_FOLDERS/'express_initial', folder_path)
    if 'django' in project_id:
        copy_tree(PATH_TO_INITIAL_FOLDERS/'django_initial', folder_path)
    if 'node' in project_id:
        copy_tree(PATH_TO_INITIAL_FOLDERS/'node_initial', folder_path)
    if 'c++' in project_id:
        copy_tree(PATH_TO_INITIAL_FOLDERS/'c++_initial', folder_path)
    if 'python' in project_id:
        copy_tree(PATH_TO_INITIAL_FOLDERS/'python_initial', folder_path)

# @app.route("/", methods = ["GET"])
# def test():
#     backend_db.clear_users_db()
#     return jsonify({}),200



# Adds a user to the database.
# If a user is already present, it returns 400.
# Parameters
# fullName: String
# email: String
# password: String
#
# Response
# email: String
# fullName: String
@app.route("/signup", methods = ["POST"])
def add_user():
    req = eval(request.data)
    print(req)
    name = req["fullName"]
    user_email = req["email"]
    pwd = req["password"]
    document = backend_db.users_db_get_document_for_email_id(user_email)
    status = 400
    res = {}
    if document == None:
        result_of_insert = backend_db.users_db_insert_email_id_password_name(
            user_email, pwd, name)
        status = 200
        res = {
            "email" : user_email,
            "fullName" : name
            }
        print(result_of_insert)
    return jsonify(res), status


# Verifies whether email and password match.
# If it doesn't, it returns 404.
# Parameters
# email: String
# password: String
#
# Response
# email: String
# fullName: String
@app.route("/login", methods = ["POST"])
def login():
    req = eval(request.data)
    user_email = req["email"]
    pwd = req["password"]
    document = backend_db.users_db_get_document_for_email_id_password(user_email, pwd)
    res = {}
    status = 404
    if document is not None and document['password'] == pwd:
        res = {
            "email" : user_email,
            "fullName" : document['name']
            }
        status = 200
    return jsonify(res), status

# Sends a request to the container microservice to create/delete a code editor.
# Parameters
# email: String
# frameworkId: String
#
# Response
# Response of container microservice.
@app.route("/code_editor", methods = ["PUT", "DELETE"])
def code_editor():
    request_data = eval(request.data)
    # print(request_data)
    email_key = "email"
    framework_key = "frameworkId"
    print("REQUEST DATA IS", request_data)
    assert email_key in request_data
    assert framework_key in request_data
    email_id = request_data[email_key]
    framework = request_data[framework_key]
    if request.method == "PUT":
        document = backend_db.framework_db_get_document_for_email_id_framework(
            email_id, framework)
        assert document is not None
        put_request = {
            'user_id': email_id,
            'project_id': framework,
            'folder_path': document['folder_path']
        }
        response = requests.put(URL_TO_CODE_EDITOR, json = put_request)
        print(response.status_code)
        return make_response(
            jsonify(response.text),
            response.status_code
            )

    if request.method == "DELETE":
        delete_request = {
            'user_id': email_id,
            'project_id': framework,
        }
        response = requests.delete(URL_TO_CODE_EDITOR, json = delete_request)
        print(response.status_code)
        print(response.content)
        # response.
        return make_response(
            jsonify(response.text),
            response.status_code
            )

# Sends a request to the container microservice to create/delete a test server.
# Parameters
# email: String
# frameworkId: String
#
# Response
# Response of container microservice.
@app.route("/deploy_server", methods = ["PUT", "DELETE"])
def deploy_server():
    request_data = eval(request.data)
    email_key = "email"
    framework_key = "frameworkId"
    assert email_key in request_data
    assert framework_key in request_data
    email_id = request_data[email_key]
    framework = request_data[framework_key]
    if request.method == "PUT":
        document = backend_db.framework_db_get_document_for_email_id_framework(
            email_id, framework)
        assert document is not None
        put_request = {
            'user_id': email_id,
            'project_id': framework,
            'folder_path': document['folder_path']
        }
        response = requests.put(URL_TO_DEPLOYMENT_SERVER, json = put_request)
        print(response.status_code)
        return make_response(
            jsonify(response.text),
            response.status_code
            )

    if request.method == "DELETE":
        delete_request = {
            'user_id': email_id,
            'project_id': framework,
        }
        response = requests.delete(URL_TO_DEPLOYMENT_SERVER, json = delete_request)
        print(response.status_code)
        print(response.content)
        # response.
        return make_response(
            jsonify(response.text),
            response.status_code
            )



# Sends a request to the container microservice to retrieve the password for the text editor.
# Parameters
# email: String
# frameworkId: String
#
# Response
# Response of container microservice.
@app.route("/code_editor_password", methods = ["GET"])
def code_editor_password():
    request_data = request.args
    print(request_data)
    email_key = "email"
    framework_key = "frameworkId"
    print("REQUEST DATA IS", request_data)
    assert email_key in request_data
    assert framework_key in request_data
    email_id = request_data[email_key]
    framework = request_data[framework_key]
 
    get_request = {
        'user_id': email_id,
        'project_id': framework
    }
    response = requests.get(URL_TO_CODE_EDITOR_PASSWORD, json = get_request)
    print(response.status_code)
    return make_response(
        jsonify(response.text), 
        response.status_code
        )
    

# Signs a user up for a particular framework.
# Creates a folder at BASE_DIRECTORY_FOR_USER_FOLDERS.
# Copies the intiial folder for the given framework there.
# Creates a git user and a git repo.
# Parameters
# email: String
# frameworkName: String
#
# Response
# 200 if success.
# 400 if user already signed up.
@app.route("/framework_signup", methods = ["POST"])
def framework_signup():
    request_data = request.get_json()
    print(request_data)

    email_key = "email"
    framework_key = "frameworkName"
    assert email_key in request_data
    assert framework_key in request_data
    email_id = request_data[email_key]
    framework = request_data[framework_key]
    document = backend_db.framework_db_get_document_for_email_id_framework(email_id, framework)
    folder_path = BASE_DIRECTORY_FOR_USER_FOLDERS/(email_id+"_"+framework)
    # assert os.path.exists(folder_path) is False
    # os.makedirs(folder_path)
    if os.path.exists(folder_path) is False:
        os.makedirs(folder_path)
    copy_initial_folder(str(folder_path), framework)
    status = 400
    if document is None:
        backend_db.framework_db_insert_email_id_framework_folder_path(
            email_id, framework, str(folder_path))
        # create git user
        backend_git.create_user(email_id, framework)
        # create git user.
        backend_git.create_repo(email_id, framework)
        # req = git_backend.create_repo(email_id, framework)
        status = 200
    return jsonify({}), status

# Checks to see if the user has already signed up for the framework.
# Parameters
# email: String
# frameworkName: String
# 
# Response
# 200 if user is signed up for the framework.
# 404 if the user hasn't
@app.route("/framework_signup_exists", methods = ["GET"])
def framework_signup_exists():
    # print("ARGS", request.args)
    request_data = request.args
    email_key = "email"
    framework_key = "frameworkId"
    assert email_key in request_data
    assert framework_key in request_data
    email_id = request_data[email_key]
    framework = request_data[framework_key]
    document = backend_db.framework_db_get_document_for_email_id_framework(email_id, framework)
    if document is None:
        return jsonify({}), 404
    else:
        return jsonify({}), 200



if __name__ == '__main__':
    app.secret_key = "secret_key"
    app.run(debug = True)
