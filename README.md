# se_project_submission

Doc link -> https://docs.google.com/document/d/10LS89MR5z4EFpyr6MCvc6h33QDean_v4BKbW9zkQ_Uw/edit?usp=sharing

Backend <br>
Repository - Backend and Container Repository (https://github.com/hudibaba44/se_project_submission)<br>
Dependencies - <br>
Install environment.yml using conda. <br>
https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file

backend folder<br>
backend.py is run using nginx and gunicorn. It is the server the frontend interacts with.<br>
It’s API’s are <br>
/signup<br>
/login<br>
/code_editor (sends request to container microservice)<br>
/deploy_server (sends request to container microservice)<br>
/code_editor_password (sends request to container microservice)<br>
/framework_signup (creates folder, and git user, repo)<br>
/framework_signup_exists<br>

database_backend.py handles all database requests. <br>
Mongo is used as the database. <br>
It connects to a common database shared by the container microservice.<br>
Database name - ‘SE’<br>
Users collection - ‘users’<br>
Frameworks collection - ‘frameworks’<br>

git_backend,py  handles git requests.<br>
It needs the IP address of the git server and authentication token.<br>

Initial_folders contains folders that are copied to the users folder during sign up of the framework.

code folder<br>
Code_server_with_python_g++_git folder contains the dockerfile which adds on to the image from https://github.com/cdr/code-server. It installs python3, build essentials and git.<br>
Add on to this dockerfile if anything more is needed.

Dockerfiles folder contains the dockerfiles to build and run the user's files according to the framework chosen.

app.py is deployed on port 5001 and backend.py requests services from it.   
It is the microservice responsible for creating/deleting the text editor and the test server for the user.

API’s<br>
/code_editor (creates code editor)<br>
/code_editor_password (retrieves password)<br>
/deploy (creates server for user to test on)<br>

Frontend<br>
Git Repository: Frontend and Content Server (https://github.com/mehulgarg/se-project-frontend)<br>
Dependencies<br>
Install all the dependencies by navigating to the main folder<br>
Then run the `npm install` command<br>
All the peer dependencies have to be installed manually<br>

Learning-platform folder<br>
The frontend runs on the default Angular Server<br>
There are multiple components<br>
There are shared components which are used inside multiple components<br>
The nav-bar component is the top navigation bar<br>
The login-component contains the login page<br>
The register-component contains the registration page<br>
The services maintain the state of the application and broadcast data across components<br>
The user models explore the  data sent by various APIs<br>
The AppConstants maintains the keys for the session storage which is very similar to JavaScript<br> localStorage<br>
The assets folder contains the various images and thumbnails used in the frontend.<br>

The Content Server<br>
The content server contains all the content for the learning platform<br>
The content server must be running along with frontend server.<br>
The content.py file contains all the content<br>
The folder contains the various JSON files for the content of individual frameworks<br>

Drone<br>
In the drone dockerfile change the gitea server ip to the one on which gitea is setup.<br>
Follow the steps in https://docs.drone.io/installation/providers/gitea/<br>
Change the client id and client secret.<br>
docker-compose is there in the backend repo.<br>

Git Server<br>
https://gitea.io/en-us/<br>

