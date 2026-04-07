import psutil
import time
from sender import send_log
from config import USERNAME

# To avoid duplicate logs for the same connection
seen_connections = set()

def check_connections():
    global seen_connections
    try:
        # Get all active internet connections
        connections = psutil.net_connections(kind='inet')
        current_active_remote = set()

        for conn in connections:
            # We only care about connections that are actually connected (ESTABLISHED)
            if conn.status == psutil.CONN_ESTABLISHED and conn.raddr:
                remote_ip = conn.raddr.ip
                remote_port = conn.raddr.port
                conn_id = f"{remote_ip}:{remote_port}"
                
                current_active_remote.add(conn_id)

                # If this is a new connection we haven't logged yet
                if conn_id not in seen_connections:
                    data = {
                        "user": USERNAME,
                        "event_type": "network_connection",
                        "value": conn_id
                    }
                    send_log(data)
                    print(f"[NETWORK] New outbound connection: {conn_id}")

        # Update our 'seen' list: remove connections that are no longer active
        seen_connections = current_active_remote

    except Exception as e:
        print(f"Network monitor error: {e}")

if __name__ == "__main__":
    print(f"Monitoring network for {USERNAME}...")
    while True:
        check_connections()
        time.sleep(5) # Scan every 5 seconds
