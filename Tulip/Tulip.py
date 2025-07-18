import os
import socket
import re
import random
import string
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Generate unique ID
def generate_random_id(length=15):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Read weight from Mettler scale
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
                return float(numbers[0]) * 1000, None  # Convert kg to g
            return None, f"ERROR: Unexpected response - {response}"
    except Exception as e:
        return None, f"ERROR: {str(e)}"

# Send weight to Tulip Table
def send_to_tulip(weight):
    try:
        endpoint = "https://partner-amc.tulip.co/api/v3/tables/iDgS8aQHa2jdktmdg/records"
        api_key = os.getenv("TULIP_API_KEY")
        api_secret = os.getenv("TULIP_API_SECRET")

        if not api_key or not api_secret:
            raise ValueError("TULIP_API_KEY and/or TULIP_API_SECRET not set")

        # Encode for Basic Auth
        auth_string = f"{api_key}:{api_secret}"
        auth_base64 = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_base64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        data = {
            "id": generate_random_id(),
            "bvyaq_value": weight
        }

        response = requests.post(endpoint, json=data, headers=headers)
        response.raise_for_status()
        return response.status_code, response.json()

    except requests.exceptions.HTTPError as e:
        print("HTTP Error")
        print("Status Code:", e.response.status_code)
        print("Response Text:", e.response.text)
        return None, f"Failed to send data to Tulip: {str(e)}"


# Main
if __name__ == "__main__":
    weight, error = get_weight()
    if error:
        print(error)
    elif weight:
        print(f"Weight: {weight:.1f}g")
        status, result = send_to_tulip(weight)
        if status:
            print(f"Data sent to Tulip (HTTP {status})")
            print(f"Response: {result}")
        else:
            print(result)

"""
URL for Arkite InflufDB = https://aws-influxdb-dmi-4iorviw6v5obag.eu-west-1.timestream-influxdb.amazonaws.com:8086/api/v2/write?bucket=dmi-bucket&precision=s&org=dmi-org
Token = ? Need to write directly to a variable within Arkite...
"""