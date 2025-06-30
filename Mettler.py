import os
import socket
import re
from dotenv import load_dotenv
import sys


load_dotenv()

def get_weight():
    try:
        # Get environment variables
        ip = os.getenv('SCALE_HOST')
        port_str = os.getenv('SCALE_PORT')
        
        if not ip:
            raise ValueError("Scale IP not set. Use SCALE_IP, SCALE_HOST or SCALE_ADDRESS")
        if not port_str:
            raise ValueError("Scale port not set. Use SCALE_PORT or SCALE_PORT_NUMBER")
        
        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"Invalid port number: {port_str}")

        # Connection setup
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3.0)
            s.connect((ip, port))
            s.send(b'SI\r\n')
            response = s.recv(32).decode().strip()
            
            # Parse response
            if response == 'ES':
                return "ERROR: Scale stabilization issue"
                
            numbers = re.findall(r"[-+]?\d+\.\d+", response)
            if numbers:
                return float(numbers[0]) * 1000
                
            return f"ERROR: Unexpected response - {response}"
            
    except Exception as e:
        return f"ERROR: {str(e)}"

if __name__ == "__main__":
    try:
        weight = get_weight()
        if isinstance(weight, float):
            print(f"\nWEIGHT: {weight:.1f}g")
        else:
            print(f"\n{weight}")
    except Exception as e:
        print(f"\nCRITICAL ERROR: {str(e)}")
        sys.exit(1)