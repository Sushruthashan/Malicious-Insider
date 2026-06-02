import requests
from config import SERVER_URL

# ===============================
# CONFIG
# ===============================
API_KEY = "CHANGE_THIS_SECRET_KEY"

# ===============================
# GLOBAL SESSION
# ===============================
session = requests.Session()

# ===============================
# SEND LOG
# ===============================
def send_log(data):

    headers = {
        "X-API-KEY": API_KEY
    }

    try:

        response = session.post(
            SERVER_URL,
            json=data,
            headers=headers,
            timeout=3
        )

        if response.status_code != 200:

            print(
                f"[!] Server Error "
                f"({response.status_code})"
            )

            return False

        print(f"[✓] Sent: {data}")

        return True

    except requests.exceptions.Timeout:

        print(
            "[!] Timeout: Server took too long."
        )

    except requests.exceptions.ConnectionError:

        print(
            "[!] Connection Error: "
            "Server unreachable."
        )

    except Exception as e:

        print(f"[!] Sender Error: {e}")

    return False
