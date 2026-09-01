import socket
from urllib.parse import urlparse
import threading
import select
import os, subprocess, ssl, re
from datetime import datetime
import decompiler as decm
import certificad_forge as forge
import json
from http.server import HTTPServer, BaseHTTPRequestHandler


HOST = '127.0.0.1'
PORT = 8080
proxy_stats = {
    "total_connections": 0,
    "blocked_connections": 0
}

blocked_domains = set()
conection_logs = []
stats_lock = threading.Lock()

def update_logs(domain, method, status):
    # safe log update
    with stats_lock:
        if status == "BLOCKED":
            proxy_stats["blocked_connections"] += 1
        proxy_stats["total_connections"] += 1

        log_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "domain": str(domain),
            "method": str(method),
            "status": str(status)
        }
        conection_logs.insert(0, log_entry)
        if len(conection_logs) > 67:
            conection_logs.pop()

def check_certs():
    os.makedirs("certs", exist_ok=True)

check_certs()

def check_http_conection(Data):
    http_methods = [b"GET", b"POST", b"HEAD", b"CONNECT", b"PUT", b"DELETE", b"OPTIONS", b"PATCH"]
    for m in http_methods:
        if Data.startswith(m):
            return True
    return False

def handle_client(c_socket):
    try: 
        brute_data = c_socket.recv(4096)

        if not brute_data:
            c_socket.close()
            return

        is_http = check_http_conection(brute_data)

        if not is_http:
            c_socket.close()
            return

        method, complete_url = split_petition_data(brute_data)
        if method is None or complete_url is None:
            c_socket.close()
            return

        urlparsed, url_port = connect_or_else(method, complete_url, brute_data)

        if not urlparsed:
            c_socket.close()
            return

        with stats_lock:
            is_blocked = any(blocked_domain in urlparsed for blocked_domain in blocked_domains if blocked_domain)

        if is_blocked:
            print(f"[X] Blocked: {urlparsed} HA that bitch aint connecting >:D ( url in ur black list)")
            update_logs(urlparsed, method, "BLOCKED")
            c_socket.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\nBlack Wall: Access Denied")
            c_socket.close()
            return

        update_logs(urlparsed, method, "ALLOWED")
        print(f"[+] ALLOWED: site:{method} -> {urlparsed}:{url_port}, Good boy conection :3")

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
 ║    >_ [ LISTENING ON ] {HOST}:{PORT}                                          ║
 ║                                                                                ║
 ╚════════════════════════════════════════════════════════════════════════════════╝\033[0m
        """)

        while True:
            c_socket, c_address = s_socket.accept()
            threading.Thread(target=handle_client, args=(c_socket,), daemon=True).start()

def chunk_paser(sock, initial_buffer=b""):
    full_body = bytearray()
    lect_buffer = bytearray(initial_buffer)

    while True:
        while b'\r\n' not in lect_buffer:
            chunk = sock.recv(4096)
            if not chunk:
                return bytes(full_body)
            lect_buffer.extend(chunk)

        line_size, _, rest = lect_buffer.partition(b'\r\n')
        lect_buffer = bytearray(rest)

        try:
            chunk_size_hex = int(line_size.strip().split(b';')[0], 16)
        except ValueError:
            break

        if chunk_size_hex == 0:
            break

        while len(lect_buffer) < chunk_size_hex + 2:
            data_missing = sock.recv(4096)
            if not data_missing:
                break
            lect_buffer.extend(data_missing)

        full_body.extend(lect_buffer[:chunk_size_hex])
        lect_buffer = lect_buffer[chunk_size_hex + 2:]

    return bytes(full_body)

def read_http_message(sock):
    buffer = b""
    while b"\r\n\r\n" not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buffer += chunk

    if b"\r\n\r\n" not in buffer:
        return None, None

    headers_bytes, leftover_body = buffer.split(b"\r\n\r\n", 1)
    headers_bytes += b"\r\n\r\n"
    
    if b'HTTP/1.1 101' in headers_bytes or b'101 Switching Protocols' in headers_bytes:
        return headers_bytes, leftover_body

    if re.search(b"Transfer-Encoding:.*chunked", headers_bytes, re.IGNORECASE):
        body = chunk_paser(sock, leftover_body)
        if body is None:
            return None, None
        headers_bytes = re.sub(b"Transfer-Encoding: [^\r\n]+\r\n", b"", headers_bytes, flags=re.IGNORECASE)
    else:
        cl_match = re.search(b"Content-Length: (\\d+)", headers_bytes, re.IGNORECASE)
        if cl_match:
            expected_length = int(cl_match.group(1))
            body = bytearray(leftover_body)
            while len(body) < expected_length:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                body.extend(chunk)
            body = bytes(body[:expected_length])
        else:
            body = leftover_body

    content_encoding_match = re.search(b"Content-Encoding: ([^\r\n]+)", headers_bytes, flags=re.IGNORECASE)
    if content_encoding_match:
        encoding = content_encoding_match.group(1).strip().lower()
        decompressed_body = None
        if encoding == b'gzip':
            decompressed_body = decm.decompress_gzip(body)
        elif encoding == b'br':
            decompressed_body = decm.decompress_brotli(body)
        
        if decompressed_body is not None:
            body = decompressed_body
            headers_bytes = re.sub(b'Content-Encoding: [^\r\n]+\r\n', b'', headers_bytes, flags=re.IGNORECASE)

    if re.search(b"Content-Type:.*text/html", headers_bytes, re.IGNORECASE):
        headers_bytes = re.sub(b'Content-Length: [^\r\n]+\r\n', b'', headers_bytes, flags=re.IGNORECASE)
        new_header = f'Content-Length: {len(body)}\r\n\r\n'.encode()
        headers_bytes = headers_bytes.replace(b'\r\n\r\n', b'\r\n' + new_header)

    return headers_bytes, body

def tunnel_sockets(sock1, sock2):
    inputs = [sock1, sock2]
    while inputs:
        readable, _, _ = select.select(inputs, [], [], 10)
        if not readable:
            break
        for sock in readable:
            other = sock2 if sock is sock1 else sock1
            try:
                data = sock.recv(4096)
                if not data:
                    return
                other.sendall(data)
            except Exception:
                return

def daemon_blackwall(urlparsed, brute_data, c_socket, method, url_host, url_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        if method == 'CONNECT':
            try:
                c_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                cert_path, key_path = forge.certificade_forge(url_host)

                ctx_serv = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ctx_serv.load_cert_chain(certfile=cert_path, keyfile=key_path)
                ctx_serv.set_alpn_protocols(["http/1.1"])
                c_ssl = ctx_serv.wrap_socket(c_socket, server_side=True)

                server_socket.connect((url_host, url_port))
                ctx_client = ssl.create_default_context()
                ctx_client.check_hostname = False
                ctx_client.verify_mode = ssl.CERT_NONE
                ctx_client.set_alpn_protocols(["http/1.1"])
                s_ssl = ctx_client.wrap_socket(server_socket, server_hostname=url_host)

            except Exception as e:
                print(f"[!] Connection failed {url_host}", e)
                return

            inputs = [c_ssl, s_ssl]

            while inputs:
                readable, _, _ = select.select(inputs, [], [])
                
                for sock in readable:
                    if sock is c_ssl:
                        headers, body = read_http_message(c_ssl)
                        if not headers:
                            print("[+] Closing connection with client")
                            s_ssl.close()
                            c_ssl.close()
                            return

                        if b"Accept-Encoding" in headers:
                            headers = re.sub(b"Accept-Encoding: .*?\r\n", b"Accept-Encoding: identity\r\n", headers, flags=re.IGNORECASE)
                        
                        full_package = headers + body
                        print(f"[!!!!!unencrypted client] {headers[:100]}...")

                        s_ssl.sendall(full_package)

                    elif sock is s_ssl:
                        headers, body = read_http_message(s_ssl)
                        if not headers:
                            print("[+] Closing connection with server")
                            c_ssl.close()
                            s_ssl.close()
                            return

                        if b"101 Switching Protocols" in headers or b"HTTP/1.1 101" in headers:
                            print(f"[+] WebSocket connection established with {url_host}")
                            s_ssl.sendall(headers + body)
                            c_ssl.sendall(headers + body)
                            tunnel_sockets(c_ssl, s_ssl)
                            c_ssl.close()
                            s_ssl.close()
                            return

                        headers = ICE_s(headers)
                        full_package = headers + body

                        print(f"[!!!!!unencrypted server] {headers[:100]}...")
                        c_ssl.sendall(full_package)

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
    petition = brute_data.decode('utf-8', errors='ignore')
    petition_lines = petition.split('\r\n')
    if not petition_lines or not petition_lines[0]:
        return None, None
    petition_line_one = petition_lines[0]
    try:
        complete_url = petition_line_one.split(' ')
        if len(complete_url) < 2:
            return None, None
        method = complete_url[0]
    except Exception:
        print("[!] No such valid petition D:")
        return None, None
    
    return method, complete_url

def connect_or_else(method, complete_url, brute_data=b""):
    if len(complete_url) < 2:
        return None, 80

    url_target = complete_url[1]
    if method == 'CONNECT':
        host_part = url_target.split(':')[0]
        port = 443
        if ':' in url_target:
            try:
                port = int(url_target.split(':')[1])
            except ValueError:
                port = 443
        return host_part, port
    else:
        parsed = urlparse(url_target)
        urlparsed = parsed.hostname
        url_port = parsed.port

        if not urlparsed:
            # Fallback to Host header in brute_data
            host_match = re.search(br"Host:\s*([^\r\n:]+)(?::(\d+))?", brute_data, re.IGNORECASE)
            if host_match:
                urlparsed = host_match.group(1).decode('utf-8', errors='ignore')
                if host_match.group(2):
                    url_port = int(host_match.group(2).decode())

        if url_port is None:
            url_port = 80
        return urlparsed, url_port 

cert_lock = threading.Lock()

def inyect_ice(brute_package):
    try:
        with open("ice_module.js", "r", encoding="utf-8") as f:
            ice_js = f.read()
    except FileNotFoundError:
        return brute_package

    ice_payload = f"<script>\n{ice_js}\nif (typeof Module !== 'undefined') {{ Module.onRuntimeInitialized = function() {{ if (typeof Module.ccall === 'function') Module.ccall('deploy_defense', null, [], []); }}; }}\n</script>"

    ice_payload_bytes = ice_payload.encode('utf-8')

    brute_package = re.sub(
        b"(<head\\b[^>]*>)", 
        lambda match: match.group(1) + ice_payload_bytes, 
        brute_package,
        count=1, 
        flags=re.IGNORECASE
    )


    if b"\r\n\r\n" in brute_package:
            headers, body = brute_package.split(b"\r\n\r\n", 1)
            body_length = len(body)

            if re.search(b"Content-Length: \\d+", headers, re.IGNORECASE):
                headers = re.sub(b"Content-Length: \\d+", f"Content-Length: {body_length}".encode(), headers, count=1, flags=re.IGNORECASE)
            else:
                headers += f"Content-Length: {body_length}\r\n".encode()

            brute_package = headers + b"\r\n\r\n" + body

    return brute_package

def ICE_s(server_responce):
    if re.search(b"Content-Security-Policy", server_responce, re.IGNORECASE):
        server_responce = re.sub(b"Content-Security-Policy: [^\r\n]+\r\n", b"", server_responce, count=1, flags=re.IGNORECASE)
        print("[!] Black Wall security bypass (CSP removed)!!")
    return server_responce

class hub_handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path in ("/", "/black_wall_hub.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                with open('black_wall_hub.html', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b"<h1>Error: black_wall_hub.html not found :C</h1>")

        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            with stats_lock:
                data_hub = {
                    "stats": proxy_stats,
                    "blocked_domains": list(blocked_domains),
                    "logs": conection_logs
                }
            self.wfile.write(json.dumps(data_hub).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/block':
            longitud = int(self.headers.get('Content-Length', 0))
            if longitud > 0:
                body = self.rfile.read(longitud)
                try:
                    data = json.loads(body.decode('utf-8'))
                    domain_to_bloq = data.get("domain")

                    if domain_to_bloq:
                        with stats_lock:
                            blocked_domains.add(domain_to_bloq)
                        print(f"[BLOCKED] {domain_to_bloq} was BLOCKED by user ^_^")
                except Exception as e:
                    print(f"[!] Error parsing block payload: {e}")

            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def start_hub():
    hub_server = HTTPServer(('127.0.0.1', 5000), hub_handler)
    print("\033[92m[+] CONTROL HUB ACTIVE ON >> http://127.0.0.1:5000 \033[0m")
    hub_server.serve_forever()


if __name__ == '__main__':
    try:
        threading.Thread(target=start_hub, daemon=True).start()
        listen()
    except KeyboardInterrupt:
        print("\n[Black Wall] is stopping, goodbye!")
        
        