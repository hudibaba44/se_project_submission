from pymongo import MongoClient
mongo_client = MongoClient('localhost', 27017)
database_SE = mongo_client.SE 
class code_editor_db_service:
    def __init__(self):
        self.code_editor_db = database_SE.code_editor
    def create_dictionary_user_id_project_id(self, user_id, project_id):
        return  {
                "user_id": user_id,
                "project_id": project_id
            }

    def insert_user_id_project_id_ip_address_port_no_container_id_password(self,
        user_id, project_id, ip_address, port_no, container_id, password):
            document_to_insert = {
                "user_id": user_id,
                "project_id": project_id,
                "ip_address": ip_address,
                "port_no": port_no,
                "container_id": container_id,
                "password": password
            }
            self.code_editor_db.insert_one(document_to_insert)
    def get_container_id(self, user_id, project_id):
        document_to_find = self.create_dictionary_user_id_project_id(user_id, project_id)
        print(document_to_find)
        document = self.code_editor_db.find_one(document_to_find)
        return None if document is None else document['container_id']

    def delete_user_id_project_id(self, user_id, project_id):
        document_to_delete = self.create_dictionary_user_id_project_id(user_id, project_id)
        self.code_editor_db.delete_one(document_to_delete)

    def get_document_for_user_id_project_id(self, user_id, project_id):
        document_to_find = self.create_dictionary_user_id_project_id(user_id, project_id)
        return self.code_editor_db.find_one(document_to_find)
    
    def get_all_documents_for_ip_address(self, ip_address):
        query_ip_address = {
            'ip_address': ip_address
            }
        return self.code_editor_db.find(query_ip_address)
    
    def get_all_ports(self):
        query = {
             "port_no": 1, 
             "_id": 0
        }
        return self.code_editor_db.find({}, query)
        


class deployment_server_db_service:
    def __init__(self):
        self.deployment_server_db = database_SE.deployment_server
    def create_dictionary_user_id_project_id(self, user_id, project_id):
        return  {
                "user_id": user_id,
                "project_id": project_id
            }

    def insert_user_id_project_id_ip_address_port_no_container_id(self,
        user_id, project_id, ip_address, port_no, container_id):
            document_to_insert = {
                "user_id": user_id,
                "project_id": project_id,
                "ip_address": ip_address,
                "port_no": port_no,
                "container_id": container_id
            }
            self.deployment_server_db.insert_one(document_to_insert)
    def get_container_id(self, user_id, project_id):
        document_to_find = self.create_dictionary_user_id_project_id(user_id, project_id)
        print(document_to_find)
        document = self.deployment_server_db.find_one(document_to_find)
        return None if document is None else document['container_id']

    def delete_user_id_project_id(self, user_id, project_id):
        document_to_delete = self.create_dictionary_user_id_project_id(user_id, project_id)
        self.deployment_server_db.delete_one(document_to_delete)

    def get_document_for_user_id_project_id(self, user_id, project_id):
        document_to_find = self.create_dictionary_user_id_project_id(user_id, project_id)
        return self.deployment_server_db.find_one(document_to_find)
    
    def get_all_documents_for_ip_address(self, ip_address):
        query_ip_address = {
            'ip_address': ip_address
            }
        return self.deployment_server_db.find(query_ip_address)
    
    def get_all_ports(self):
        query = {
             "port_no": 1, 
             "_id": 0
        }
        return self.deployment_server_db.find({}, query)
