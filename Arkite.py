import os
import socket
import re
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Config from .env
ARKITE_BASE_URL = os.getenv("ARKITE_API_URL", "https://192.168.200.126")
ARKITE_API_KEY = os.getenv("ARKITE_API_KEY")
ARKITE_PROJECT_ID = os.getenv("ARKITE_PROJECT_ID")  
ARKITE_VARIABLE_ID = os.getenv("ARKITE_VARIABLE_ID")
SCALE_HOST = os.getenv("SCALE_HOST")
SCALE_PORT = int(os.getenv("SCALE_PORT", 0))
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

if not ARKITE_API_KEY:
    raise ValueError("Missing ARKITE_API_KEY in environment variables.")
if not ARKITE_PROJECT_ID or not ARKITE_VARIABLE_ID:
    raise ValueError("Missing ARKITE_PROJECT_ID or ARKITE_VARIABLE_ID in environment variables.")

DEBUG = True

def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def get_weight():
    try:
        if not SCALE_HOST or not SCALE_PORT:
            raise ValueError("Missing SCALE_HOST or SCALE_PORT.")

        debug(f"Connecting to scale at {SCALE_HOST}:{SCALE_PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3.0)
            s.connect((SCALE_HOST, SCALE_PORT))
            s.send(b'SI\r\n')
            response = s.recv(32).decode().strip()

        debug(f"Raw scale response: {response}")

        if response == 'ES':
            return None, "Scale stabilization issue"

        numbers = re.findall(r"[-+]?\d+\.\d+", response)
        if numbers:
            weight = float(numbers[0]) * 1000  # Convert to grams
            debug(f"Parsed weight: {weight} g")
            return weight, None

        return None, f"Unexpected response: {response}"
    except Exception as e:
        return None, str(e)

def push_to_arkite(weight):
    """
    Pushes the weight value to Arkite API as DefaultState
    Args:
        weight (float): Weight value in grams from scale
    """
    url = f"{ARKITE_BASE_URL}/api/v1/projects/{ARKITE_PROJECT_ID}/variables/{ARKITE_VARIABLE_ID}?apiKey={ARKITE_API_KEY}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Format weight to 1 decimal place and convert to string
    formatted_weight = f"{weight:.1f}"
    
    payload = {
        "DefaultState": formatted_weight 
    }

    print(f"\n[INFO] URL: {url}")
    print(f"[INFO] Payload: {payload}")

    if MOCK_MODE:
        print(f"[MOCK] Would send weight: {formatted_weight} g (MOCK_MODE enabled)")
        return

    try:
        debug("Sending PATCH request to Arkite API...")
        response = requests.patch(
            url, 
            json=payload, 
            headers=headers, 
            verify=False,  # Bypass SSL verification
            timeout=10     # 10 second timeout
        )

        debug(f"Response status: {response.status_code}")
        debug(f"Response text: {response.text}")

        if response.status_code == 204:
            print(f"[SUCCESS] Updated DefaultState to {formatted_weight} g")
        else:
            print(f"[FAILED] {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] API request failed: {str(e)}")

if __name__ == "__main__":
    print("[INFO] Starting Arkite Weight Integration...")
    print(f"[INFO] MOCK_MODE: {MOCK_MODE}")

    weight, error = get_weight()
    if error:
        print(f"[ERROR] Failed to read from scale: {error}")
    else:
        print(f"[INFO] Scale weight: {weight:.1f} g")
        push_to_arkite(weight)
