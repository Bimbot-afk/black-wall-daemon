@echo off
cd /d "%~dp0"
echo [*] Buscando OpenSSL...
where openssl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] OpenSSL no esta instalado o no esta en el PATH.
    echo Por favor, lee el archivo README.md para ver las opciones y generar el certificado con mkcert o instalar OpenSSL.
    pause
    exit /b 1
)

echo [*] Generating RSA master key of 2048 bytes...
openssl genrsa -out blackwall_ca.key 2048

echo [*] Creating Certificate of Authority...
openssl req -x509 -new -nodes -key blackwall_ca.key -sha256 -days 3650 -out blackwall_ca.crt -subj "/C=CO/O=BlackWall/CN=BlackWall Root CA" -addext "basicConstraints=critical,CA:TRUE" -addext "keyUsage=critical,keyCertSign,cRLSign"

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Hubo un problema al generar los certificados. Lee el README.md para alternativas.
) else (
    echo [*] Criptography files created successfully
)

pause