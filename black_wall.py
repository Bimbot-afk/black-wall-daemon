import socket
from urllib.parse import urlparse
import threading
import select, sys

HOST = '127.0.0.1'
PORT = 8080


def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_socket:
        s_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_socket.bind((HOST, PORT))
        s_socket.listen(5)
        print(f"[Black Wall] is running >:D. Listening on {HOST}:{PORT}")

        while True:
            c_socket, c_address= s_socket.accept()

            brute_data = c_socket.recv(4096)

            if not brute_data:
                continue

            method, complete_url = split_petition_data(brute_data)
            
            if method == None and complete_url == None:
                continue

            urlparsed, url_port = connect_or_else(method, complete_url)
            
            threading.Thread(target=daemon_blackwall, args=(urlparsed, brute_data, c_socket, method, urlparsed, url_port)).start()
            print(f"[+] Recived petition for site:{method} -> {urlparsed}:{url_port}")

def daemon_blackwall(urlparsed, brute_data, c_socket, method, url_host, url_port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        if method=='CONNECT':
            server_socket.connect((url_host, 443))
            c_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            inputs = [c_socket, server_socket]

            while inputs:
                readable, _, _ = select.select(inputs, [], [])
                
                for sock in readable:
                    if sock is c_socket:
                        brute_data = c_socket.recv(4096)
                        if brute_data:
                            server_socket.sendall(brute_data)
                        else:
                            print("[+] Closing conection with: ", server_socket.getpeername())
                            server_socket.close()
                            break

                    elif sock is server_socket:
                        server_responce = server_socket.recv(4096)
                        if server_responce:
                            c_socket.sendall(server_responce)
                        else:
                            print("[+] Closing conection with: ", c_socket.getpeername())
                            c_socket.close()
                            break
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


if __name__ == '__main__':
    try:
        listen()
    except KeyboardInterrupt:
        print("[Black Wall] is stopping, goodbye!") 

