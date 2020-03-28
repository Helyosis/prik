class Reflector:
    def __init__(self, parent, root, size):
        self.root = root
        self.parent = parent

        # self.config = list(range(size))
        # shuffle(self.config)

        self.config = list(range(size))  # TODO: Faire aléatoirement (mélange par pair (index et valeur interchangeable)
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
