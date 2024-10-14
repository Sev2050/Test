import subprocess
import pymongo
from datetime import datetime

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["certificate_management"]
cert_collection = db["certificates"]

def update_certificate_record(thumbprint, action):
    cert_collection.update_one(
        {"thumbprint": thumbprint},
        {"$set": {
            "last_updated": datetime.now(),
            "status": f"{action} initiated"
        }}
    )

def renew_certificate(thumbprint):
    command = f'powershell.exe -ExecutionPolicy Bypass -File RenewRequest.ps1 -Action Renew -CertificateThumbprint {thumbprint}'
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        update_certificate_record(thumbprint, "Renew")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

def request_new_certificate(thumbprint):
    command = f'powershell.exe -ExecutionPolicy Bypass -File RenewRequest.ps1 -Action RequestNew -CertificateThumbprint {thumbprint}'
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        update_certificate_record(thumbprint, "RequestNew")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

if __name__ == "__main__":
    # Get all certificates that need renewal
    certificates = cert_collection.find({"renew": True})
    for cert in certificates:
        if cert["action"] == "Renew":
            renew_certificate(cert["thumbprint"])
        elif cert["action"] == "RequestNew":
            request_new_certificate(cert["thumbprint"])

