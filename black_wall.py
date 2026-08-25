import socket
from urllib.parse import urlparse
import threading


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

            urlparsed, method = split_petition_data(brute_data)
            threading.Thread(target=daemon_blackwall, args=(urlparsed, brute_data, c_socket, method)).start()
            print(f"[+] Recived petition for site: {urlparsed}")

def daemon_blackwall(urlparsed, brute_data, c_socket, method):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        if method=='CONNECT':
            print(f"[Black Wall] Blocked petition {urlparsed}")
        else:
            server_socket.connect((urlparsed, 80))
            server_socket.sendall(brute_data)
            server_responce = server_socket.recv(4096)
            c_socket.sendall(server_responce)


def split_petition_data(brute_data):
    petition = brute_data.decode('utf-8', errors ='ignore')
    petition_lines = petition.split('\n')
    petition_line_one = petition_lines[0]
    complete_url = petition_line_one.split(' ')
    urlparsed=urlparse(complete_url[1]).netloc
    method=complete_url[0]
    return urlparsed, method


if __name__ == '__main__':
    try:
        listen()
    except KeyboardInterrupt:
        print("[Black Wall] is stopping, goodbye!") 

