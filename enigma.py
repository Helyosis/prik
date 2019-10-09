# coding: utf-8
from random import seed, shuffle
import json

# seed("Bonjour 123")

# TODO: Faire génération aléatoire de clés


class Machine():
    def __init__(self, size=256, nbRotors=3, config=None):
        if config is not None:
            self.set_config(config)
            return

        self.size = size
        self.nbRotors = nbRotors

        self.child = Rotor(self, self, size, nbRotors)

    def send_letter(self, letter: int, rotation):
        substituted = self.child.send_letter(letter)
        if rotation: self.child.rotate()
        return substituted

    def send_message(self, phrase: str, rotation = True):
        crypted = []
        for i in phrase:
            letter = ord(i)
            crypted.append(chr(self.send_letter(letter, rotation)))
        return "".join(crypted)

    def get_config(self):
        config_child = self.child.get_config()
        config_to_send = {
            "TYPE": "MACHINE",
            "SIZE": self.size,
            "NBROTORS": self.nbRotors,
            "CONFIG_CHILD": config_child
        }
        return config_to_send

    def set_config(self, config):
        if config["TYPE"] == "MACHINE":
            self.size = config["SIZE"]
            self.nbRotors = config["NBROTORS"]
            self.child = Rotor(self, self, self.size, self.nbRotors)
            self.child.set_config(config["CONFIG_CHILD"])
        else:
            raise Exception(
                f"Config error, expected a MACHINE type but got {config['TYPE']}")


class Rotor():
    def __init__(self, parent, root, size, nbChilds):
        self.parent = parent
        self.root = root
        self.decallage = 0
        self.size = size
        self.config = list(range(size))
        shuffle(self.config)

        if nbChilds >= 1:
            self.child = Rotor(self, self.root, size, nbChilds-1)
        else:
            self.child = Reflector(self, self.root, size)

    def rotate(self):

        lettre = self.config.pop(0)
        self.config.append(lettre)

        self.decallage += 1

        if self.decallage == self.size:
            self.decallage = 0
            self.child.rotate()

    def send_letter(self, letter):
        substituted = self.config[letter]
        return self.child.send_letter(substituted)

    def reflect(self, letter):
        substituted = self.config.index(letter)
        if self.parent == self.root:
            return substituted
        else:
            return self.parent.reflect(substituted)

    def get_config(self):
        config_child = self.child.get_config()
        config_to_send = {
            "TYPE": "ROTOR",
            "SIZE": self.size,
            "CONFIG": self.config,
            "CONFIG_CHILD": config_child
        }
        return config_to_send

    def set_config(self, config):
        if config["TYPE"] == "ROTOR":
            self.config = list(config["CONFIG"])
            self.child.set_config(config["CONFIG_CHILD"])
        else:
            raise Exception(
                f"Config error, expected a ROTOR type but got {config['TYPE']}")


class Reflector():
    def __init__(self, parent, root, size):
        self.root = root
        self.parent = parent

        # self.config = list(range(size))
        # shuffle(self.config)

        self.config = list(range(size))  # TODO: Faire aléatoirement
        self.config.reverse()

    def send_letter(self, letter):
        substituted = self.config[letter]
        return self.parent.reflect(substituted)

    def rotate(self):
        pass

    def get_config(self):
        config_to_send = {
            "TYPE": "REFLECTOR",
            "CONFIG": list(self.config),
        }
        return config_to_send

    def set_config(self, config):
        if config["TYPE"] == "REFLECTOR":
            self.config.clear()
            self.config.extend(config["CONFIG"])
        else:
            raise Exception(
                f"Config error, expected a REFLECTOR type but got {config['TYPE']}")


if __name__ == '__main__':
    machine = Machine(255)
    machine2 = Machine(255)

    config = machine.get_config()

    machine.set_config(config)
    machine2.set_config(config)

    cryptee = machine.send_message("Bonjour tout le monde POISSON du 2 avril")
    print(cryptee)

    print("==================================")

    decryptee = machine2.send_message(cryptee)
    print(decryptee)

    # print(json.dumps(config, indent=4) )