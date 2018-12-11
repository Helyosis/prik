import socket
import select

hote = '127.0.0.1'
port = 12800

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(5)
print("Le serveur est lancé sur {}".format(port))

serveur_on = True
identification = {}
clients_connectes = []
while serveur_on:
    # On attend maximum 50ms
    connexions_demandees, _, _ = select.select([connexion_principale], [], [], 0.05)
    for connexion in connexions_demandees:
        connexion_avec_client, infos_connexion = connexion.accept()
        pseudo = connexion_avec_client.recv(1024).decode("utf-8") #Recevoir le pseudo
        identification[connexion_avec_client] = pseudo
        print("{} a rejoint le serveur".format(pseudo))
        # On ajoute le socket à la liste des clients

    # Maintenant, on écoute la liste des clients connectés
    clients_a_ecrire = []
    clients_a_lire = []
    messages_a_envoyer = []
    try:
        clients_a_lire, clients_a_ecrire, _ = select.select(clients_connectes,clients_connectes, [], 0)
    except select.error:
        pass
    else:
        # On parcourt la liste des clients Ã  lire
        for client in clients_a_lire:
            # Client est de type socket
            msg_recu = client.recv(1024)
            msg_recu = msg_recu.decode()
            pseudo = identification[client]
            messages_a_envoyer.append("{} > {}".format(pseudo, msg_recu))
            print(messages_a_envoyer)
            if msg_recu == "fin" or msg_recu == "":
                client.send("La connexion se termine".encode("utf-8"))
                clients_connectes.remove(client)
                clients_a_ecrire.remove(client)
                client.shutdown(socket.SHUT_RDWR)
                client.close()

            if msg_recu == "shutdown":
                serveur_on = False
        #Envoi des messages
        for client in clients_a_ecrire:
            for message in messages_a_envoyer:
                client.send(message.encode("utf-8"))


print("Fermeture des connexions")
for client in clients_connectes:
    client.send("La connexion se termine".encode("utf-8"))
    client.shutdown(socket.SHUT_RDWR)
    client.close()

connexion_principale.close()
print("Toutes les connexions ont été fermées et le serveur s'est éteint.")