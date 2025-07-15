import requests

url = "http://10.60.0.52/units/1/variables/"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "kHczGVm9v"
}
payload = [
    {
        "Name": "WeightData",
        "CurrentState": "12.3"
    }
]

response = requests.put(url, json=payload, headers=headers)

if response.status_code == 204:
    print("Success! Variable updated.")
else:
    print(f"Failed: {response.status_code} - {response.text}")
