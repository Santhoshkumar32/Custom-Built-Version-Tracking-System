
import os
import socket
import uuid
import json
from datetime import datetime
from pytz import timezone


IP = "127.0.0.1"
PORT = 4456
SIZE = 1024
FORMAT = "utf"
SERVER_FOLDER = "server_folder"


def main():
    print("[STARTING] Server is starting.\n")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()
    print("[LISTENING] Server is waiting for clients.")

    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.\n")

        response = conn.recv(SIZE).decode(FORMAT)
        action, received = response.split(":")

        if action == "FILE":
            """ Receiving the folder_name """
            folder_name, commit_msg = received.split("&")

            """ Generating unique folder name """
            unique_folder = str(uuid.uuid1().int)

            """ creating the folder """
            folder_path = os.path.join(
                SERVER_FOLDER, folder_name, unique_folder)

            project_path = os.path.join(SERVER_FOLDER, folder_name)

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                conn.send(f"Folder ({folder_name}) created.".encode(FORMAT))

            else:
                conn.send(
                    f"Folder ({folder_name}) already exists.".encode(FORMAT))

            if not os.path.exists(os.path.join(project_path, "data.json")):
                f = open(os.path.join(project_path, "data.json"), "w")
                f.write('{"version_data":[]}')
                f.close()

            """ Storing the version id with correseponding uuid in json file"""

            commit_id = sum(os.path.isdir(os.path.join(project_path, i))
                            for i in os.listdir(project_path))
            print(commit_id)

            current_time = datetime.now(timezone("Asia/Kolkata"))
            time = current_time.strftime("%a %b %d %H:%M:%S")
            print(current_time)

            commit_data = {}
            commit_data["id"] = commit_id
            commit_data["folder_name"] = unique_folder
            commit_data["msg"] = commit_msg
            commit_data["time"] = time+" EDT"
            print(commit_data)

            f = open(os.path.join(project_path, "data.json"), "r")
            data = json.loads(f.read())
            print("REad data ", data)
            f.close()
            data["version_data"].append(commit_data)
            print("Write data", data)

            file = open(os.path.join(project_path, "data.json"), "w")
            file.seek(0)
            json.dump(data, file, indent=4)
            file.close()

            """ Receiving files """
            while True:
                msg = conn.recv(SIZE).decode(FORMAT)
                print(msg)
                cmd, data = msg.split(":")

                if cmd == "FILENAME":
                    """ Recv the file name """
                    print(f"[CLIENT] Received the filename: {data}.")

                    file_path = os.path.join(folder_path, data)
                    file = open(file_path, "w")
                    conn.send("Filename received.".encode(FORMAT))

                elif cmd == "DATA":
                    """ Recv data from client """
                    print(f"[CLIENT] Receiving the file data.")
                    file.write(data)
                    conn.send("File data received".encode(FORMAT))

                elif cmd == "FINISH":
                    file.close()
                    print(f"[CLIENT] {data}.\n")
                    conn.send("The data is saved.".encode(FORMAT))

                elif cmd == "CLOSE":
                    # conn.close()
                    print(f"[CLIENT] {data}")
                    break

        elif action == "LOG":
            file_name = received
            file = open(os.path.join(SERVER_FOLDER,
                                     file_name, 'data.json'), "r")
            file_data = file.read()
            msg = f"{file_data}"
            conn.send(msg.encode(FORMAT))

            msg = conn.recv(SIZE).decode(FORMAT)
            print(f"[CLIENT] {msg}")
            # conn.close()
            # break

        elif action == "GET":
            r_name = received
            print(f"Received the repo name {r_name}.")

            msg = f"Received the repo name {r_name}."
            conn.send(msg.encode(FORMAT))

            v_no = conn.recv(SIZE).decode(FORMAT)
            conn.send(f"Received the version number".encode(FORMAT))
            print(f"Received the version number {v_no}")

            f = open(os.path.join(SERVER_FOLDER, r_name, "data.json"), "r")
            data = json.loads(f.read())
            folder_name = data["version_data"][int(v_no)-1]["folder_name"]
            print(folder_name)
            f.close()

            path = os.path.join(SERVER_FOLDER, r_name,
                                folder_name)
            files = sorted(os.listdir(path))
            for file_name in files:

                msg = f"FILENAME:{file_name}"
                print(f"[SERVER] Sending file name: {file_name}")
                conn.send(msg.encode(FORMAT))

                msg = conn.recv(SIZE).decode(FORMAT)
                print(f"[CLIENT] {msg}")

                file = open(os.path.join(path, file_name), "r")
                file_data = file.read()
                msg = f"DATA:{file_data}"
                conn.send(msg.encode(FORMAT))

                msg = conn.recv(SIZE).decode(FORMAT)
                print(f"[SERVER] {msg}")

                msg = f"FINISH:Complete data send"
                conn.send(msg.encode(FORMAT))

                msg = conn.recv(SIZE).decode(FORMAT)
                print(f"[SERVER] {msg}")

                file.close()
            msg = f"CLOSE:File transfer is completed"
            conn.send(msg.encode(FORMAT))


if __name__ == "__main__":
    main()
