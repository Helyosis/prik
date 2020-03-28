# coding: utf-8

import hashlib
import json
import socket
import sys
import tkinter as tk
import tkinter.messagebox as msg
from math import ceil

from enigma_machine import enigma

hote = '127.0.0.1'  # "78.211.180.110"
port = 12801
prefixe = "/"
mdp = "MDP"


class Application(tk.Tk):
    def __init__(self):
        super().__init__() 

        self.title("Prik")
        self["bg"] = "black"
        self.geometry("900x600+250+100")
        self.minsize(400, 500)
        #self.minsize("200x400")
        #self.Button(fenetre, text ="pirate", relief=tk.RAISED, cursor="pirate").pack()
        self.bind_all("<MouseWheel>", self._on_mouse_wheel)

        #self.affichage = tk.Label(self, textvariable = self.messages, anchor = "w", justify = "left")

        self.affichage = tk.Text(state=tk.DISABLED)
        self.affichage.pack(fill=tk.BOTH)

        self.quitter = tk.Button(self, text="Quitter", command=self.end)
        self.quitter.pack()

        self.mdp_base = ""

        label_clients_connectés = tk.Label(self, text="Clients connectés:")
        label_clients_connectés.pack()

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
            [None, None, hote],
            [None, None, port],
            [None, None, mdp],
        ]

        for i in self.boites:
            i[1] = tk.StringVar(self.top, value=i[2])
            i[0] = tk.Entry(self.top, textvariable=i[1])
            i[0].pack()

        self.bouton_confirmer = tk.Button(
            self.top, text="Confirmer", command=self.confirmer_setup)
        self.bouton_confirmer.pack()

        self.top.focus_set()

    def confirmer_setup(self):
        ip, port, self.mdp_base = self.boites[0][1].get(), self.boites[1][1].get(), self.boites[2][1].get()
        self.connexion_avec_serveur = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.connexion_avec_serveur.connect(
            ( ip, int(port) ))

        print("connexion avec le QG réussie")
        nonce = self.connexion_avec_serveur.recv(1024).decode()  # /!\
        print(nonce)

        mdp = (self.mdp_base + nonce).encode()  # mot de passe + le nombre
        mdp = hashlib.sha224(mdp).hexdigest()  # sha224
        print(mdp)
        self.connexion_avec_serveur.send(mdp.encode("utf-8"))  # on evoi

        etat = self.connexion_avec_serveur.recv(1024).decode('utf-8')
        if etat != "OK":
            sys.exit(0)

        size = self.connexion_avec_serveur.recv(1024).decode("utf-8")
        self.machine = enigma.Machine(int(size))

        print("Je vais recevoir la config")

        config = chunk = ""
        while not "\x00" in chunk:
            chunk = self.connexion_avec_serveur.recv(99999999).decode('utf-8')
            config += chunk

        print(config.encode())

        config = config.strip('\x00')

        config = self.xor(config, self.mdp_base)
        config = json.loads( config )
        self.machine.set_config(config)

      

        self.connexion_avec_serveur.setblocking(False)
        self.connexion_avec_serveur.send("*Invisible*".encode("utf-8"))
        self.after(10, self.recevoirMsg)
        self.top.destroy()
        #self.after(10, fenetre.recevoirMsg)

    def ping(self):
        pass
        #print("PING reçu")
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
                self.affichage.insert(tk.END, pseudo + " > " + vrai_message) # Don't want to decrypt the message
                self.affichage.insert(tk.END, '\n')

                self.affichage.config(state=tk.DISABLED)

            elif index == '1': # Commande

                if message[1:] == "CONFIG?":
                    config = self.machine.get_config()
                    config = json.dumps( config )
                    config = self.xor(config, self.mdp_base)
                    config = "4" + config
                    self.connexion_avec_serveur.send( config.encode("utf-8") )

            elif index == '2': # Message automatique (déconnection, etc), aucun cryptage pour les messages autos donc traitement différent

                self.affichage.config(state = tk.NORMAL)

                self.affichage.insert(tk.END, message[1:])
                self.affichage.insert(tk.END, '\n')

                self.affichage.config(state=tk.DISABLED)


fenetre = Application()
fenetre.protocol("WM_DELETE_WINDOW", fenetre.end)

fenetre.setup()

fenetre.mainloop()
