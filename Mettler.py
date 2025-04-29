import socket
import logging
import time
import re  # Added for better number extraction
import os

host = os.getenv("SCALE_HOST")
port = int(os.getenv("SCALE_PORT"))
TIMEOUT = 3.0

if host is None or port is None:
    raise ValueError("IP address or Port number missing")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def get_weight():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            s.connect((host, port))
           
            s.send(b'SI\r\n')
            response = s.recv(32).decode().strip()
           
            numbers = re.findall(r"[-+]?\d+\.\d+", response)
            if numbers:
                grams = float(numbers[0]) * 1000
                return f"{grams:.1f} grams"  # Only grams in output
            return f"Error: Couldn't parse weight from: {response}"

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("=== Mettler Scale Reader ===")
    start = time.time()
    result = get_weight()
    print(f"\n{result}")
    print(f"\nRuntime: {time.time()-start:.2f}s")