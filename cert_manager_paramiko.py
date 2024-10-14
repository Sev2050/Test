import paramiko
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

def execute_powershell_on_windows(server, username, password, action, thumbprint):
    command = f"powershell.exe -ExecutionPolicy Bypass -File C:\\Scripts\\RenewRequest.ps1 -Action {action} -CertificateThumbprint {thumbprint}"

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, username=username, password=password)

        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode())
        error = stderr.read().decode()
        if error:
            print(f"Error: {error}")
        else:
            update_certificate_record(thumbprint, action)

        client.close()

    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    windows_server = "your_windows_server_ip"
    windows_username = "your_username"
    windows_password = "your_password"

    # Get all certificates that need renewal
    certificates = cert_collection.find({"renew": True})
    for cert in certificates:
        if cert["action"] == "Renew":
            execute_powershell_on_windows(windows_server, windows_username, windows_password, "Renew", cert["thumbprint"])
        elif cert["action"] == "RequestNew":
            execute_powershell_on_windows(windows_server, windows_username, windows_password, "RequestNew", cert["thumbprint"])
