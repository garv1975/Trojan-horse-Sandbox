import os

def create_structure():
    dirs = [
        "backend",
        "frontend/templates/shop",
        "frontend/templates/dashboard",
        "frontend/static",
        "core",
        "victim_data",
        "stolen_data"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    # 1. Create dummy target data in core/
    bank_data = """Name: Garv Sharma
Card Number: 4111 1111 1111 1111
Expiry: 12/28
CVV: 123
"""
    with open("core/bank_data.txt", "w") as f:
        f.write(bank_data)
        
    session_data = """SessionID: a1b2c3d4e5f6
Username: garv
Email: garv@example.com
PasswordHash: 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92 # ('test@123' sha256)
LastLogin: 2026-04-15 00:00:00
"""
    with open("core/session_data.txt", "w") as f:
        f.write(session_data)

    # 2. Create some dummy files in victim_data to be "encrypted" later
    with open("victim_data/passwords.txt", "w") as f:
        f.write("admin:hunter2\nroot:toor123\n")
    with open("victim_data/project_notes.txt", "w") as f:
        f.write("Important details about the Trojan project.\nDo not lose this file.\n")
    with open("victim_data/personal_diary.txt", "w") as f:
        f.write("15 April 2026: Successfully demonstrated the project.\n")

    # 3. Create a dummy PDF file logic for invoice to be served by Flask
    invoice_content = b"%PDF-1.4\n1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R>> endobj\n4 0 obj <</Length 55>> stream\nBT /F1 24 Tf 100 700 Td (Invoice Order 45821 - Thank You!) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000213 00000 n\ntrailer <</Size 5/Root 1 0 R>>\nstartxref\n319\n%%EOF"
    os.makedirs("backend/assets", exist_ok=True)
    with open("backend/assets/Invoice_Order_45821.pdf", "wb") as f:
        f.write(invoice_content)

if __name__ == "__main__":
    create_structure()
    print("Project structure and dummy files created successfully.")
