import os
import shutil
import subprocess
from pathlib import Path


def generate_cert(cert_file: str, key_file: str) -> None:
    subprocess.run(
        [
            "openssl",
            "req",
            "-x509",
            "-nodes",
            "-days",
            "365",
            "-newkey",
            "rsa:3072",
            "-keyout",
            key_file,
            "-out",
            cert_file,
            "-subj",
            "/C=US/ST=Any/L=Any/O=MedPerf/CN=127.0.0.1",
            "-addext",
            "subjectAltName=DNS:localhost,IP:127.0.0.1",
        ],
        check=True,
    )

    # Also trusted by the medperf CLI's local/testauth profiles
    medperf_dev_dir = Path.home() / ".medperf_dev"
    os.makedirs(medperf_dev_dir, exist_ok=True)
    shutil.copy(cert_file, medperf_dev_dir / "cert.crt")
