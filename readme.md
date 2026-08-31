```text
 ╔════════════════════════════════════════════════════════════════════════════════╗
 ║                                                                                ║
 ║  ██████╗ ██╗      █████╗  ██████╗██╗  ██╗██╗    ██╗ █████╗ ██╗     ██╗         ║
 ║  ██╔══██╗██║     ██╔══██╗██╔════╝██║  ██║██║    ██║██╔══██╗██║     ██║         ║
 ║  ██████╔╝██║     ███████║██║     ███████║██║ █╗ ██║███████║██║     ██║         ║
 ║  ██╔══██╗██║     ██╔══██║██║     ██╔══██║██║███╗██║██╔══██║██║     ██║         ║
 ║  ██████╔╝███████╗██║  ██║╚██████╗██║  ██║╚███╔███╔╝██║  ██║███████╗███████╗    ║
 ║  ╚══════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝   ║
 ║                                                                                ║
 ╠════════════════════════════════════════════════════════════════════════════════╣
 ║                                                                                ║
 ║    >_ [ BLACK WALL DAEMON ] is running >:D                                     ║
 ║    >_ [ STATUS ] INTERCEPTING TRAFFIC...                                       ║
 ║    >_ [ LISTENING ON ] 127.0.0.1:8080                                          ║
 ║                                                                                ║
 ╚════════════════════════════════════════════════════════════════════════════════╝
```
<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Cryptography-000000?style=for-the-badge&logo=expensify&logoColor=white" alt="Cryptography" />
  <img src="https://img.shields.io/badge/Sockets-FF6F00?style=for-the-badge&logo=databricks&logoColor=white" alt="Sockets" />
  <img src="https://img.shields.io/badge/SSL%2FTLS-20232A?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="SSL" />
</div>
<br>
## 🛡️ What is Black Wall?
**Black Wall** is a MITM (Man-In-The-Middle) proxy developed in Python. It runs locally on port `8080` and listens to, intercepts, and analyzes HTTP and HTTPS requests made through your browser. 
## 👁️ Why use Black Wall?
Thanks to Black Wall, it is possible to have **total visibility** over the connections your browser makes in the background. You will be able to know:
- Exactly which servers you connect to.
- Which HTTP methods are used (GET, POST, CONNECT, etc.).
- Deduce the purpose of each connection (telemetry, trackers, etc.).
With this, you can discover which services track your browsing, analyze the network traffic of web applications, and take control of your data.
## 🔒 Is it safe? Will I get hacked?
**No.** The proxy runs entirely locally on your own machine and network. Currently, it acts as a "transparent glass": it allows you to see all the traffic passing through it without maliciously modifying the packets you send or receive. It works by intercepting certificates and generating fake ones on the fly to decrypt HTTPS traffic locally before re-encrypting it towards the original destination, but everything happens strictly inside your PC.
## ⚙️ How does it work?
1. **Traffic Interception**: You configure your operating system or browser to send all its web traffic to `127.0.0.1:8080`.
2. **Dynamic Certificate Generation**: When you try to access a secure site (HTTPS), Black Wall intercepts the `CONNECT` request, temporarily halts the flow, and instantly forges a valid SSL certificate for that specific domain (signed by its own local CA).
3. **Decryption and Analysis**: The browser trusts the fake certificate (provided you have installed the CA on your system), allowing Black Wall to decrypt and read the packets in plain text.
4. **Forwarding**: Finally, the proxy repackages the request and sends it through a secure channel to the real destination server. The response takes the same journey back.
## 🚀 Future Improvements (Roadmap)
The project is constantly evolving. Some of the features planned for the future are:
- [ ] **AdBlocker**: Ability to intercept and discard requests directed at known ad servers before they even leave your network.
- [ ] **Custom Blacklists**: You will be able to add your own list of blocked domains to prevent connections to unwanted services.
- [ ] **Dashboard**: A user-friendly interface to visualize real-time traffic in a cleaner way.
---
> *"Know your traffic, rule your network."*