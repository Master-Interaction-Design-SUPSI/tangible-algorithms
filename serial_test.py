from concurrent.futures import ThreadPoolExecutor
from supabase import create_client, Client
import serial.tools.list_ports
import serial
import os
import asyncio
import time

time.sleep(5)  # Wait for the system to initialize
url: str = "https://dbfrqzavcmyvlavddqny.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRiZnJxemF2Y215dmxhdmRkcW55Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDk3MjEwMTcsImV4cCI6MjAyNTI5NzAxN30._JaMrMxwnZMgkkwsRJn8syjdBHyasHWGCkp0WgQL-14"


# Environment Variables for Sensitive Information
# url = os.getenv("SUPABASE_URL")
# key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

table_name = "button"

# Serial Connection Setup
ser = None
is_connected = False


def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    print("Connected serial ports:")
    for port in ports:
        print(f" - {port.device}: {port.description}")
        if port.manufacturer:
            print(f"   Manufacturer: {port.manufacturer}")
        if port.serial_number:
            print(f"   Serial Number: {port.serial_number}")


async def connect_to_serial(port_name="/dev/cu.usbserial-1130", baud_rate=115200):
    global ser, is_connected
    try:
        ser = serial.Serial(port_name, baud_rate, timeout=0)
        is_connected = True
        print(f"Successfully connected to {port_name} at {baud_rate} baud.")
    except serial.SerialException as e:
        is_connected = False
        print(f"Error connecting to serial port: {e}")


async def poll_for_changes():
    global is_connected
    while is_connected:
        # This assumes implementation of async Supabase client operations
        data = await fetch_changes()
        if data:
            await process_changes(data)
        await asyncio.sleep(2)  # Adjust polling rate as needed


async def fetch_changes():
    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor() as pool:
        response = await loop.run_in_executor(
            pool,
            lambda: supabase.table(table_name).select("*").execute()
        )

    data = {}
    if response.data:
        for record in response.data:
            data[record["variable"]] = record["state"]
    return data

last_image_index = None  # Define this globally if not already defined


async def determine_commands(state_safe_or_not, state_start_button):
    # Commands are sent only if the start button is pressed (state_start_button != 0)
    if state_start_button != 0:
        if state_safe_or_not == 0:  # The image is considered safe
            commands = [
                'G10P0L20X0Y0Z0\n',
                'M3S0\n',
                'G90X-65Y220\n',
                'G90X-65Y200\n',
                'G4P0.5\n',
                'G90X-65Y170\n',
                'G4P0.5\n',
                'G90X0Y150\n',
                'G4P0.5\n',
                'G90X30Y180\n',
                'G90X0Y100\n',
                'G4P0.5\n',
                'G90X40Y85\n',
                'G90X-65Y220\n',
                'G90X-65Y180\n',
                'G4P0.5\n',
                'G90X0Y0\n',
                'G4P1\n',
                'G90X65Y163\n',
                'G4P0.7\n',
                'M3S1000\n',
                'G4P0.1\n',
                'M3S0\n',
                'G4P0.5\n',
                'G90X0Y0\n'
            ]
            print("The image is Safe.")
        elif state_safe_or_not == 1:  # The image is considered not safe
            commands = [
                'G10P0L20X0Y0Z0\n',
                'M3S0\n',
                'G90X-65Y220\n',
                'G90X-65Y170\n',
                'G4P0.5\n',
                'G90X0Y150\n',
                'G4P0.5\n',
                'G90X30Y180\n',
                'G90X0Y100\n',
                'G4P0.5\n',
                'G90X40Y85\n',
                'G90X-65Y220\n',
                'G90X-65Y180\n',
                'G4P0.5\n',
                'G90X0Y0\n',
                'G4P1\n',
                'G90X-65Y163\n',
                'G4P0.7\n',
                'M3S1000\n',
                'G4P0.1\n',
                'M3S0\n',
                'G4P0.5\n',
                'G90X0Y0\n'
            ]
            print("The image is not Safe.")
        else:
            commands = []
            print("No action required.")
        return commands
    else:
        print("Start button not pressed.")
        return []


async def process_changes(data):
    global last_image_index
    state_image_index = data.get("image_index")
    val_safe_or_not = data.get("safe_or_not")
    val_start_button = data.get("start")

    # Check if image index has changed and start button is pressed
    if state_image_index is not None and state_image_index != last_image_index and val_start_button:
        last_image_index = state_image_index  # Update the last image index
        commands = await determine_commands(val_safe_or_not, val_start_button)
        for command in commands:
            send_to_serial(command)
            await asyncio.sleep(1)  # Delay between commands for stability


def send_to_serial(data):
    global ser
    if is_connected and ser:
        try:
            ser.write(data.encode())
            print(f"Sent: {data}")
        except serial.SerialException as e:
            print(f"Error sending data: {e}")
            try:
                print("Attempting to reinitialize serial connection...")
                ser.close()
                ser.open()  # Assuming ser is already configured with the correct settings
                ser.write(data.encode())  # Attempt to send again
                print(f"Sent: {data}")
            except serial.SerialException as e:
                print(f"Failed to reinitialize serial connection: {e}")
    else:
        print("Serial connection not established or closed.")


async def main():
    list_serial_ports()
    await connect_to_serial()  # Add your default serial port and baud rate if necessary
    if is_connected:
        await poll_for_changes()
    if ser:
        ser.close()

if __name__ == "__main__":
    asyncio.run(main())
