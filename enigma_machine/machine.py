from enigma_machine.rotor import Rotor


class Machine:
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

    def send_message(self, phrase: str, rotation=True):
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
