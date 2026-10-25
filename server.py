"""Simple HTTPS dev server for the Food Barcode Scanner web app.

Camera access on a phone requires a secure context (HTTPS or localhost).
This server generates a self-signed certificate and serves the app over HTTPS
so you can open it on your phone via https://<your-pc-ip>:8443

Usage:
    python server.py            # serves current dir on 0.0.0.0:8443
    python server.py 9000       # custom port
"""
import http.server
import os
import socket
import ssl
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import datetime

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8443
CERT_DIR = Path(__file__).parent / ".certs"
CERT_FILE = CERT_DIR / "cert.pem"
KEY_FILE = CERT_DIR / "key.pem"


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def ensure_cert():
    CERT_DIR.mkdir(exist_ok=True)
    if CERT_FILE.exists() and KEY_FILE.exists():
        return
    print("Generating self-signed certificate...")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ip = get_lan_ip()
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, ip),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Food Barcode Scanner"),
    ])
    san = x509.SubjectAlternativeName([
        x509.DNSName("localhost"),
        x509.IPAddress(__import__("ipaddress").ip_address("127.0.0.1")),
        x509.IPAddress(__import__("ipaddress").ip_address(ip)),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
        .add_extension(san, critical=False)
        .sign(key, hashes.SHA256())
    )
    KEY_FILE.write_bytes(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    CERT_FILE.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    print(f"Certificate created for {ip} (and localhost)")


def main():
    ensure_cert()
    os.chdir(Path(__file__).parent)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("0.0.0.0", PORT), handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(str(CERT_FILE), str(KEY_FILE))
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    ip = get_lan_ip()
    print(f"\nFood Barcode Scanner running:")
    print(f"  Local:   https://localhost:{PORT}")
    print(f"  Phone:   https://{ip}:{PORT}")
    print(f"\nOpen the 'Phone' URL on your phone (same Wi-Fi).")
    print("You'll get a certificate warning - tap 'Advanced' -> 'Proceed' (self-signed).")
    print("Press Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
