import psutil
from sender import send_log
from config import USERNAME

EVENT_TYPE = "process_execution"

SUSPICIOUS_NAMES = [
    "nc", "ncat", "netcat",
    "nmap", "wireshark", "tcpdump",
    "scp", "ftp", "wget", "curl",
    "zip", "tar", "base64",
]

SUSPICIOUS_ARGS = [
    "nc", "ncat", "netcat",
    "nmap", "wireshark", "tcpdump",
    "bash -i", "python -c",
    "chmod 777", "sudo su",
    "wget", "curl", "base64",
    "/tmp/", "./"
]

import re
SUSPICIOUS_PATTERNS = [re.compile(p) for p in [
    r"\bnc\b", r"\bncat\b", r"netcat", r"nmap",
    r"wireshark", r"tcpdump", r"chmod\s+777",
    r"sudo\s+su", r"bash\s+-i", r"python\s+-c",
    r"\bcurl\b", r"\bwget\b", r"base64", r"/tmp/", r"\./",
]]

# Deduplicate by (normalized cmdline) not PID
# so sudo nc / nc / forked nc all collapse to one entry
seen_cmdlines = set()

def normalize_cmdline(cmdline_str):
    # Strip leading sudo, normalize whitespace
    cleaned = re.sub(r"^sudo\s+", "", cmdline_str.strip())
    return re.sub(r"\s+", " ", cleaned)

def check_processes():
    global seen_cmdlines
    active_cmdlines = set()

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name       = (proc.info['name'] or "").lower().strip()
            cmdline    = proc.info['cmdline'] or []
            cmdline_str = normalize_cmdline(" ".join(cmdline).lower())

            if not cmdline_str:
                continue

            active_cmdlines.add(cmdline_str)

            if cmdline_str in seen_cmdlines:
                continue

            matched = False

            # Exact name match
            for sus in SUSPICIOUS_NAMES:
                if sus == name:
                    matched = True
                    break

            # Full cmdline pattern match
            if not matched:
                for pattern in SUSPICIOUS_PATTERNS:
                    if pattern.search(cmdline_str):
                        matched = True
                        break

            if matched:
                seen_cmdlines.add(cmdline_str)
                send_log({
                    "user":       USERNAME,
                    "event_type": EVENT_TYPE,
                    "value":      cmdline_str
                })
                print(f"[PROCESS] Suspicious: {cmdline_str}")

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Clean up finished processes
    seen_cmdlines &= active_cmdlines
