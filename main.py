import os
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


if __name__ == "__main__":
    tomcat_folder_path = os.getenv("CATALINA_HOME")
    project_name = input("Enter project name: ")
    create_new_project(tomcat_folder_path, project_name)
    webapps_folder = os.path.join(tomcat_folder_path, "webapps")
    create_new_file(webapps_folder, project_name)
