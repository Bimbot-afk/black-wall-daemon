from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os, datetime, threading

cert_lock = threading.Lock()

def certificade_forge(domain):
    os.makedirs("certs", exist_ok=True)
    clean_domain = str(domain).split(':')[0].strip() if domain else "unknown"
    cert_path = f"certs/{clean_domain}.crt"
    key_path = f"certs/{clean_domain}.key"

    with cert_lock:
        if os.path.exists(cert_path):
            return cert_path, key_path

        print(f"[*] Fake identity forge for: {clean_domain}")

        with open("blackwall_ca.crt", "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())

        with open("blackwall_ca.key", "rb") as f:
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