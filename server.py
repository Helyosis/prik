import hashlib
import json
import select
import time
from random import randint

from enigma_machine import enigma
from utils import *

HOST = '0.0.0.0'
PORT = 12801  # Port du serveur
SIZE_ENIGMA = 255

nonce = 0
mdp_base = "MDP"

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((HOST, PORT))
connexion_principale.listen(5)

print("Le serveur est lancé sur le port {}".format(PORT))

machine = enigma.Machine(SIZE_ENIGMA)


def ask_config(client: socket.socket):
    success = envoyer_message(client, "1CONFIG?")
    if not success:
        return False

    while True:
        local_config = client.recv(999999999).decode('utf-8')
        if local_config[0] == "4":
            return xor(local_config[1:], mdp_base)
        else:
            traiter_message(local_config, client)


def deconnexion(
        client_to_disconnect: socket.socket):  # Fonction de deconnexion, a comme argument le client à déconnecter
    global clients_a_ecrire, clients_connectes, identification, messages_a_envoyer

    messages_a_envoyer.append(
        "2[-]{} a quitté le serveur".format(
            identification[client_to_disconnect]))  # Informe tout le monde de la déconnexion

    clients_connectes.remove(client_to_disconnect)  # Supprime de la liste des clients connectés
    clients_a_ecrire.remove(client_to_disconnect)  # Idem

    envoyer_message(client_to_disconnect, "1[END]")
    client_to_disconnect.shutdown(socket.SHUT_RDWR)  # Ferme le flux de connexion
    client_to_disconnect.close()  # Idem


def ping(client_to_ping: socket.socket):  # Vérifie l'intégrité de la connexion
    global last_ping  # Liste des dates de dernier pings
    client_to_ping.settimeout(2)  # Délai max de 2 secondes
    if last_ping[client_to_ping] + 5 > time.time():  # Si le dernier ping date de moins de 5 secondes
        return True  # Quitte sur un succès
    try:
        envoyer_message(client_to_ping, "[PING]")
        print('Ping effectué avec succes sur', identification[client_to_ping])
        last_ping[client_to_ping] = time.time()
        return True
    except:
        return False


def traiter_message(msg, client):
    global identification, messages_a_envoyer, serveur_on, machine
    index = msg[0]
    if index == '0':
        print("Message décrypté reçu :", machine.send_message(msg[1:]))
        pseudo = identification[client]
        messages_a_envoyer.append("0{} > {}".format(pseudo, msg[1:]))

        if msg == "fin":
            deconnexion(client)

        if msg == "shutdown":
            serveur_on = False


serveur_on = True
identification = {}
last_ping = {}
clients_connectes = []

while serveur_on:
    # On attend maximum 50ms
    connexions_demandees, _, _ = select.select([connexion_principale], [], [], 0.05)
    messages_a_envoyer = []

    for connexion in connexions_demandees:
        connexion_avec_client, infos_connexion = connexion.accept()

        print("Quelqu'un essaie de se connecter")
        nonce = str(int(nonce) + randint(0, 100))  # nouveaux nonce
        connexion_avec_client.send(nonce.encode())

        print(nonce)

        mdp_serveur = (mdp_base + str(nonce)).encode()  # ce que l'on attend
        mdp_serveur = str(hashlib.sha224(mdp_serveur).hexdigest())  # hash
        print(mdp_serveur)
        # on vérifie
        mdp_client = str(connexion_avec_client.recv(1024).decode())
        print(mdp_client)

        if mdp_client != mdp_serveur:
            connexion_avec_client.send("PAS OK".encode("utf-8"))
            connexion_avec_client.shutdown(socket.SHUT_RDWR)  # Ferme le flux de connexion
            connexion_avec_client.close()  # Idem
            print("Intru détecté /!\\")

        else:
            envoyer_message(connexion_avec_client, 'OK')

            config = json.dumps(machine.get_config(), indent=None)

            envoyer_message(connexion_avec_client, SIZE_ENIGMA)

            config = xor(config, mdp_base)

            envoyer_message(connexion_avec_client, config)

            pseudo = connexion_avec_client.recv(1024).decode("utf-8")  # Recevoir le pseudo
            print("Bienvenu Mr", pseudo)

            identification[connexion_avec_client] = pseudo
            messages_a_envoyer.append("2[+]{} a rejoint le serveur".format(pseudo))
            clients_connectes.append(connexion_avec_client)
            last_ping[connexion_avec_client] = time.time()

    for client in clients_connectes:
        if not (ping(client)):
            deconnexion(client)
    # Maintenant, on écoute la liste des clients connectés
    clients_a_ecrire = []
    clients_a_lire = []
    try:
        clients_a_lire, clients_a_ecrire, _ = select.select(clients_connectes, clients_connectes, [], 0.05)
    except select.error:
        pass
    else:
        # On parcourt la liste des clients Ã  lire
        for client in clients_a_lire:
            # Client est de type socket
            try:
                msg_recu = client.recv(1024)

            except ConnectionResetError:
                deconnexion(client)
                continue

            msg_recu = msg_recu.decode()
            # machine.send_message(msg_recu)
            print("Un message a été reçu :", msg_recu)

            traiter_message(msg_recu, client)

        # Envoi des messages
        for client in clients_a_ecrire:
            for message in messages_a_envoyer:
                msg = message
                print("Envoi de :", msg)

                envoyer_message(client, msg)

print("Fermeture des connexions")
for client in clients_connectes:
    envoyer_message(client, "La connexion se termine")
    client.shutdown(socket.SHUT_RDWR)
    client.close()

connexion_principale.close()
print("Toutes les connexions ont été fermées et le serveur s'est éteint.")
