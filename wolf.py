import argparse
import shelve
import socket
import re

from pathlib import Path


db_name = "wolf_db"

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = str(SCRIPT_DIR / db_name)


def wake_host(args):
    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", args.ref.lower()):
        cleaned_mac = args.ref.replace(":", "").replace("-", "")

        mac_bytes = bytes.fromhex(cleaned_mac)

        magic_packet = b"\xff" * 6 + mac_bytes * 16

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            sock.sendto(magic_packet, (args.broadcast, args.port))
            print(f"Magic packet sent.")

    else:
        with shelve.open(DB_PATH, "c") as db:
            if args.ref in db:
                mac_address, broadcast, port = db[args.ref]
                print(f"{args.ref} - MAC Address: {mac_address}, Broadcast: {broadcast}, Port: {port}")

                cleaned_mac = mac_address.replace(":", "").replace("-", "")

                mac_bytes = bytes.fromhex(cleaned_mac)

                magic_packet = b"\xff" * 6 + mac_bytes * 16

                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

                    sock.sendto(magic_packet, (broadcast, port))
                    print(f"Magic packet sent.")

            else:
                print("Invalid MAC Address or alias not found.")



def add_alias(args):
    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", args.mac_address.lower()):
        with shelve.open(DB_PATH, "c") as db:
            if args.name in db:
                print(f"Alias '{args.name}' already exists, overriding.")
            else:
                print(f"Saved alias '{args.name}'.")

            db[args.name] = (args.mac_address, args.broadcast, args.port)

    else:
        print("Invalid MAC Address.")



def list_aliases(args):
    if args.name:
        with shelve.open(DB_PATH, "c") as db:
            if args.name in db:
                mac_address, broadcast, port = db[args.name]
                print(f"{args.name} - MAC Address: {mac_address}, Broadcast: {broadcast}, Port: {port}")

            else:
                print(f"Alias not found.")

    else:
        with shelve.open(DB_PATH, "c") as db:
            for key, value in db.items():
                mac_address, broadcast, port = value
                print(f"{key} - MAC Address: {mac_address}, Broadcast: {broadcast}, Port: {port}")

    print()


def remove_aliases(args):
    if args.name == "*":
        with shelve.open(DB_PATH, "c") as db:
            if not db:
                print("No saved aliases.")

            else:
                db.clear()
                print("Removed all aliases.")

    elif args.name:
        with shelve.open(DB_PATH, "c") as db:
            if args.name in db:
                del db[args.name]
                print(f"Removed alias '{args.name}'.")

            else:
                print(f"Alias not found.")



def main():
    parser = argparse.ArgumentParser(description="Send a Wake-on-LAN magic packet")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Wake host
    wake_parser = subparsers.add_parser("wake", help="Send Magic Packet to host by MAC address or alias.")
    wake_parser.add_argument("ref", help="MAC Address or alias.")
    wake_parser.add_argument("-p", "--port", type=int, default=9, help="Port.")
    wake_parser.add_argument("-b", "--broadcast", default="255.255.255.255", help="Broadcast IP address.")
    wake_parser.set_defaults(func=wake_host)

    # Add alias
    add_parser = subparsers.add_parser("add", help="Add an alias to a host.")
    add_parser.add_argument("name", help="Alias name.")
    add_parser.add_argument("mac_address", help="MAC Address.")
    add_parser.add_argument("-b", "--broadcast", default="255.255.255.255", help="Broadcast IP address.")
    add_parser.add_argument("-p", "--port", type=int, default=9, help="Port.")
    add_parser.set_defaults(func=add_alias)

    # List aliases
    list_parser = subparsers.add_parser("list", help="List all saved aliases.")
    list_parser.add_argument("-n", "--name", help="Name of the alias, or empty to list all.")
    list_parser.set_defaults(func=list_aliases)

    # Remove aliases
    remove_parser = subparsers.add_parser("remove", help="Remove an alias by name or remove all using '*'.")
    remove_parser.add_argument("name", help="Name of the alias, or '*' to remove all.")
    remove_parser.set_defaults(func=remove_aliases)

    args = parser.parse_args()
    args.func(args)



if __name__ == "__main__":
    main()

# TODO: Add IPv4 checks
