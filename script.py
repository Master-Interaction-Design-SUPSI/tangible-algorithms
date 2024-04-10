import serial
import sys

# Configura la porta seriale qui
# o il tuo dispositivo specifico su Linux/Mac, es. '/dev/ttyUSB0'
SERIAL_PORT = '/dev/cu.usbserial-1130'
BAUD_RATE = 115200


def send_gcode(command):
    print(f"Invio G-code: {command}")
    # with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
    #     ser.write(f"{command}\n".encode())


def handle_action(action, value, state):
    if action == "updateState" and value == "stateImageProperties":
        if state == "safe":
            # Inserisci qui i comandi G-code per l'immagine "safe"
            safe_commands = [
                'G0 X10 Y10',
                'G1 X20 Y20',
                # Aggiungi altri comandi necessari
            ]
            for command in safe_commands:
                send_gcode(command)
            print("Comandi G-code inviati per l'immagine safe.")
        elif state == "not_safe":
            # Inserisci qui i comandi G-code per l'immagine "not_safe"
            not_safe_commands = [
                'G0 X30 Y30',
                'G1 X40 Y40',
                # Aggiungi altri comandi necessari
            ]
            for command in not_safe_commands:
                send_gcode(command)
            print("Comandi G-code inviati per l'immagine not safe.")
    else:
        print("Azione non gestita o stato non corrispondente.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("PYTHON: Uso corretto: script.py [azione] [valore] [stato]")
        sys.exit(1)

    action = sys.argv[1]
    value = sys.argv[2]
    state = sys.argv[3]

    handle_action(action, value, state)
