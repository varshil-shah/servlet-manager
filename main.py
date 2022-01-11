import os
import sys
from subprocess import Popen, CREATE_NEW_CONSOLE, SubprocessError
from termcolor import colored


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


def hard_link_class_file(project_folder: str, src: str, class_filename: str):
    dest = os.path.join(project_folder, fr"WEB-INF\classes\{class_filename}")
    if not os.path.exists(dest):
        os.link(src, dest)
        print(colored("Hard link created to classes folder", "yellow"))


if __name__ == "__main__":
    tomcat_folder_path = os.getenv("CATALINA_HOME")
    project_name = input("Enter project name: ")
    create_new_project(tomcat_folder_path, project_name)
    webapps_folder = os.path.join(tomcat_folder_path, "webapps")
    create_new_file(webapps_folder, project_name)
