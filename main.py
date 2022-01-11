import os
import sys
from subprocess import Popen, CREATE_NEW_CONSOLE, SubprocessError

from termcolor import colored


def handle_server(tomcat_folder_path: str, command: str):
    Popen([os.path.join(tomcat_folder_path, "bin\\catalina.bat"), command],
          creationflags=CREATE_NEW_CONSOLE)


def create_new_project(webapps_folder: str, project_name: str):
    os.chdir(webapps_folder)

    if not os.path.exists(project_name):
        os.makedirs(project_name)

    project_path = os.path.join(webapps_folder, project_name)
    os.mkdir(f"{project_path}/src")
    os.makedirs(f"{project_path}/WEB-INF/classes")

    html_data = """
    <!DOCTYPE html>
    <html>
    <body>
        <h2>Welcome to java servlet project</h2>
    </body>
    </html>
    """

    os.chdir(project_path)

    with open('index.html', 'w') as file_writer:
        file_writer.write(html_data)

    os.mkdir(f"{project_path}/images")
    print(colored(f"Project created at ${project_path}", "green"))


def open_project(webapps_folder: str, project_name: str) -> bool:
    project_location = os.path.join(webapps_folder, project_name)
    if os.path.exists(project_location):
        os.chdir(project_location)
        return True

    print(colored("Project not found!", "red"))

    should_create = input("Do you want to create it (Y/N) ? ")
    if should_create.lower() == "y":
        create_new_project(webapps_folder, project_name)
        return True

    return False


def create_new_file(webapps_folder: str, project_name: str):
    src_folder = os.path.join(webapps_folder, project_name, "src")

    filename = input("Enter filepath relative to src folder: ")
    try:
        open(os.path.join(src_folder, filename), 'x').close()
    except FileExistsError:
        print(colored(f"{filename} already exists", "red"))
    except FileNotFoundError as e:
        print(colored(str(e), "red"))
    else:
        print(colored(f"{filename} created successfully!", "green"))


def hard_link_class_file(project_folder: str, src: str, class_filename: str):
    dest = os.path.join(project_folder, fr"WEB-INF\classes\{class_filename}")
    if not os.path.exists(dest):
        os.link(src, dest)
        print(colored("Hard link created to classes folder", "yellow"))


def compile_file(tomcat_folder: str, project_name: str):
    filename = input("Enter file to compile: ")
    project_folder = fr"{tomcat_folder}\webapps\{project_name}"
    command = fr'javac --class-path ".;{tomcat_folder}\lib\servlet-api.jar" "{project_folder}\src\{filename}"'
    if os.path.exists(os.path.join(project_folder, "src", filename)):
        try:
            output = Popen(command)
            output.communicate()
            code = output.returncode
        except SubprocessError as e:
            print(colored(str(e), "red"))
        else:
            if code == 0:
                filename_without_ext, _ = os.path.splitext(filename)
                class_filename = f"{filename_without_ext}.class"
                src = os.path.join(project_folder, fr"src\{class_filename}")

                if os.path.exists(src):
                    hard_link_class_file(project_folder, src, class_filename)
                else:
                    print(colored(f"{class_filename} not found", "red"))
            else:
                print(colored(f"Error in {filename}", "red"))
    else:
        print(colored("File not found!", "red"))


def get_project_option():
    option_prompt = """

PRESS C: TO CREATE A NEW PROJECT
PRESS O: TO OPEN A PROJECT
PRESS X: TO QUIT
    """
    print(option_prompt)

    selection = input("Enter your selection: ")
    return selection


def initialize_project(webapps_folder) -> str:
    while True:
        choice = get_project_option()
        match choice.upper():
            case 'C':
                project_name = input("Enter the project name: ")
                create_new_project(webapps_folder, project_name)
                return project_name
            case 'O':
                project_name = input("Enter existing project name: ")
                if open_project(webapps_folder, project_name):
                    return project_name
            case 'X':
                exit_with_success()
            case _:
                print(colored(f"Invalid choice: {choice}", "red"))


def get_file_option():
    option_prompt = """

PRESS N: TO CREATE A NEW FILE
PRESS S: TO COMPILE JAVA FILE
PRESS R: TO RELOAD TOMCAT-SERVER
PRESS M: TO GO BACK TO MAIN MENU
PRESS X: TO QUIT
    """
    print(option_prompt)

    selection = input("Enter your selection: ")
    return selection


def handle_file_operations(tomcat_folder_path: str, webapps_folder: str, project_name: str):
    handle_server(tomcat_folder_path, "start")
    while True:
        choice = get_file_option()
        match choice.upper():
            case 'N':
                create_new_file(webapps_folder, project_name)
            case 'R':
                handle_server(tomcat_folder_path, "stop")
                handle_server(tomcat_folder_path, "start")
            case 'S':
                compile_file(tomcat_folder_path, project_name)
            case 'M':
                handle_server(tomcat_folder_path, "stop")
                return
            case 'X':
                exit_with_success()
            case _:
                print(colored(f"Invalid choice: {choice}", "red"))


def exit_with_success():
    print(colored("Thanks for using!!", "yellow"))
    sys.exit(0)


def main():
    tomcat_folder_path = os.getenv("CATALINA_HOME")
    if tomcat_folder_path is None:
        print(colored(
            "Please set CATALINA_HOME in environment variables pointing to the Apache Tomcat installation directory",
            "yellow"))
        sys.exit(1)

    webapps_folder = os.path.join(tomcat_folder_path, "webapps")
    try:
        while True:
            project_name = initialize_project(webapps_folder)
            handle_file_operations(
                tomcat_folder_path, webapps_folder, project_name)
    except KeyboardInterrupt:
        handle_server(tomcat_folder_path, "stop")


if __name__ == "__main__":
    main()
