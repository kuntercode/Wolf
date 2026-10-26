import argparse
import re

def send_wol():
    print("Sedning WOL...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("mac_address")

    args = parser.parse_args()

    if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", args.mac_address.lower()):
        print("Valid MAC Address")
        send_wol()

    else:
        print("Invalid MAC Address")
