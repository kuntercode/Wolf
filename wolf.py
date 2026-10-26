import argparse
import sqlite3
import socket
import re

def send_wol(mac_address: str, broadcast_ip: str = "255.255.255.255", port: int = 9):
    
    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac_address.lower()):
        cleaned_mac = mac_address.replace(":", "").replace("-", "")

        mac_bytes = bytes.fromhex(cleaned_mac)

        magic_packet = b"\xff" * 6 + mac_bytes * 16

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            sock.sendto(magic_packet, (broadcast_ip, port))
            print(f"Magic packet sent")

    else:
        print("Invalid MAC Address")



def main():
    parser = argparse.ArgumentParser(description="Send a Wake-on-LAN magic packet")

    parser.add_argument("mac_address", help="Target MAC address")

    parser.add_argument("--broadcast", default="255.255.255.255", help="Broadcast IP address")
    parser.add_argument("--port", type=int, default=9)

    args = parser.parse_args()

    send_wol(args.mac_address, args.broadcast, args.port)


if __name__ == "__main__":
    main()