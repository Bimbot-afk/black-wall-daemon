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

## How to install and run

*>Note, if you want to see the dashboard, you need to run the python script, because it creates a simple server to host the html page and listen for api requests.*

1. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the daemon:**
   Start the proxy server by executing:
   ```bash
   python black_wall.py
   ```

3. **Configuration:**
   - Configure your browser or OS proxy to route traffic to `127.0.0.1:8080`.
   - Install the generated `blackwall_ca.crt` in your trusted Root Certification Authorities to avoid browser warnings.
   - Access the control hub at `http://127.0.0.1:5000` to monitor traffic and block domains.

## What is Black Wall?
**Black Wall** is a MITM (Man-In-The-Middle) proxy developed in Python. It runs locally on port `8080` and listens to, intercepts, and analyzes HTTP and HTTPS requests made through your browser. 

## Why use Black Wall?
Thanks to Black Wall, it is possible to have **total visibility** over the connections your browser makes in the background. You will be able to know:
- Exactly which servers you connect to.
- Which HTTP methods are used (GET, POST, CONNECT, etc.).
- Deduce the purpose of each connection (telemetry, trackers, etc.).
With this, you can discover which services track your browsing, analyze the network traffic of web applications, and take control of your data.

## Is it safe? Will I get hacked?
**No.** The proxy runs entirely locally on your own machine and network. Currently, it acts as a "transparent glass": it allows you to see all the traffic passing through it without maliciously modifying the packets you send or receive. It works by intercepting certificates and generating fake ones on the fly to decrypt HTTPS traffic locally before re-encrypting it towards the original destination, but everything happens strictly inside your PC.
## How does it work?
1. **Traffic Interception**: You configure your operating system or browser to send all its web traffic to `127.0.0.1:8080`.
2. **Dynamic Certificate Generation**: When you try to access a secure site (HTTPS), Black Wall intercepts the `CONNECT` request, temporarily halts the flow, and instantly forges a valid SSL certificate for that specific domain (signed by its own local CA).
3. **Decryption and Analysis**: The browser trusts the fake certificate (provided you have installed the CA on your system), allowing Black Wall to decrypt and read the packets in plain text.
4. **Forwarding**: Finally, the proxy repackages the request and sends it through a secure channel to the real destination server. The response takes the same journey back.

## Future Improvements (Roadmap)
The project is constantly evolving. Some of the features planned for the future are:
- [ ] **AdBlocker**: Ability to intercept and discard requests directed at known ad servers before they even leave your network. (So complex 🥀)
- [x] **Custom Blacklists**: You will be able to add your own list of blocked domains to prevent connections to unwanted services.
- [x] **Dashboard**: A user-friendly interface to visualize real-time traffic in a cleaner way.
---

## What I have learned?

This project were really complex and im kinda sad for not achive being able to eddit the html of the page, and inyect the c++ to destroy the adds, maybe next time with more time i will reach it! even tho I can proudly say I learned a lot about everything related with networking, sockets, how works a MITM,
what is actually a proxy, how works the HTTP and the BIG diference with HTTPS, certifcates.

Also I noticed the amount of telemetry and data tracking that modern websites do, it's really impresive, and how many things run in the background without our knoledge.

if u reading this, thanks <3.
