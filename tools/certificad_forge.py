from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os, datetime, threading, sys

cert_lock = threading.Lock()

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CA_CERT_PATH = os.path.join(BASE_DIR, "blackwall_ca.crt")
CA_KEY_PATH = os.path.join(BASE_DIR, "blackwall_ca.key")
CERTS_DIR = os.path.join(BASE_DIR, "certs")

def ensure_ca_certs():
    if os.path.exists(CA_CERT_PATH) and os.path.exists(CA_KEY_PATH):
        return

    print("[*] Generating missing Root CA certificate and key (blackwall_ca.crt, blackwall_ca.key)...")
    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CO"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "BlackWall"),
        x509.NameAttribute(NameOID.COMMON_NAME, "BlackWall Root CA"),
    ])

    now = datetime.datetime.now(datetime.timezone.utc)

    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(ca_key, hashes.SHA256())
    )

    with open(CA_KEY_PATH, "wb") as f:
        f.write(
            ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open(CA_CERT_PATH, "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    print("[+] Master Root CA certificate generated successfully.")

def certificade_forge(domain):
    os.makedirs(CERTS_DIR, exist_ok=True)
    clean_domain = str(domain).split(':')[0].strip() if domain else "unknown"
    cert_path = os.path.join(CERTS_DIR, f"{clean_domain}.crt")
    key_path = os.path.join(CERTS_DIR, f"{clean_domain}.key")

    with cert_lock:
        if os.path.exists(cert_path):
            return cert_path, key_path

        ensure_ca_certs()

        print(f"[*] Fake identity forge for: {clean_domain}")

        with open(CA_CERT_PATH, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())

        with open(CA_KEY_PATH, "rb") as f:
            ca_key = serialization.load_pem_private_key(f.read(), password=None)

        key_priv = rsa.generate_private_key(
            public_exponent = 65537,
            key_size = 2048
        )

        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, clean_domain),
        ])

        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject)
        builder = builder.issuer_name(ca_cert.subject)
        builder = builder.public_key(key_priv.public_key())
        builder = builder.serial_number(x509.random_serial_number())

        now = datetime.datetime.now(datetime.timezone.utc)
        builder = builder.not_valid_before(now)
        builder = builder.not_valid_after(now + datetime.timedelta(days=365))

        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(clean_domain)]),
            critical=False
        )

        builder = builder.add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
            critical= False
        )

        new_cert = builder.sign(ca_key, hashes.SHA256())

        with open(key_path, "wb") as f:
            f.write(key_priv.private_bytes(
                encoding=serialization.Encoding.PEM,
                format= serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(cert_path, "wb") as f:
            f.write(new_cert.public_bytes(serialization.Encoding.PEM))

        print(f"[+] SSL Certificate for {clean_domain} generated.")
        
        return cert_path, key_path