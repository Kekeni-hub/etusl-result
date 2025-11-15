param(
    [Parameter(Mandatory=$true)]
    [string]$Username,
    [Parameter(Mandatory=$true)]
    [string]$Password,
    [string]$SaveTo = "token.txt",
    [string]$Url = "http://localhost:8000/api-token-auth/"
)

# Request token (form-encoded)
$body = @{ username = $Username; password = $Password }
try {
    $response = Invoke-RestMethod -Uri $Url -Method Post -Body $body
    if ($response.token) {
        $response.token | Out-File -FilePath $SaveTo -Encoding ascii
        Write-Host "Token saved to $SaveTo"
        Write-Host "Use in PowerShell: Invoke-RestMethod -Uri 'http://localhost:8000/api/students/' -Method Get -Headers @{ Authorization = \"Token $($response.token)\" }"
    } else {
        Write-Error "Token not present in response: $($response | ConvertTo-Json -Depth 2)"
    }
} catch {
    Write-Error "Request failed: $_"
}
