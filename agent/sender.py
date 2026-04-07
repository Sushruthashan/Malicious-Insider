import requests
from config import SERVER_URL

# Create a global session object to reuse TCP connections
session = requests.Session()

def send_log(data):
    """
    Sends log data to the Flask server with error handling and connection pooling.
    """
    try:
        # Use 'json=' parameter instead of json.dumps() + headers manually
        # It automatically sets Content-Type to application/json
        response = session.post(SERVER_URL, json=data, timeout=3)
        
        # Check if the server actually accepted the log (200 OK)
        if response.status_code != 200:
            print(f"[!] Server Error: Received status {response.status_code}")
            return False
            
        return True

    except requests.exceptions.Timeout:
        print("[!] Network Timeout: Server is taking too long to respond.")
    except requests.exceptions.ConnectionError:
        print("[!] Connection Error: Is the Flask server running?")
    except Exception as e:
        print(f"[!] Unexpected Error in sender: {e}")
    
    return False
