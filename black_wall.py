import socket
from urllib.parse import urlparse
import threading
import select
import os, subprocess, ssl

HOST = '127.0.0.1'
PORT = 8080

def handle_client(c_socket):
    try:
        brute_data = c_socket.recv(4096)
        if not brute_data:
            c_socket.close()
            return

        method, complete_url = split_petition_data(brute_data)
        if method == None and complete_url == None:
            c_socket.close()
            return

        urlparsed, url_port = connect_or_else(method, complete_url)
        print(f"[+] Recived petition for site:{method} -> {urlparsed}:{url_port}")
        
        daemon_blackwall(urlparsed, brute_data, c_socket, method, urlparsed, url_port)
    except Exception as e:
        print(f"[!] Error handling client: {e}")
        c_socket.close()

def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_socket:
        s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_socket.bind((HOST, PORT))
        s_socket.listen(5)
        print(f"""\033[91m
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
 ║    >_ [ LISTENING ON ] {HOST}:{PORT}                                           ║
 ║                                                                                ║
 ╚════════════════════════════════════════════════════════════════════════════════╝\033[0m
        """)

        while True:
            c_socket, c_address= s_socket.accept()
            threading.Thread(target=handle_client, args=(c_socket,)).start()

def daemon_blackwall(urlparsed, brute_data, c_socket, method, url_host, url_port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        if method=='CONNECT':
            try:
                c_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

                cert_path, key_path = certificade_forge(url_host)

                ctx_serv = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx_serv.load_cert_chain(certfile=cert_path, keyfile=key_path)
                c_ssl = ctx_serv.wrap_socket(c_socket, server_side=True)

                server_socket.connect((url_host, url_port))
                ctx_client = ssl.create_default_context()
                s_ssl = ctx_client.wrap_socket(server_socket, server_hostname=url_host)

            except Exception as e:
                print(f"[!] Connection failed {url_host}", e)
                return

            inputs = [c_ssl, s_ssl]

            while inputs:
                readable, _, _ = select.select(inputs, [], [])
                
                for sock in readable:
                    if sock is c_ssl:
                        brute_data = c_ssl.recv(4096)
                        print(f"[!!!!!unencrypted] {brute_data}")
                        if brute_data:
                            s_ssl.sendall(brute_data)
                        else:
                            print("[+] Closing conection with: ", s_ssl.getpeername())
                            s_ssl.close()
                            return

                    elif sock is s_ssl:
                        server_responce = s_ssl.recv(4096)
                        print(f"[!!!!!unencrypted] {server_responce}")
                        if server_responce:
                            c_ssl.sendall(server_responce)
                        else:
                            print("[+] Closing conection with: ", c_ssl.getpeername())
                            c_ssl.close()
                            return
        else:
            server_socket.connect((urlparsed, url_port))
            server_socket.sendall(brute_data)

            while True:
                server_responce = server_socket.recv(4096)
                if not server_responce:
                    break
                c_socket.sendall(server_responce)
            c_socket.close()


def split_petition_data(brute_data):
    petition = brute_data.decode('utf-8', errors ='ignore')
    petition_lines = petition.split('\r\n')
    petition_line_one = petition_lines[0]
    try:
        complete_url = petition_line_one.split(' ')
        method=complete_url[0]
    except:
        print("[!] No such valid petition D:")
        return None, None
    
    return method, complete_url


def connect_or_else(method, complete_url):
    url_host = None
    url_port = None
    urlparsed = None

    if method=='CONNECT':
        url_host = complete_url[1].split(':')[0]
        return url_host, 443
    else:
        urlparsed = urlparse(complete_url[1]).hostname
        url_port = urlparse(complete_url[1]).port
        if url_port is None:
            url_port = 80
        return urlparsed, url_port 

import threading
cert_lock = threading.Lock()

def certificade_forge(domain):
    cert_path = f"certs/{domain}.crt"
    key_path = f"certs/{domain}.key"
    csr_path = f"certs/{domain}.csr"
    ext_path = f"certs/{domain}.ext"

    with cert_lock:
        if os.path.exists(cert_path):
            return cert_path, key_path

        print(f"[*]Fake identity forge for: {domain}")

        with open(ext_path, "w") as f:
            f.write(f"subjectAltName=DNS:{domain}\n")
            f.write("extendedKeyUsage=serverAuth\n")

        subprocess.run(["openssl", "genrsa", "-out", key_path, "2048"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["openssl", "req", "-new", "-key", key_path, "-out", csr_path, "-subj", f"/CN={domain}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  
        subprocess.run(["openssl", "x509", "-req", "-in", csr_path, "-CA", "blackwall_ca.crt", "-CAkey", "blackwall_ca.key", "-CAcreateserial", "-out", cert_path, "-days", "365", "-extfile", ext_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return cert_path, key_path

if __name__ == '__main__':
    try:
        listen()
    except KeyboardInterrupt:
        print("[Black Wall] is stopping, goodbye!") 

