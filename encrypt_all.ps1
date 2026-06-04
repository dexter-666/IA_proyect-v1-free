$files = Get-ChildItem -Path "src_clean" -Recurse -Filter "*.py" | Where-Object { $_.Name -ne "beta_config.py" -and $_.Name -ne "sitecustomize.py" }
foreach ($file in $files) {
    Write-Host "Compilando $($file.FullName) a C..."
    & ".\.venv\Scripts\python.exe" -m nuitka --module $file.FullName --disable-plugin=tk-inter --mingw64 --remove-output
    if ($LASTEXITCODE -eq 0) {
        Remove-Item $file.FullName -Force
    }
}
Write-Host "¡Toda la encriptación C finalizada!"
