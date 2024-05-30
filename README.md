# Veb_server
This project is a web server for file upload with basic HTTP authentication. It allows users to upload files to the server via a web interface. To ensure secure access to the server, HTTP authentication is used, and user passwords are stored in the htpasswd file.

Main features:

File upload: Users can upload files to the server via the web interface.
Basic HTTP authentication: Access to the server requires authentication using a username and password stored in the htpasswd file.
Error and exception handling: The project handles various errors and exceptions, such as missing files, empty file names, and others, to ensure stable application operation.
Launch parameters:

-p or --port: the port on which the server will be running (default is 5000).
-d or --directory: the directory to which files will be uploaded (default is "uploads").
-f or --htpasswd: the path to the htpasswd file where users and their passwords are stored (default is "htpasswd").
This project can be useful for creating a simple and secure web server for file upload with authentication.
