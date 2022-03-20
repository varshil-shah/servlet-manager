import os
import shutil
import sys
from subprocess import SubprocessError

from colorama import init
from termcolor import colored

from server import *


def copy_template_file(src: str, dest: str, running_in_bundle: bool):
    if running_in_bundle:
        src = os.path.join(sys._MEIPASS, src)

    shutil.copyfile(src, dest)


def hard_link_class_file(project_folder: str, src: str, class_filename: str):
    os.makedirs(os.path.join(project_folder, "WEB-INF", "classes", os.path.dirname(class_filename)))
    dest = os.path.join(project_folder, "WEB-INF", "classes", os.path.dirname(class_filename),
                        os.path.basename(class_filename))
    if not os.path.exists(dest):
        os.link(src, dest)
        print(colored("Hard link created to classes folder", "yellow"))


def create_new_project(tomcat_folder: str, webapps_folder: str, project_name: str) -> bool:
    current_dir = os.getcwd()
    print(f'CURRENT DIR: {current_dir}')
    os.chdir(webapps_folder)

    if os.path.exists(project_name):
        print(colored(f"{project_name} already exists", "red"))
        input("Press Enter to exit")
        return False

    os.makedirs(project_name)

    project_path = os.path.join(webapps_folder, project_name)
    os.chdir(project_path)

    os.mkdir("src")
    os.makedirs("WEB-INF/classes")
    os.mkdir("images")

    running_in_bundle = getattr(sys, 'frozen', False)
    if not running_in_bundle:
        os.chdir(current_dir)

    copy_template_file("templates/index.html", os.path.join(project_path, "index.html"), running_in_bundle)
    copy_template_file("templates/Main.java", os.path.join(project_path, "src/Main.java"), running_in_bundle)
    copy_template_file("templates/web.xml", os.path.join(project_path, "WEB-INF/web.xml"), running_in_bundle)

    compile_file(tomcat_folder, project_name, "Main.java")

    print(colored(f"Project created at {project_path}", "green"))
    return True


def open_project(tomcat_folder: str, webapps_folder: str, project_name: str) -> bool:
    project_location = os.path.join(webapps_folder, project_name)
    if os.path.exists(project_location):
        os.chdir(project_location)
        return True

    print(colored("Project not found!", "red"))

    should_create = input("Do you want to create it (Y/N) ? ")
    if should_create.lower() == "y":
        return create_new_project(tomcat_folder, webapps_folder, project_name)

    return False


def create_new_file(webapps_folder: str, project_name: str):
    src_folder = os.path.join(webapps_folder, project_name, "src")
    current_dir = os.getcwd()

    filename = input("Enter filepath relative to src folder: ")
    try:
        os.chdir(src_folder)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        open(filename, "x").close()
    except FileExistsError:
        print(colored(f"{filename} already exists", "red"))
    except FileNotFoundError as e:
        print(colored(str(e), "red"))
    else:
        print(colored(f"{filename} created successfully!", "green"))
    os.chdir(current_dir)


def compile_file(tomcat_folder: str, project_name: str, filename: str):
    project_folder = fr"{tomcat_folder}\webapps\{project_name}"
    command = fr'javac --class-path ".;{tomcat_folder}\lib\servlet-api.jar" "{project_folder}\src\{filename}"'

    if not os.path.exists(os.path.join(project_folder, "src", os.path.dirname(filename), os.path.basename(filename))):
        print(colored("File not found!", "red"))
        return

    try:
        output = Popen(command)
        output.communicate()
        code = output.returncode
    except SubprocessError as e:
        print(colored(str(e), "red"))
    else:
        if code != 0:
            print(colored(f"Error in {filename}", "red"))
            return

        filename_without_ext, _ = os.path.splitext(filename)
        print(f"File name without extension: {filename_without_ext}")
        classfile_name = f"{filename_without_ext}.class"
        src = os.path.join(project_folder, "src", classfile_name)
        print(f"SRC: {src}")
        print(f"CURRENT DIR: {os.getcwd()}")
        hard_link_class_file(project_folder, src, classfile_name)


def get_project_option():
    option_prompt = """

PRESS C: TO CREATE A NEW PROJECT
PRESS O: TO OPEN A PROJECT
PRESS X: TO QUIT
    """
    print(option_prompt)

    selection = input("Enter your selection: ")
    return selection


def get_project(tomcat_folder: str, webapps_folder: str) -> str:
    while True:
        choice = get_project_option()
        match choice.upper():
            case 'C':
                project_name = input("Enter the project name: ")
                if create_new_project(tomcat_folder, webapps_folder, project_name):
                    return project_name
            case 'O':
                project_name = input("Enter existing project name: ")
                if open_project(tomcat_folder, webapps_folder, project_name):
                    return project_name
            case 'X':
                exit_with_success()
            case _:
                print(colored(f"Invalid choice: {choice}", "red"))


def get_file_option(project_name: str):
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
    start_server(tomcat_folder_path)
    while True:
        choice = get_file_option(project_name)
        match choice.upper():
            case 'N':
                create_new_file(webapps_folder, project_name)
            case 'R':
                restart_server(tomcat_folder_path)
            case 'S':
                filename = input("Enter file to compile: ")
                compile_file(tomcat_folder_path, project_name, filename)
            case 'M':
                stop_server(tomcat_folder_path)
                return
            case 'X':
                exit_with_success()
            case _:
                print(colored(f"Invalid choice: {choice}", "red"))


def exit_with_success():
    print(colored("Thanks for using servlet manager!!",
                  "blue", attrs=["bold"]))
    sys.exit(0)


def main():
    tomcat_folder = os.getenv("CATALINA_HOME")
    if tomcat_folder is None:
        print(colored(
            "Please set CATALINA_HOME environment variable pointing to the Apache Tomcat installation directory",
            "yellow"))
        input("Press Enter to exit")
        sys.exit(1)

    webapps_folder = os.path.join(tomcat_folder, "webapps")
    try:
        while True:
            project_name = get_project(tomcat_folder, webapps_folder)
            print(colored(f"Project running on url: http://localhost:8080/{project_name}", "yellow"))
            handle_file_operations(
                tomcat_folder, webapps_folder, project_name)
    except KeyboardInterrupt:
        stop_server(tomcat_folder)


if __name__ == "__main__":
    init()
    main()
