# coding: utf-8
# seed("Bonjour 123")

from enigma_machine.machine import Machine


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
