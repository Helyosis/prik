import socket, select
import time
from threading import Thread
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.simpledialog as simple

hote = "127.0.0.1"
port = 12800
en_marche = True
prefixe = "/"


"""
class EnvoiMessage(Thread):
    #Thread chargé de l'envoi des messages au serveur
    def __init__(self, pseudo, serveur):
        Thread.__init__(self)
        self.serveur = serveur
        self.pseudo = pseudo
    def run(self):
        #Code exécuté dans le Thread
        global client_lancé
        while client_lancé:
            msg_a_envoyer = ""
            msg_a_envoyer = input("> ")
            if msg_a_envoyer != "" and msg_a_envoyer != "fin":
                msg_a_envoyer = "[]".join([pseudo, msg_a_envoyer]).encode("utf-8")
                self.serveur.send(msg_a_envoyer)
            else:
                client_lancé = False
        print("La connexion avec le serveur va se terminer")
        self.serveur.close()
"""     

def confirmerQuit():
    global fenetre, en_marche
    if msg.askyesno('Terminer la session ?', 'Êtes-vous sûr de vouloir quitter ?'):
        try:
            connexion_avec_serveur.send("{} a quitté le serveur".format(pseudo).encode("utf-8")) 
        
        fenetre.quit()
        en_marche = False
    else:
        msg.showinfo("","Heureux de l'apprendre ^^")
        msg.showinfo("","Ca serait dommage de nous abandonner comme ça !")

def envoiTexte(event):
    global prefixe, connexion_avec_serveur
    widget = event.widget
    msg_a_envoyer = widget.get()
    print(msg_a_envoyer)
    msg_a_envoyer = "[]".join([pseudo, msg_a_envoyer])
    connexion_avec_serveur.send(msg_a_envoyer.encode("utf-8"))
    widget.delete(0,'end')

fenetre = tk.Tk()
fenetre.title("Hmmm... Le caca c'est délicieux")
fenetre.configure(bg = "olive", height = 500, width = 500, cursor = "star")
fenetre.geometry("500x500")

messages = tk.Listbox(fenetre)
messages.pack(fill = "both")

saisie = tk.Entry()
saisie.pack()
saisie.bind("<Return>", envoiTexte)

quitter = tk.Button(fenetre, text = "Quitter", command = confirmerQuit)
quitter.pack()

pseudo = simple.askstring("Bonjour", fenetre, initialvalue = "Quel sera ton pseudo lors de cette session ?")
if pseudo and "[]" in pseudo:
	pseudo = "".join(pseudo.split("[]"))
	msg.askokcancel("Ton pseudo a été changé en {} car il contenait un combinaison de caractères \"interdite\"".format(pseudo))

connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((hote, port))
connexion_avec_serveur.setblocking(False)
connexion_avec_serveur.send(pseudo.encode("utf-8"))

fenetre.protocol("WM_DELETE_WINDOW", confirmerQuit)
fenetre.mainloop()

while en_marche:
            msg = connexion_avec_serveur.recv(1024).decode("utf-8)")
            print(msg)

fenetre.quit()
connexion_avec_serveur.shutdown(socket.SHUT_RDWR)