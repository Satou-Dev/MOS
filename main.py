import struct
import socket
from icecream import ic
import json
from server import net
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import utils
import uuid
import os


def open_jsons(name):
    with open(f"data\\{name}.json", encoding="utf-8") as f:
        data = json.load(f)
        return data


def check_player(name, player_uuid):
    if player_uuid in os.listdir("data\\players"):
        with open(f"data\\players\\{player_uuid}\\data.json", encoding="utf-8") as f:
            data = json.load(f)
            return data
    else:
        os.mkdir(f"data\\players\\{player_uuid}")
        with open(f"data\\players\\{player_uuid}\\data.json", "w", encoding="utf-8") as f:
            data = {
                "uuid": player_uuid,
                "name": name
            }
            json.dump(data, f, indent=4)
            return data


def login_start(client, data):
    print("Login Start...")
    login_raw_data = client.recv(1024)
    data_len = data[0]
    packet_id = data[1]
    print(f"Data: {login_raw_data}")
    print(f"Packet ID: {packet_id}")
    print(f"Data len: {data_len}")
    nick = login_raw_data[3:-16].decode("utf-8")
    print(f"Nick: {nick}")
    """player_uuid = "{}{}{}{}-{}{}-{}{}-{}{}-{}{}{}{}{}{}".format(
        *[
            hex(byte)[2:]
            for byte
            in struct.unpack(
                "!16B",
                login_raw_data[-16:]
            )
        ]
    )"""
    player_uuid = "".join(
        [
            hex(byte)[2:]
            for byte
            in struct.unpack(
                "!16B",
                login_raw_data[-16:]
            )
        ]
    )
    print(f"Player UUID: {player_uuid}")
    player_settings = check_player(nick, player_uuid)
    print(player_settings)
    #player_int_uuid = [int(player_settings["uuid"][i:i+2], 16) for i in range(0, len(player_settings["uuid"]), 2)]
    player_int_uuid = login_raw_data[-16:]
    print(f"Player int UUID: {player_int_uuid}")



def read_handshake(socket_client):
    print("Reading handshake...")
    #data_len = int(socket_client.recv(1).hex(), 16)
    #packet_id = int(socket_client.recv(1).hex(), 16)
    #protocol_ver = net.read_varint(socket_client.recv(2))
    data = socket_client.recv(1024)
    data_len = data[0]
    packet_id = data[1]
    protocol_ver = net.read_varint(data[2:4])
    print(f"Data: {data}")
    print(f"Packet ID: {packet_id}")
    print(f"Data len: {data_len}")
    match packet_id:
        case 0:
            pass
            port_index = data.find(b"\xdd")
            next_state = data[port_index + 1]
            print(f"Protocol version: {protocol_ver}")
            print(f"Next state: {next_state}")
            if next_state == 1:
                print("Sending status response...")
                status_json_dumped = json.dumps(open_jsons("server_options"))
                socket_client.send(status_json_dumped.encode("utf-8"))
            else:
                login_start(socket_client, data)
        case 1:
            socket_client.send(data)
            print("Pong")



def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 25565))
    server.listen(1)
    print("Listening for connections...")
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        read_handshake(client_socket)


if __name__ == "__main__":
    main()
