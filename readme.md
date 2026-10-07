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
> 2. Download the batch file "Generate CA"
> 3. Double click `generate_ca.bat` to run it. 
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
   - Configure your browser or OS proxy to route traffic to `127.0.0.1:8080`. (on windows type `"network proxy"` in the start menu and configure it)
   - Install the generated `blackwall_ca.crt` in your trusted Root Certification Authorities to avoid browser warnings. (to do that double click on it, click en install certificate, select local machine, then trusted root certification authorities and finish)
   - Access the control hub at `http://127.0.0.1:5000` to monitor traffic and block domains. (you can copy and paste this link in ur browser.)

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
# Generación de Certificados SSL para Desarrollo local

Si el script `.bat` no está generando el certificado o el archivo `.ca` correctamente (esto puede suceder por bloqueos del Antivirus o problemas de entorno en la máquina virtual/VPS donde se prueba el proyecto), sigue estas instrucciones para generarlos de manera manual.

Hay dos opciones: usar **mkcert** (recomendada porque el navegador confiará en el certificado y es muy sencilla) o usar **OpenSSL**.

---

## Opción 1: Usar `mkcert` (Recomendado)

`mkcert` crea una Autoridad Certificadora (CA) local en tu equipo para que el navegador no te muestre la advertencia de "Sitio no seguro".

### Paso 1: Instalar mkcert
- **En Windows:** Abre PowerShell como Administrador y usa Chocolatey:
  ```powershell
  choco install mkcert
  ```
  *(Alternativa: Descarga el ejecutable desde el [GitHub de mkcert](https://github.com/FiloSottile/mkcert/releases)).*
- **En macOS:** `brew install mkcert`
- **En Linux:** `sudo apt install libnss3-tools` y sigue las instrucciones de su repositorio.

### Paso 2: Crear e instalar la Autoridad Certificadora (CA)
En la terminal, ejecuta este comando para que tu equipo confíe en los certificados locales:
```bash
mkcert -install
```

### Paso 3: Generar el certificado
Ve a la carpeta de este proyecto y ejecuta:
```bash
mkcert -key-file key.pem -cert-file cert.pem localhost 127.0.0.1
```
> **Resultado:** Se crearán los archivos `key.pem` y `cert.pem`. Usa estos archivos en la configuración de tu servidor.

---

## Opción 2: Usar OpenSSL (Manual)

Si no puedes instalar `mkcert` o estás probando el proyecto en un entorno donde prefieres no instalar herramientas extra, puedes usar OpenSSL (que viene incluido en Git Bash para Windows o en casi cualquier Linux).

En tu terminal (Git Bash, WSL o Linux), ejecuta:
```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "//CN=localhost"
```
*(Nota: Si usas Linux o Mac, cambia `//CN=localhost` por `/CN=localhost`).*

> **Resultado:** Esto generará `key.pem` (clave) y `cert.pem` (certificado). 
> **Nota:** Con este método, al entrar desde el navegador verás una advertencia de "Sitio no seguro". Solo debes hacer clic en "Configuración avanzada" y "Continuar a localhost".
