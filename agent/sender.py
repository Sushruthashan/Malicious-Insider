import requests
import json
from config import SERVER_URL

def send_log(data):
    try:
        headers = {'Content-Type': 'application/json'}
        requests.post(SERVER_URL, headers=headers, data=json.dumps(data), timeout=5)
    except:
        print("Server not reachable")
