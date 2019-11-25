from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from pathlib import Path
import os
import docker
import json
# import .database_code_editor
from database_code_editor import code_editor_db_service, deployment_server_db_service
import time
import shutil
from time import sleep
from abc import ABC, abstractmethod
import string
import random 

app = Flask(__name__)
api = Api(app)
docker_client = docker.from_env()


CODE_EDITOR_IMAGE_NAME = "neeleshca26/code_server"
#Default port for text editor
PORT_OF_CONTAINER = '8080/tcp'
PATH_TO_BIND_HOST_FOLDER_TO_CONTAINER = "/home/project"
START_PORT_FOR_EDITOR = 5500
START_PORT_FOR_DEPLOYED_SERVER = 6000
# Look up ip from ifconfig.
# HOST_IP = "192.168.43.144"
HOST_IP = "0.0.0.0"
PATH_TO_DOCKERFILES = Path(os.path.realpath(__file__)).parents[0]/"dockerfiles"
code_editor_db = code_editor_db_service()
deployment_server_db = deployment_server_db_service()


class docker_file_creator(ABC):
    @abstractmethod
    def factory_method(self):
        pass

    def copy_files_to_folder(self, folder_path, dest_path):
        product = self.factory_method()
        product.copy_files(folder_path, dest_path)


class concrete_flask_creator(docker_file_creator):
    def factory_method(self):
        return concrete_flask_product()


class concrete_express_creator(docker_file_creator):
    def factory_method(self):
        return concrete_express_product()

class concrete_django_creator(docker_file_creator):
    def factory_method(self):
        return concrete_django_product()

class concrete_node_creator(docker_file_creator):
    def factory_method(self):
        return concrete_node_product()

class dockerfile_product(ABC):
    @abstractmethod
    def copy_files(self, folder_path, dest_path):
        pass


class concrete_flask_product(dockerfile_product):
    def copy_files(self, folder_path, dest_path):
        shutil.copytree(folder_path, dest_path/"app")
        dockerfile_path = get_dockerfile_path("flask")
        shutil.copy(dockerfile_path, dest_path/"Dockerfile")
        docker_ignore_path = get_dockerfile_ignore_path("flask")
        if docker_ignore_path is not None:
            shutil.copy(docker_ignore_path, dest_path/".dockerignore")


class concrete_express_product(dockerfile_product):
    def copy_files(self, folder_path, dest_path):
        shutil.copytree(folder_path, dest_path)
        dockerfile_path = get_dockerfile_path("express")
        shutil.copy(dockerfile_path, dest_path/"Dockerfile")
        docker_ignore_path = get_dockerfile_ignore_path("express")
        if docker_ignore_path is not None:
            shutil.copy(docker_ignore_path, dest_path/".dockerignore")

class concrete_django_product(dockerfile_product):
    def copy_files(self, folder_path, dest_path):
        shutil.copytree(folder_path, dest_path/"app")
        dockerfile_path = get_dockerfile_path("django")
        shutil.copy(dockerfile_path, dest_path/"Dockerfile")
        docker_ignore_path = get_dockerfile_ignore_path("django")
        if docker_ignore_path is not None:
            shutil.copy(docker_ignore_path, dest_path/".dockerignore")

class concrete_node_product(dockerfile_product):
    def copy_files(self, folder_path, dest_path):
        shutil.copytree(folder_path, dest_path)
        dockerfile_path = get_dockerfile_path("node")
        shutil.copy(dockerfile_path, dest_path/"Dockerfile")
        docker_ignore_path = get_dockerfile_ignore_path("node")
        if docker_ignore_path is not None:
            shutil.copy(docker_ignore_path, dest_path/".dockerignore")


def get_dockerfile_object(project_id):
    if 'flask' in project_id:
        return concrete_flask_creator()
    if 'express' in project_id:
        return concrete_express_creator()
    if 'django' in project_id:
        return concrete_django_creator()
    if 'node' in project_id:
        return concrete_node_creator()

def container_run(user_id, project_id, port_no, image_name):
    container_object = None
    if 'flask' in project_id:
        container_object = docker_client.containers.run(
            image_name,
            # Default port
            ports={'5000/tcp': f'{port_no}'},
            detach=True)

    if 'express' in project_id:
        container_object = docker_client.containers.run(
            image_name,
            # Default port
            ports={'8080/tcp': f'{port_no}'},
            detach=True)

    if 'django' in project_id:
        container_object = docker_client.containers.run(
            image_name,
            # Default port
            ports={'8000/tcp': f'{port_no}'},
            detach=True)

    if 'node' in project_id:
        container_object = docker_client.containers.run(
            image_name,
            # Default port
            ports={'8080/tcp': f'{port_no}'},
            detach=True)

    return container_object


def current_micro_time(): return int(round(time.time() * 1000000))


def get_dockerfile_path(project_id):
    if 'flask' in project_id:
        return Path(PATH_TO_DOCKERFILES, "Dockerfile_flask")
    if 'express' in project_id:
        return Path(PATH_TO_DOCKERFILES, "Dockerfile_express")
    if 'django' in project_id:
        return Path(PATH_TO_DOCKERFILES, "Dockerfile_django")
    if 'node' in project_id:
        return Path(PATH_TO_DOCKERFILES, "Dockerfile_node")

def get_dockerfile_ignore_path(project_id):
    if 'express' in project_id:
        return Path(PATH_TO_DOCKERFILES, ".dockerignore_express")
    # if 'node' in project_id:
    #     return Path(PATH_TO_DOCKERFILES, ".dockerignore_node")
    return None


def make_url_server_ip_port_no(server_ip, port_no):
    return str(server_ip) + ":" + str(port_no)
    # return {
    #     'server_ip': server_ip,
    #     'port_no': port_no
    # }


def find_code_editor_user_id_project_id(user_id, project_id):
    document = code_editor_db.get_document_for_user_id_project_id(
        user_id, project_id)
    if(document is None):
        return None
    else:
        return make_url_server_ip_port_no(
            document['ip_address'], document['port_no'])


def find_deployment_server_user_id_project_id(user_id, project_id):
    document = deployment_server_db.get_document_for_user_id_project_id(
        user_id, project_id)
    if(document is None):
        return None
    else:
        return make_url_server_ip_port_no(
            document['ip_address'], document['port_no'])


def get_free_port_code_editor(START_PORT):
    ports = code_editor_db.get_all_ports()
    set_of_ports = set()
    # set_of_ports = [set_of_ports.add(i['port_no']) for i in ports]
    # print("Ports are")
    for i in ports:
        # print(i['port_no'])
        set_of_ports.add(i['port_no'])
    print(set_of_ports)
    free_port = START_PORT
    for i in range(1000):
        if(free_port+i not in set_of_ports):
            return free_port+i
    return None


def get_free_port_deployment_server(START_PORT):
    ports = deployment_server_db.get_all_ports()
    set_of_ports = set()
    # set_of_ports = [set_of_ports.add(i['port_no']) for i in ports]
    # print("Ports are")
    for i in ports:
        # print(i['port_no'])
        set_of_ports.add(i['port_no'])
    print(set_of_ports)
    free_port = START_PORT
    for i in range(1000):
        if(free_port+i not in set_of_ports):
            return free_port+i
    return None

    # return 5500


# Build an image for a given project id.
def build_image(user_id, project_id, folder_path):
    # unique path
    tmp_folder_name = "tmp"+str(current_micro_time())
    tmp_folder_path = Path(tmp_folder_name)
    if(os.path.exists(tmp_folder_path)):
        tmp_folder_name += '1'
        tmp_folder_path = Path(tmp_folder_name)
    # os.mkdir(tmp_folder_path)
    dockerfile_obj = get_dockerfile_object(project_id)
    dockerfile_obj.copy_files_to_folder(folder_path, tmp_folder_path)
    # shutil.copytree(folder_path, tmp_folder_path/"app")
    # dockerfile_path = get_dockerfile_path(project_id)
    # shutil.copy(dockerfile_path, tmp_folder_path/"Dockerfile")
    # print(f'{user_id}_{project_id}')
    tag_name = str(user_id)+"_"+str(project_id)
    # '@' not allowed in name.
    tag_name = tag_name.replace('@', '_')
    # Spaces not allowed in tag name
    docker_client.images.build(path=str(tmp_folder_path),
                               tag=tag_name)

    # shutil.copytree()
    # sleep(2)
    shutil.rmtree(tmp_folder_path)
    return tag_name

# Deploys a text editor for the given user and project id. 
def create_code_editor(user_id, project_id, folder_path):
    path_to_folder = Path(folder_path)
    assert path_to_folder.exists() == 1
    port_no = get_free_port_code_editor(START_PORT_FOR_EDITOR)
    if port_no is None:
        return (None, None)
    container_object = docker_client.containers.run(
        CODE_EDITOR_IMAGE_NAME,
        ports={PORT_OF_CONTAINER: f'{port_no}'},
        volumes={
            path_to_folder: {
                'bind': PATH_TO_BIND_HOST_FOLDER_TO_CONTAINER,
                'mode': 'rw'}
        },
        # network = "host",
        detach=True)
    #Takes some time for the container to start.
    time.sleep(5)
    list_of_logs = container_object.logs().decode("utf-8").split("\n")
    assert "Password is" in list_of_logs[1]
    password = list_of_logs[1].split(' ')[-1]
    code_editor_db.insert_user_id_project_id_ip_address_port_no_container_id_password(
        user_id, project_id, HOST_IP, port_no, container_object.id, password)
    return (HOST_IP, port_no)

# Deploys a container for the given user and project id. 
# A different image is built for each project id.
def create_user_deployed_server(user_id, project_id, folder_path):
    path_to_folder = Path(folder_path)
    assert path_to_folder.exists() == 1
    port_no = get_free_port_deployment_server(START_PORT_FOR_DEPLOYED_SERVER)
    if port_no is None:
        return (None, None)
    image_name = build_image(user_id, project_id, folder_path)
    container_object = container_run(user_id, project_id, port_no, image_name)
    deployment_server_db.insert_user_id_project_id_ip_address_port_no_container_id(
        user_id, project_id, HOST_IP, port_no, container_object.id
    )
    return (HOST_IP, port_no)

#Retrieves container id from database and removes it if present.
def delete_code_editor(user_id, project_id):
    container_id = code_editor_db.get_container_id(user_id, project_id)
    print("Container id is ", container_id)
    if (container_id is None):
        return False
    container = docker_client.containers.get(container_id)
    container.stop()
    container.remove()
    code_editor_db.delete_user_id_project_id(user_id, project_id)
    return True


#Retrieves container id from database and removes it if present.
def delete_deployment_server(user_id, project_id):
    container_id = deployment_server_db.get_container_id(user_id, project_id)
    print("Container id is ", container_id)
    if (container_id is None):
        return False
    container = docker_client.containers.get(container_id)
    container.stop()
    container.remove()
    deployment_server_db.delete_user_id_project_id(user_id, project_id)
    return True


def assert_and_return_user_id_project_id_folder_path(request_data):
    assert 'user_id' in request_data
    assert 'project_id' in request_data
    assert 'folder_path' in request_data
    return (request_data['user_id'],
            request_data['project_id'],
            request_data['folder_path'])


class code_editor(Resource):
    # Creates a text editor for the given user, framework and folder.
    # If a text editor is already present for the user and framework, it returns that URL.
    # Parameters
    # user_id: String
    # project_id: String
    # folder_path: String
    #
    # Response
    # server_ip+":"port_no: String
    def put(self):
        request_data = request.get_json()
        user_id, project_id, folder_path = assert_and_return_user_id_project_id_folder_path(
            request_data)
        result_of_find = find_code_editor_user_id_project_id(
            user_id, project_id)
        if(result_of_find is None):
            server_ip, port_no = create_code_editor(
                user_id, project_id, folder_path)
            return make_response(jsonify(
                    make_url_server_ip_port_no(server_ip, port_no)
                ),
                200
            )
        else:
            return make_response(jsonify(
                    result_of_find
                ),
                200
            )

    # Deletes the text editor for the given user, framework.
    # Parameters
    # user_id: String
    # project_id: String
    # folder_path: String
    #
    # Response
    # 200 status code in cases of successful deletion.
    # 404 status code if a text editor isn't there for the user and framework.
    def delete(self):
        request_data = request.get_json()
        assert 'user_id' in request_data
        assert 'project_id' in request_data
        user_id = request_data['user_id']
        project_id = request_data['project_id']
        # file_path = request_data['file_path']
        if (delete_code_editor(user_id, project_id) is False):
            return make_response("No container exists", 404)
        else:
            return make_response("Container deleted succesfully", 200)

class user_deployed_server(Resource):
    # Creates a test server for the given user, framework and folder. 
    # This is for the user to test.
    # If a server is already present for the user and framework, it returns that URL.
    # Creates servers only for frameworks. i.e. node, express, django and flask. 
    # Not for cpp or python.
    # Parameters
    # user_id: String
    # project_id: String
    # folder_path: String
    #
    # Response
    # server_ip+":"port_no: String
    # 400 for cpp and python as a server doesn't make sense. It can be done in the terminal
    def put(self):
        request_data = request.get_json()
        user_id, project_id, folder_path = assert_and_return_user_id_project_id_folder_path(
            request_data)
        if "cpp" in project_id:
            return make_response({}, 400)
        if "python" in project_id:
            return make_response({}, 400)
        
        result_of_find = find_deployment_server_user_id_project_id(
            user_id, project_id)
        if(result_of_find is None):
            server_ip, port_no = create_user_deployed_server(
                user_id, project_id, folder_path)
            return make_response(jsonify(
                    make_url_server_ip_port_no(server_ip, port_no)
                ),
                200
            )
        else:
            return make_response(jsonify(
                    result_of_find
                ),
                200
            )
            
    # Deletes the test server for the given user, framework.
    # Parameters
    # user_id: String
    # project_id: String
    # folder_path: String
    #
    # Response
    # 200 status code in cases of successful deletion.
    # 404 status code if a deployment server isn't there for the user and framework.
    def delete(self):
        request_data = request.get_json()
        assert 'user_id' in request_data
        assert 'project_id' in request_data
        user_id = request_data['user_id']
        project_id = request_data['project_id']
        # file_path = request_data['file_path']
        if (delete_deployment_server(user_id, project_id) is False):
            return make_response("No container exists", 404)
        else:
            return make_response("Container deleted succesfully", 200)


class code_editor_password(Resource):
    # Returns a password for the text editor for the given user and framework. 
    # The password is needed to access the text editor.
    # Parameters
    # user_id: String
    # project_id: String
    #
    # Response
    # password: String
    # 404 if there is no text editor for the given user and framework
    def get(self):
        request_data = request.get_json()
        print(request_data)
        assert 'user_id' in request_data
        assert 'project_id' in request_data
        user_id = request_data['user_id']
        project_id = request_data['project_id']
        document = code_editor_db.get_document_for_user_id_project_id(
        user_id, project_id)
        if(document is None):
            return make_response("No container exists", 404)
        else:
            return make_response({"password":document['password']}, 200)


api.add_resource(code_editor, '/code_editor')
api.add_resource(code_editor_password, '/code_editor_password')
api.add_resource(user_deployed_server, '/deploy')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
