#paste and run this script ONLY on the pi

import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import requests
import time
import os

# Public URL of the Mac running face_server.py (I used an ngrok tunnel to reach it from the Pi)
SERVER = os.environ.get("NFCLEND_SERVER", "https://your-tunnel.ngrok-free.dev")
HEADERS = {"ngrok-skip-browser-warning": "true"}

i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
ic, ver, rev, support = pn532.firmware_version
print(f"PN532 ready. Firmware: {ver}.{rev}")
pn532.SAM_configuration()

try:
    print("Waiting for NFC card...")
    while True:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is not None:
            uid_string = ''.join(f'{byte:02x}' for byte in uid) #bascily formats the uid into a hex string
            print(f"Scanned: {uid_string}")
            try:
                requests.post(
                    f"{SERVER}/notify-scan",
                    json={"uid": uid_string},
                    headers=HEADERS,
                    timeout=6
                )
                print(f"Notified server")
            except Exception as e:
                print(f"Could not notify server: {e}")
            time.sleep(1.5)
            print("Waiting for NFC card...")
except KeyboardInterrupt:
    print("\nStopped.")