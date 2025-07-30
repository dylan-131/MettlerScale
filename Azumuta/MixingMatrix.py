import requests
import os
from dotenv import load_dotenv

load_dotenv()

AZUMUTA_API_TOKEN = os.getenv("AZUMUTA_API_KEY")

workinstruction_id = "SarLiLeyuNWgw3Tai"
user_id = "GsAN2Cvyf6uqYTJ25"

def update_competency(workinstruction_id, user_id):
    url = "https://app.azumuta.com/api/v1/competencies/status"
    headers = {
        "X-API-Key": AZUMUTA_API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "workinstructionId": workinstruction_id,
        "userId": user_id,
        "trainedWorkinstructionVersion": 10,
        "level": 5,
        "notes": "Testing API"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Competency updated successfully!")
        print(response.json())
    else:
        print(f"Failed to update competency. Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    update_competency(workinstruction_id, user_id)