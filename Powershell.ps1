param (
    [string]$Action,
    [string]$CertificateThumbprint,
    [string]$CertificateTemplate = "WebServer",
    [string]$CertStoreLocation = "Cert:\LocalMachine\My"
)

if ($Action -eq "Renew") {
    # Renew the certificate with the given thumbprint
    $cert = Get-ChildItem -Path $CertStoreLocation | Where-Object Thumbprint -eq $CertificateThumbprint

    if ($cert) {
        Write-Output "Renewing certificate with Thumbprint: $CertificateThumbprint"
        certreq -submit -attrib "RenewalCert=$($cert.Thumbprint)" -config "CA_SERVER\CA_NAME"
    } else {
        Write-Error "Certificate with Thumbprint $CertificateThumbprint not found."
    }
} elseif ($Action -eq "RequestNew") {
    # Request a new certificate with the same subject and SANs as the existing one
    $cert = Get-ChildItem -Path $CertStoreLocation | Where-Object Thumbprint -eq $CertificateThumbprint

    if ($cert) {
        $csrFile = "C:\Temp\certrequest.req"
        $infFile = "C:\Temp\certrequest.inf"
        $outputCertFile = "C:\Temp\newcert.cer"

        # Prepare the .inf file for certificate request
        @"
[Version]
Signature="$Windows NT$"

[NewRequest]
Subject = "$($cert.Subject)"
KeySpec = 1
KeyLength = 2048
Exportable = TRUE
MachineKeySet = TRUE
SMIME = FALSE
PrivateKeyArchive = FALSE
UserProtected = FALSE
UseExistingKeySet = FALSE
ProviderName = "Microsoft RSA SChannel Cryptographic Provider"
ProviderType = 12
RequestType = PKCS10
KeyUsage = 0xa0

[Extensions]
2.5.29.17 = "{text}"
_continue_ = "dns=$($cert.Subject)";dns=$($cert.SubjectAlternativeName)"

[RequestAttributes]
CertificateTemplate = "$CertificateTemplate"
"@ | Set-Content -Path $infFile

        # Generate CSR
        certreq -new $infFile $csrFile

        # Submit request to CA
        certreq -submit -config "CA_SERVER\CA_NAME" $csrFile $outputCertFile

        Write-Output "New certificate requested with same Subject and SANs."
    } else {
        Write-Error "Certificate with Thumbprint $CertificateThumbprint not found."
    }
} else {
    Write-Error "Invalid Action specified. Use 'Renew' or 'RequestNew'."
}
