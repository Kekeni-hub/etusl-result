param(
    [Parameter(Mandatory=$true)]
    [string]$TokenFile = "token.txt",
    [string]$Url = "http://localhost:8000/api/token-rotate/",
    [string]$SaveTo = "token.txt"
)

if (-Not (Test-Path $TokenFile)) {
    Write-Error "Token file $TokenFile not found. Obtain a token first with get_token.ps1."
    exit 1
}

$oldToken = Get-Content $TokenFile -Raw
$headers = @{ Authorization = "Token $oldToken" }
try {
    $response = Invoke-RestMethod -Uri $Url -Method Post -Headers $headers
    if ($response.token) {
        $response.token | Out-File -FilePath $SaveTo -Encoding ascii
        Write-Host "Rotated token saved to $SaveTo"
    } else {
        Write-Error "No token in rotate response: $($response | ConvertTo-Json -Depth 2)"
    }
} catch {
    Write-Error "Token rotate request failed: $_"
}
