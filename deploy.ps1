param(
    [string]$msg = "auto update"
)

git add .

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "No hay cambios para subir."
    exit 0
}

git commit -m "$msg"
git push origin main