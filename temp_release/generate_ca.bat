@echo off
echo [*] Generating RSA master key of 2048 bytes...
openssl genrsa -out blackwall_ca.key 2048

echo [*] Creating Certificate of Authority...
openssl req -x509 -new -nodes -key blackwall_ca.key -sha256 -days 3650 -out blackwall_ca.crt -subj "/C=CO/O=BlackWall/CN=BlackWall Root CA" -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign"

echo [*] Criptography files created successfully
pause