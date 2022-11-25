import json
import socket
import os

IP = "172.22.11.34"
PORT = 4456
SIZE = 1024
FORMAT = "utf"
CLIENT_FOLDER = "client_folder"
user_name = os.environ.get('USERNAME')


def display_log(file_name):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    msg = f"LOG:{file_name}"
    folder_path = os.path.join(CLIENT_FOLDER, file_name, "data.json")
    print(f"[CLIENT] Requesting the log : {file_name}")
    client.send(msg.encode(FORMAT))

    msg = client.recv(SIZE).decode(FORMAT)
    file = open(folder_path, "w+")
    file.write(msg)
    file.close()

    msg = f"Data received Successfully"
    client.send(msg.encode(FORMAT))

    f = open(folder_path, "r+")
    data = json.loads(f.read())

    for x in data["version_data"]:
        print(" version : ", x["id"])
        print(" user    : ", user_name.split()[0])
        print(" message : ", x["msg"])
        print(" time    : ", x["time"])
        print()

    f.close()
    client.close()


def get_version(rname, vno):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    msg = f"GET:{rname}"
    print(f"[CLIENT] Sending the repo name : {rname}")
    client.send(msg.encode(FORMAT))

    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]{msg}")

    msg = f"{vno}"
    print(f"[CLIENT] Sending the version number : {vno}")
    client.send(msg.encode(FORMAT))

    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER] {msg}")

    while True:
        msg = client.recv(SIZE).decode(FORMAT)
        print(msg)
        cmd, data = msg.split(":")

        if cmd == "FILENAME":
            file = open(os.path.join(CLIENT_FOLDER, rname, data), "w")
            client.send("Filename received.".encode(FORMAT))

        elif cmd == "DATA":
            """ Recv data from client """
            print(f"[CLIENT] Receiving the file data.")

            file.write(data)
            client.send("File data received".encode(FORMAT))

        elif cmd == "FINISH":

            file.close()
            print(f"[CLIENT] {data}.\n")
            client.send("The data is saved.".encode(FORMAT))

        elif cmd == "CLOSE":
            # client.close()
            print(f"[CLIENT] {data}")
            break

    client.close()
