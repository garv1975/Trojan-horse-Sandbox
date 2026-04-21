import os
import time
import shutil
import base64
import random
from pathlib import Path
from event_stream import broadcast_event

# Define safe, controlled paths relative to the project root
BASE_DIR = Path(__file__).parent.parent
CORE_DIR = BASE_DIR / "core"
VICTIM_DIR = BASE_DIR / "victim_data"
STOLEN_DIR = BASE_DIR / "stolen_data"

# Fixed C2 address so it is clearly distinct from localhost in the dashboard
C2_SERVER_IP = "192.168.0.99"
C2_SERVER_PORT = 443

def trigger_trojan_simulation(captured_data=None):
    """
    Kicks off the scenario in a background thread to prevent blocking
    the web request that triggered the "Download Invoice" action.
    captured_data: dict with dynamically captured user input from the web forms.
    """
    import threading
    t = threading.Thread(target=_run_simulation, args=(captured_data or {},))
    t.start()

def _run_simulation(captured_data):
    # --- PHASE 1: EXECUTION ---
    broadcast_event("status_update", {"stage": "Execution", "msg": "Payload executed via Invoice_Order_45821.pdf"})
    time.sleep(1)

    # --- PHASE 2: CREDENTIAL CAPTURE (dynamic user input) ---
    broadcast_event("status_update", {"stage": "Credential Capture", "msg": "Harvesting user-supplied credentials from browser session."})
    time.sleep(0.8)

    username    = captured_data.get('username', 'unknown')
    display     = captured_data.get('display_name', username)
    password    = captured_data.get('password', '')
    card_number = captured_data.get('card_number', '')
    card_expiry = captured_data.get('card_expiry', '')
    card_cvv    = captured_data.get('card_cvv', '')

    # Broadcast captured credentials to the dashboard (full card & CVV)
    broadcast_event("exfiltrated_data", {
        "user": display,
        "email": captured_data.get('email', ''),
        "password": password,
        "card_number": card_number,
        "card_expiry": card_expiry,
        "card_cvv": card_cvv,
    })
    time.sleep(0.5)

    # --- PHASE 3: ACCESSING STORED SENSITIVE FILES ---
    broadcast_event("status_update", {"stage": "Access", "msg": "Scanning for sensitive files in sandbox."})
    stolen_creds = {}

    bank_file = CORE_DIR / "bank_data.txt"
    if bank_file.exists():
        broadcast_event("file_activity", {"action": "READ", "file": "core/bank_data.txt"})
        with open(bank_file, "r") as f:
            stolen_creds['bank'] = f.read()
        time.sleep(0.5)

    session_file = CORE_DIR / "session_data.txt"
    if session_file.exists():
        broadcast_event("file_activity", {"action": "READ", "file": "core/session_data.txt"})
        with open(session_file, "r") as f:
            stolen_creds['session'] = f.read()
        time.sleep(0.5)

    # --- PHASE 4: EXFILTRATION & C2 COMMUNICATION ---
    broadcast_event("status_update", {"stage": "Exfiltration", "msg": f"Initiating C2 connection to {C2_SERVER_IP}..."})
    time.sleep(1)

    broadcast_event("c2_network", {
        "type": "CONNECT",
        "source": "127.0.0.1:5000 (victim)",
        "target": C2_SERVER_IP,
        "port": C2_SERVER_PORT
    })
    time.sleep(1)

    broadcast_event("c2_network", {
        "type": "SEND",
        "source": "127.0.0.1:5000 (victim)",
        "target": C2_SERVER_IP,
        "port": C2_SERVER_PORT,
        "size": "4 KB",
        "desc": f"Sending harvested credentials for user '{display}'."
    })

    # Save the "stolen" data locally to simulate exfiltration success
    dump_file = STOLEN_DIR / f"dump_{int(time.time())}.log"
    with open(dump_file, "w") as f:
        f.write(f"=== CAPTURED USER INPUT ===\n")
        f.write(f"Username : {username}\n")
        f.write(f"Password : {password}\n")
        f.write(f"Card     : {card_number}\n")
        f.write(f"Expiry   : {card_expiry}\n")
        f.write(f"CVV      : {card_cvv}\n\n")
        for k, v in stolen_creds.items():
            f.write(f"--- {k.upper()} DATA ---\n{v}\n")

    broadcast_event("file_activity", {"action": "WRITE", "file": f"stolen_data/{dump_file.name}"})
    time.sleep(1)

    broadcast_event("c2_network", {
        "type": "RECEIVE",
        "source": C2_SERVER_IP,
        "target": "127.0.0.1:5000 (victim)",
        "port": C2_SERVER_PORT,
        "size": "120 bytes",
        "desc": "Command received: Execute module [Ransomware]"
    })
    time.sleep(1)

    # --- PHASE 5: IMPACT (safe simulated encryption within victim_data) ---
    broadcast_event("status_update", {"stage": "Impact", "msg": "Beginning targeted filesystem encryption."})

    for item in VICTIM_DIR.iterdir():
        if item.is_file() and not item.name.endswith(".encrypted"):
            broadcast_event("file_activity", {"action": "ENCRYPT", "file": f"victim_data/{item.name}"})

            with open(item, "rb") as f:
                content = f.read()

            # Simulated encryption (mock — just base64 encoding with a fake header)
            enc_content = b"TROJAN_ENCRYPTED_HEADER_V1:" + base64.b64encode(content)

            enc_file = item.with_name(item.name + ".encrypted")
            with open(enc_file, "wb") as f:
                f.write(enc_content)

            item.unlink()  # Delete original file
            time.sleep(0.8)  # Slow down for dramatic UI effect

    # --- PHASE 6: COMPLETE ---
    broadcast_event("status_update", {"stage": "Complete", "msg": "Simulation cycle finished. IOCs generated."})

    # Generate final static report
    _generate_final_report(captured_data)
    broadcast_event("report_ready", {"status": True})

def _generate_final_report(captured_data):
    import json
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": "Banking Trojan Simulation",
        "victim": {
            "username": captured_data.get('username', 'unknown'),
            "display_name": captured_data.get('display_name', 'Unknown'),
            "email": captured_data.get('email', ''),
        },
        "iocs": {
            "network": [
                {"address": C2_SERVER_IP, "port": C2_SERVER_PORT, "type": "Mock C2 Server"},
                {"address": "127.0.0.1", "port": 5000, "type": "Local Application (Victim)"}
            ],
            "files_accessed": [
                "core/bank_data.txt",
                "core/session_data.txt"
            ],
            "stolen_artifacts": [
                p.name for p in STOLEN_DIR.iterdir() if p.is_file()
            ],
            "encrypted_files": [
                p.name for p in VICTIM_DIR.iterdir() if p.name.endswith(".encrypted")
            ],
            "malware_hashes": [
                {"algorithm": "MD5", "hash": "d41d8cd98f00b204e9800998ecf8427e", "desc": "Dummy Invoice Payload"}
            ]
        },
        "risk_level": "CRITICAL"
    }

    with open(BASE_DIR / "behavior_report.json", "w") as f:
        json.dump(report, f, indent=4)
