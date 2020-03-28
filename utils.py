import socket
from math import ceil


def xor(message1: str, message2: str):  # message2 = clé
    crypted = []
    if len(message1) > len(message2):
        nbRepeat = ceil(len(message1) / len(message2))
        key = message2 * nbRepeat
    else:
        key = message2

    for index, lettre in enumerate(message1):
        ord1 = ord(lettre)
        ord2 = ord(key[index])
        crypted.append(chr(ord1 ^ ord2))
    return "".join(crypted)


def envoyer_message(client: socket.socket, message):
    try:
        client.send(str(message).encode('utf-8'))
        client.send(b'\x00')
    except Exception as e:
        print(e)
        return False
    return True


def recv_all(client: socket.socket):
    total = ""
    chunk = ""
    while chunk != '\x00':
        chunk = client.recv(1).decode('utf-8')  #  >:(
        total += chunk
    return total
