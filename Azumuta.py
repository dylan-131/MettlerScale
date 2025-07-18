import requests
import os
import socket
import re
from dotenv import load_dotenv

load_dotenv()

AZUMUTA_API_TOKEN = os.getenv("AZUMUTA_API_KEY")
WORKINSTRUCTION_ID = "p6LBNeNicSgkxHbXR"  
STEP_UUID = "e7d086ec-2f5f-4567-b941-4f915dd187bc" 

def get_weight():
    try:
        ip = os.getenv('SCALE_HOST')
        port_str = os.getenv('SCALE_PORT')

        if not ip:
            raise ValueError("Scale IP not set. Use SCALE_HOST.")
        if not port_str:
            raise ValueError("Scale port not set. Use SCALE_PORT.")

        port = int(port_str)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3.0)
            s.connect((ip, port))
            s.send(b'SI\r\n')
            response = s.recv(32).decode().strip()

            if response == 'ES':
                return None, "ERROR: Scale stabilization issue"

            numbers = re.findall(r"[-+]?\d+\.\d+", response)
            if numbers:
                return float(numbers[0]) * 1000, None  # Convert kg to grams
            return None, f"ERROR: Unexpected response - {response}"
    except Exception as e:
        return None, f"ERROR: {str(e)}"

def update_step(weight_grams):
    # Format weight with 1 decimal place
    formatted_weight = f"{weight_grams:.1f}"

    url = f"https://app.azumuta.com/api/v1/workinstructions/{WORKINSTRUCTION_ID}/steps/{STEP_UUID}"
    headers = {
        "X-API-Key": AZUMUTA_API_TOKEN,
        "Content-Type": "application/json"
    }
    
    # Update description with formatted weight
    new_description = {"en": f"Weight recorded: {formatted_weight} g"}
    payload = {"description": new_description}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Step updated successfully!")
        print(response.json())
    else:
        print(f"Failed to update step. Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    weight, error = get_weight()
    if error:
        print(error)
    else:
        print(f"Current weight: {weight:.1f} g")
        update_step(weight)
