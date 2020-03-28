from random import shuffle

from enigma_machine.reflector import Reflector


class Rotor:
    def __init__(self, parent, root, size, nbChilds):
        self.parent = parent
        self.root = root
        self.decallage = 0
        self.size = size
        self.config = list(range(size))
        shuffle(self.config)

        if nbChilds >= 1:
            self.child = Rotor(self, self.root, size, nbChilds - 1)
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
