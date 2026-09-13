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

> [!IMPORTANT]
> **Before running the proxy, you need a Root CA to intercept HTTPS:**
> 1. Make sure you have OpenSSL installed and added to your PATH.
> 2. Double click `generate_ca.bat` to run it. 
> 
> This creates a master certificate (`blackwall_ca.crt`) that Black Wall uses to dynamically sign fake certificates for the servers you connect to. Without it, the proxy won't be able to read HTTPS traffic.


1. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the daemon:**
   Start the proxy server by executing: (if dosent work try running it on git bash)
   ```bash
   python black_wall.py
   ```

3. **Configuration:**
   - Configure your browser or OS proxy to route traffic to `127.0.0.1:8080`.
   - Install the generated `blackwall_ca.crt` in your trusted Root Certification Authorities to avoid browser warnings.
   - Access the control hub at `http://127.0.0.1:5000` to monitor traffic and block domains.

## What is Black Wall?
Black Wall is a local Python based MITM (Man In The Middle) proxy. It listens on port `8080` and intercepts HTTP/HTTPS requests so you can see exactly what your browser is doing behind the scenes.

## Features
I built this to get full visibility over background connections. It helps you find out:
- Which servers you're actually connecting to.
- The HTTP methods being used.
- Background telemetry and trackers hiding in plain sight.

## Security
It runs 100% locally. The proxy acts as a transparent middleman, decrypting HTTPS traffic locally using on-the-fly fake certificates, then re-encrypting it to the real server. Your traffic doesn't leave your PC except to go to its actual destination.

## How it works
1. Point your OS/browser proxy to `127.0.0.1:8080`.
2. Black Wall intercepts `CONNECT` requests for HTTPS sites and forges a valid SSL certificate on the fly using the local CA.
3. Once the browser trusts the fake cert, Black Wall decrypts and logs the packets.
4. The request is forwarded securely to the real server.

## Roadmap
- [ ] **AdBlocker**: Drop requests to known ad servers. (So complex 🥀)
- [x] **Custom Blacklists**: Block specific domains.
- [x] **Dashboard**: Real time traffic visualization.
---

## What I have learned?

This project were really complex and im kinda sad for not achive being able to eddit the html of the page, and inyect the c++ to destroy the adds, maybe next time with more time i will reach it! even tho I can proudly say I learned a lot about everything related with networking, sockets, how works a MITM,
what is actually a proxy, how works the HTTP and the BIG diference with HTTPS, certifcates.

Also I noticed the amount of telemetry and data tracking that modern websites do, it's really impresive, and how many things run in the background without our knoledge.

if u reading this, thanks <3.
