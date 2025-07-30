import os
import socket
import re
import requests
import time
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
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))  # Polling interval in seconds
WEIGHT_THRESHOLD = float(os.getenv("WEIGHT_THRESHOLD", "0.5"))  # Minimum weight in grams to consider

if not ARKITE_API_KEY:
    raise ValueError("Missing ARKITE_API_KEY in environment variables.")
if not ARKITE_PROJECT_ID or not ARKITE_VARIABLE_ID:
    raise ValueError("Missing ARKITE_PROJECT_ID or ARKITE_VARIABLE_ID in environment variables.")

DEBUG = True

def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

def get_weight():
    """
    Continuously polls the scale for weight readings.
    Only returns stable, non-zero weights.
    """
    if not SCALE_HOST or not SCALE_PORT:
        raise ValueError("Missing SCALE_HOST or SCALE_PORT.")
    
    last_weight = None
    last_sent_weight = None
    stability_count = 0
    stability_threshold = 3  # Number of consecutive same readings for stability
    
    print("[INFO] Starting continuous scale monitoring...")
    
    while True:
        try:
            debug(f"Polling scale at {SCALE_HOST}:{SCALE_PORT}")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3.0)
                s.connect((SCALE_HOST, SCALE_PORT))
                s.send(b'SI\r\n')
                response = s.recv(32).decode().strip()

            debug(f"Raw scale response: {response}")

            if response == 'ES':
                debug("Scale stabilization issue, continuing...")
                last_weight = None
                stability_count = 0
                time.sleep(POLL_INTERVAL)
                continue

            numbers = re.findall(r"[-+]?\d+\.\d+", response)
            if numbers:
                weight = float(numbers[0]) * 1000  # Convert to grams
                debug(f"Parsed weight: {weight} g")
                
                # Check if weight is above threshold (something on scale)
                if weight <= WEIGHT_THRESHOLD:
                    debug(f"Weight below threshold ({WEIGHT_THRESHOLD}g), ignoring...")
                    last_weight = None
                    last_sent_weight = None
                    stability_count = 0
                    time.sleep(POLL_INTERVAL)
                    continue
                
                # Check for stability
                if last_weight is not None and abs(weight - last_weight) < 0.1:
                    stability_count += 1
                    debug(f"Stable reading count: {stability_count}/{stability_threshold}")
                else:
                    stability_count = 1
                    debug("Weight changed, resetting stability count")
                
                last_weight = weight
                
                # If stable and different from last sent weight, return it
                if stability_count >= stability_threshold:
                    if last_sent_weight is None or abs(weight - last_sent_weight) > 0.1:
                        debug(f"Stable weight detected: {weight} g")
                        last_sent_weight = weight
                        yield weight
                    else:
                        debug("Weight unchanged from last sent value")
                    stability_count = 0
            else:
                debug(f"No valid weight found in response: {response}")
                last_weight = None
                stability_count = 0
                
        except Exception as e:
            debug(f"Error reading scale: {str(e)}")
            last_weight = None
            stability_count = 0
        
        time.sleep(POLL_INTERVAL)

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
            verify=False,  # This is for SSL verification
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
    print(f"[INFO] Poll Interval: {POLL_INTERVAL}s")
    print(f"[INFO] Weight Threshold: {WEIGHT_THRESHOLD}g")

    try:
        for weight in get_weight():
            print(f"\n[INFO] New stable weight detected: {weight:.1f} g")
            push_to_arkite(weight)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping weight monitoring...")
    except Exception as e:
        print(f"[ERROR] Fatal error: {str(e)}")