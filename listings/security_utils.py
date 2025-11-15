# security_utils.py
import subprocess

def scan_image_for_malware(file):
    """
    Scan uploaded image using ClamAV or fallback.
    """

    # --------- ClamAV Scan ----------
    try:
        process = subprocess.run(
            ["clamscan", "-"],
            input=file.read(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        file.seek(0)

        if "OK" in process.stdout.decode():
            return True
        else:
            return "Malicious content detected!"
    except Exception:
        pass

    # --------- Fallback basic scan ----------
    # Check for suspicious file headers
    header = file.read(32)
    file.seek(0)

    if b"MZ" in header or b"PK" in header:
        return "File looks suspicious."

    return True
