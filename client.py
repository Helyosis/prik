# coding: utf-8

import enigma
import socket
import select
import time
from threading import Thread
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.simpledialog as simple
import hashlib
import pickle, json
from math import ceil
import sys


hote = '78.211.180.110'  # "78.211.180.110"
port = 12800
prefixe = "/"
pseudo = "Helyosis"
mdp = "MDP"


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Prik")
        self["bg"] = "black"
        self.geometry("900x600+250+100")
        self.minsize(400, 500)
        self.bind_all("<MouseWheel>", self._on_mouse_wheel)

        #self.affichage = tk.Label(self, textvariable = self.messages, anchor = "w", justify = "left")

        self.affichage = tk.Text(state=tk.DISABLED)
        self.affichage.pack(fill=tk.BOTH)

        self.saisie = tk.Entry(self, width =45)
        self.saisie.pack()
        self.saisie.bind("<Return>", self.envoiTexte)

        self.quitter = tk.Button(self, text="Quitter", command=self.end)
        self.quitter.pack()

        self.mdp_base = ""
        
        self.STRING_clients_connectés = tk.StringVar()
        self.label_clients_connectés = tk.Label(self, textvariable=self.STRING_clients_connectés)
        self.label_clients_connectés.pack()

        self.bouton_clients_connectés = tk.Button(text="Rafraichir", command=self.afficher_clients_connectés)
        self.bouton_clients_connectés.pack()
        

    def afficher_clients_connectés(self):
        self.connexion_avec_serveur.send("1list_clients".encode("utf-8"))

    
        

    def _on_mouse_wheel(self, event):
        self.affichage.yview_scroll(-1 * int(event.delta / 120), "units")
    
    def xor(self, message1:str, message2:str): # message2 = clé poisson
        crypted = []
        #poisson

        if len(message1) > len(message2):
            nbRepeat = ceil( len(message1) / len(message2) )
            key = message2 * nbRepeat
        else:
            key = message2


        for i, j in enumerate(message1):
            ord1 = ord(j)
            ord2 = ord(key[i])
            crypted.append( chr(ord1 ^ ord2) )
        return "".join(crypted)

    def setup(self):  # Demande pseudo, ip, port

        self.top = tk.Toplevel()
        self.top['bg'] = "black"
        self.top.geometry("200x200+0+100")

        self.boites = [
            [None, None, pseudo],
            [None, None, hote],
            [None, None, port],
            [None, None, mdp],
        ]

        for i in self.boites:
            i[1] = tk.StringVar(self.top, value=i[2])
            i[0] = tk.Entry(self.top, textvariable=i[1])
            i[0].pack()

        self.boites[3][0].config(show = "*")

        self.bouton_confirmer = tk.Button(
            self.top, text="Confirmer", command=self.confirmer_setup)
        self.bouton_confirmer.pack()

        self.top.focus_set()

    def confirmer_setup(self):
        pseudo, ip, port, self.mdp_base = self.boites[0][1].get(), self.boites[1][1].get(
        ), self.boites[2][1].get(), self.boites[3][1].get()
        self.connexion_avec_serveur = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.connexion_avec_serveur.connect((ip, int(port)))

        print("connexion avec le QG réussite")
        nonce = self.connexion_avec_serveur.recv(1024).decode()  # /!\
        print(nonce)

        mdp = (self.mdp_base + nonce).encode()  # mot de passe + le nombre
        mdp = hashlib.sha224(mdp).hexdigest()  # sha224
        print(mdp)
        self.connexion_avec_serveur.send(mdp.encode("utf-8"))  # on evoi

        etat = self.connexion_avec_serveur.recv(1024).decode('utf-8')
        if etat == "PAS OK":
            sys.exit(0)

        size = self.connexion_avec_serveur.recv(1024).decode("utf-8")
        self.machine = enigma.Machine( int(size) )

        print("Je vais bientôt recevoir la config")

        config =  self.connexion_avec_serveur.recv(9999999).decode('utf-8')
        print(config)
        config = self.xor(config, self.mdp_base)
        
        config = json.loads( config )
        self.machine.set_config(config)



        self.connexion_avec_serveur.setblocking(False)
        self.connexion_avec_serveur.send(pseudo.encode("utf-8"))
        self.after(10, self.recevoirMsg)
        self.top.destroy()
        #self.after(10, fenetre.recevoirMsg)
        time.sleep(0.5)
        self.afficher_clients_connectés()

    def ping(self):
        pass
        #print("PING reçu")

    def envoiTexte(self, event):

        widget = event.widget
        msg_a_envoyer = widget.get()

        if msg_a_envoyer == "fin":
            self.confirmerQuit()

        else:

            config = self.machine.get_config()

            machine_temp = enigma.Machine()
            machine_temp.set_config( config )

            msg_crypté = machine_temp.send_message( msg_a_envoyer )
            # self.machine.send_message( msg_a_envoyer )


            msg_a_envoyer = '0' + msg_crypté
            print("Envoi de", msg_a_envoyer)
            self.connexion_avec_serveur.send(msg_a_envoyer.encode("utf-8"))

           # self.machine.set_config( dict(machine_temp.get_config()) )
            

        widget.delete(0, 'end')

    def end(self):
        # msg.askyesno('Terminer la session ?', 'Êtes-vous sûr de vouloir quitter ?'):
        if True:
            try:
                self.connexion_avec_serveur.send("fin".encode("utf-8"))
            except:
                pass
            self.quit()
        else:
            msg.showinfo("", "Heureux de l'apprendre ^^")
            msg.showinfo("", "Ca serait dommage de nous abandonner comme ça !")

    def recevoirMsg(self):
        self.after(50, self.recevoirMsg)
        try:
            message = self.connexion_avec_serveur.recv(1024).decode("utf-8")
        except BlockingIOError:
            pass
        else:
            if not(message):
                return

            print('Reçu', message)
            index = str(message[0])

            if index == '0':  # Message normal

                self.affichage.config(state = tk.NORMAL)
                vrai_message = "".join( message.split(" > ")[1:] )
                pseudo = message.split(" > ")[0][1:]
                message_decrypt = self.machine.send_message( vrai_message )
                self.affichage.insert(tk.END, pseudo + " > " + message_decrypt)
                self.affichage.insert(tk.END, '\n')

                self.affichage.config(state=tk.DISABLED)

            elif index == '1':

                if message[1:] == "CONFIG?":
                    config = self.machine.get_config()
                    config = json.dumps( config )
                    config = self.xor(config, self.mdp_base)
                    config = "4" + config
                    self.connexion_avec_serveur.send( config.encode("utf-8") )

            elif index == '2':

                self.affichage.config(state = tk.NORMAL)

                self.affichage.insert(tk.END, message[1:])
                self.affichage.insert(tk.END, '\n')

                self.affichage.config(state=tk.DISABLED)
            elif index == '3':
                liste_clients = message[1:]
                liste_clients = liste_clients.split("&&")
                self.STRING_clients_connectés.set("Liste clients connectés :\n" + "\n".join(liste_clients))
        
                


fenetre = Application()
fenetre.protocol("WM_DELETE_WINDOW", fenetre.end)

fenetre.setup()

fenetre.mainloop()
