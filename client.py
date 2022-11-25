import os
import socket
import argparse
import version

SIZE = 1024
FORMAT = "utf"
CLIENT_FOLDER = "client_folder"


def commit_project(client, path, folder_name, commit_msg):
    """ Sending the folder name and commit msg """
    msg = f"FILE:{folder_name}&{commit_msg}"
    print(f"[CLIENT] Sending folder name: {folder_name}")
    print(f"[CLIENT] Sending commit msg: {commit_msg}")
    client.send(msg.encode(FORMAT))

    """ Receiving the reply from the server """
    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}\n")

    """ Sending files """
    files = sorted(os.listdir(path))

    for file_name in files:
        """ Send the file name """
        if file_name != "data.json":
            msg = f"FILENAME:{file_name}"
            print(f"[CLIENT] Sending file name: {file_name}")
            client.send(msg.encode(FORMAT))

            """ Recv the reply from the server """
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")

            """ Send the data """
            file = open(os.path.join(path, file_name), "r")
            file_data = file.read()

            msg = f"DATA:{file_data}"
            client.send(msg.encode(FORMAT))

            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")

            """ Sending the close command """
            msg = f"FINISH:Complete data send"
            client.send(msg.encode(FORMAT))
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")

    """ Closing the connection from the server """
    msg = f"CLOSE:File transfer is completed"
    client.send(msg.encode(FORMAT))


def push(prj_name, commit_msg, IP, PORT):
    """ Starting a tcp socket """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

    """ Folder path """
    path = os.path.join(CLIENT_FOLDER, prj_name)
    folder_name = path.split("\\")[-1]

    commit_project(client, path, folder_name, commit_msg)

    client.close()


if __name__ == "__main__":

    import argparse
    import version

    parser = argparse.ArgumentParser(description="Simple VCS")
    parser.add_argument("cmds", nargs="*")
    args = parser.parse_args()

    if args.cmds[0] == "push":
        repo_name = args.cmds[1]
        msg = args.cmds[2]
        ip = args.cmds[3]
        port = args.cmds[4]
        push(repo_name, msg, ip, int(port))

    elif args.cmds[0] == "create":
        repo_name = args.cmds[1]
        if os.path.exists(os.path.join(CLIENT_FOLDER, repo_name)):
            print(f"[CLIENT] Repository name already exist.")
        else:
            os.makedirs(os.path.join(CLIENT_FOLDER, repo_name))

    elif args.cmds[0] == "history":
        repo_name = args.cmds[1]
        version.display_log(repo_name)

    elif args.cmds[0] == "pull":
        repo_name = args.cmds[1]
        version_no = args.cmds[2]
        version.get_version(repo_name, version_no)
