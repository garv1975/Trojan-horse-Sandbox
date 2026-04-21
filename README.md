# 🛡️ Trojan Attack Simulation Sandbox

## 📌 Overview  
This project is an interactive web-based sandbox that simulates a **Trojan Horse attack scenario** to demonstrate how sensitive user data (like card details and system files) can be compromised and monitored in real time.

It is designed for **educational and cybersecurity awareness purposes only**, helping users understand attack mechanisms and preventive measures.

---

## 👥 Team Members  
- Garv Gupta  
- Ashlesha Agrawal  
- Aashi Soni  

---

## 🎯 Features  
- 💻 Simulated e-commerce payment interface  
- 📄 Fake invoice download triggering hidden malicious activity  
- 🔓 Demonstration of data exfiltration (card details, system info)  
- 🔐 File encryption simulation (ransomware-like behavior)  
- 📊 Admin dashboard to monitor captured data  
- ⚠️ Real-time attack visualization  

---

## 🧠 Objectives  
- Explain how Trojan Horse attacks work in real-world scenarios  
- Demonstrate how users unknowingly execute malicious code  
- Highlight the importance of cybersecurity practices  
- Provide a safe environment for learning ethical hacking concepts  

---

## 🛠️ Tech Stack  
- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Node.js / Python  
- **Database:** MySQL / MongoDB  
- **Other Tools:** APIs, Encryption Libraries  

---

## ⚙️ How It Works  
1. User visits a simulated shopping website  
2. User enters payment details and completes purchase  
3. When downloading the invoice:  
   - A hidden Trojan script is triggered  
   - Sensitive data is captured and sent to the admin panel  
   - Files may be encrypted (simulated ransomware behavior)  
4. Admin dashboard displays all captured information  

---

## 🚀 Installation  

```bash
git clone https://github.com/your-username/trojan-sandbox.git
cd trojan-sandbox
npm install
npm start