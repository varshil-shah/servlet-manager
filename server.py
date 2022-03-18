import os.path

from subprocess import Popen, CREATE_NEW_CONSOLE


def handle_server(tomcat_folder_path: str, command: str):
    Popen([os.path.join(tomcat_folder_path, "bin\\catalina.bat"), command],
          creationflags=CREATE_NEW_CONSOLE)


def stop_server(tomcat_folder_path: str):
    handle_server(tomcat_folder_path, "stop")


def start_server(tomcat_folder_path: str):
    handle_server(tomcat_folder_path, "start")


def restart_server(tomcat_folder_path: str):
    handle_server(tomcat_folder_path, "stop")
    handle_server(tomcat_folder_path, "start")


