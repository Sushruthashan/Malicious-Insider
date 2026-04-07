import psutil
from sender import send_log
from config import USERNAME

def check_connections():
    connections = psutil.net_connections(kind='inet')

    for conn in connections:
        if conn.raddr:
            data = {
                "user": USERNAME,
                "event_type": "network_connection",
                "value": str(conn.raddr.ip) + ":" + str(conn.raddr.port)
            }
            send_log(data)
