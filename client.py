# coding: utf-8

import hashlib
import json
import sys
import tkinter as tk
import tkinter.messagebox as msg

from enigma_machine import enigma
from utils import *

DEFAULT_HOST = '127.0.0.1'  # "78.211.180.110"
DEFAULT_PORT = 12801
DEFAULT_USERNAME = "Helyosis"
DEFAULT_PASSWORD = "MDP"
COMMAND_PREFIX = "/"


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.top = tk.Toplevel()

        self.connexion_avec_serveur = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.bouton_confirmer = tk.Button(
            self.top, text="Confirmer", command=self.confirmer_setup)
        self.boites = [
            [None, None, DEFAULT_USERNAME],
            [None, None, DEFAULT_HOST],
            [None, None, DEFAULT_PORT],
            [None, None, DEFAULT_PASSWORD],
        ]
        self.title("Prik")
        self["bg"] = "black"
        self.geometry("900x600+250+100")
        self.minsize(400, 500)
        self.bind_all("<MouseWheel>", self._on_mouse_wheel)

        self.affichage = tk.Text(state=tk.DISABLED)
        self.affichage.pack(fill=tk.BOTH)

        self.saisie = tk.Entry(self, width=45)
        self.saisie.pack()
        self.saisie.bind("<Return>", self.envoi_texte)

        self.quitter = tk.Button(self, text="Quitter", command=self.end)
        self.quitter.pack()

        self.mdp_base = ""

        label_clients_connectes = tk.Label(self, text="Clients connectés:")
        label_clients_connectes.pack()

    def _on_mouse_wheel(self, event):
        self.affichage.yview_scroll(-1 * int(event.delta / 120), "units")

    def setup(self):  # Demande pseudo, ip, port

        self.top['bg'] = "black"
        self.top.geometry("200x200+0+100")

        for i in self.boites:
            i[1] = tk.StringVar(self.top, value=i[2])
            i[0] = tk.Entry(self.top, textvariable=i[1])
            i[0].pack()

        self.boites[3][0].config(show="*")

        self.bouton_confirmer.pack()

        self.top.focus_set()

    def confirmer_setup(self):

        user_pseudo, ip, user_port, self.mdp_base = self.boites[0][1].get(), self.boites[1][1].get(
        ), self.boites[2][1].get(), self.boites[3][1].get()
        self.connexion_avec_serveur.connect((ip, int(user_port)))

        print("connexion avec le QG réussite")
        nonce = self.connexion_avec_serveur.recv(1024).decode()  # /!\
        print(nonce)

        mdp = (self.mdp_base + nonce).encode()  # mot de passe + le nombre
        mdp = hashlib.sha224(mdp).hexdigest()  # sha224
        print(mdp)
        envoyer_message(self.connexion_avec_serveur, mdp)  # on evoi

        etat = self.connexion_avec_serveur.recv(1024).decode('utf-8')
        if etat == "PAS OK":
            sys.exit(0)

        size = self.connexion_avec_serveur.recv(1024).decode("utf-8")
        self.machine = enigma.Machine(int(size))

        print("Je vais bientôt recevoir la config")
        config = recv_all(self.connexion_avec_serveur)
        print(config)

        config = xor(config, self.mdp_base)
        print(config)
        config = json.loads(config)
        self.machine.set_config(config)
        self.connexion_avec_serveur.setblocking(False)
        self.connexion_avec_serveur.send(user_pseudo.encode("utf-8"))
        self.after(10, self.recevoir_message)
        self.top.destroy()

    def ping(self):
        pass

    def envoi_texte(self, event):

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
        if msg.askyesno('Terminer la session ?', 'Êtes-vous sûr de vouloir quitter ?'):
            try:
                self.connexion_avec_serveur.send("fin".encode("utf-8"))
            except:
                pass
            self.quit()
        else:
            msg.showinfo("", "Heureux de l'apprendre ^^")
            msg.showinfo("", "Ca serait dommage de nous abandonner comme ça !")

    def recevoir_message(self):
        self.after(50, self.recevoir_message)

        try:
            message = self.connexion_avec_serveur.recv(1024).decode("utf-8")
        except BlockingIOError:
            pass
        else:
            if not message:
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
                    config = json.dumps(config)
                    config = xor(config, self.mdp_base)
                    config = "4" + config
                    self.connexion_avec_serveur.send(config.encode("utf-8"))

            elif index == '2':

                self.affichage.config(state = tk.NORMAL)

                self.affichage.insert(tk.END, message[1:])
                self.affichage.insert(tk.END, '\n')

                self.affichage.config(state=tk.DISABLED)


fenetre = Application()
fenetre.protocol("WM_DELETE_WINDOW", fenetre.end)

fenetre.setup()

fenetre.mainloop()
