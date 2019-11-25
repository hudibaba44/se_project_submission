from pymongo import MongoClient
mongo_client = MongoClient('localhost', 27017)
database_SE = mongo_client.SE
class backend_db_service:
    # code_editor_db = None
    def __init__(self):
        self.users_db = database_SE.users
        self.framework_db = database_SE.framework

    def clear_users_db(self):
        self.users_db.drop()
     
    def create_dictionary_user_id_project_id(self, user_id, project_id):
        return  {
                "user_id": user_id,
                "project_id": project_id
            }

    def users_db_get_document_for_email_id(self, email_id):
        document = {"email_id" : email_id}
        return self.users_db.find_one(document)

    def users_db_get_document_for_email_id_password(self, email_id, password):
        document = {
            "email_id" : email_id,
            "password" : password
            }

        return self.users_db.find_one(document)

    def users_db_insert_email_id_password_name(self, email_id, password, name):
        document = {
            "email_id" : email_id ,
            "password": password,
            "name" : name
            }
        return self.users_db.insert_one(document)


    def framework_db_get_document_for_email_id_framework(
        self, email_id, framework):
        document = {
            "email_id": email_id,
            "framework": framework
        }
        return self.framework_db.find_one(document)

    def framework_db_insert_email_id_framework_folder_path(
        self, email_id, framework, folder_path):
        document = {
            "email_id" : email_id ,
            "framework": framework,
            "folder_path" : folder_path
            }
        return self.framework_db.insert_one(document)
