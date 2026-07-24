Write-Host "Creando entorno virtual..."
python -m venv venv

Write-Host "Instalando dependencias..."
.\venv\Scripts\pip install --upgrade pip
.\venv\Scripts\pip install -r requirements.txt

if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Se creo .env a partir de .env.example. Completalo con tus credenciales."
}

python -c "import tkinter; print('tkinter OK', tkinter.TkVersion)"

$mysqlInstalado = Get-Command mysql -ErrorAction SilentlyContinue
if (-not $mysqlInstalado) {
    Write-Host ""
    Write-Host "MySQL no esta instalado o no esta en el PATH."
    Write-Host "Descargalo desde: https://dev.mysql.com/downloads/installer/"
}

Write-Host ""
Write-Host "Entorno listo."
Write-Host "Para activar el entorno virtual en tus proximas sesiones:"
Write-Host "  venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Para cargar la base de datos:"
Write-Host "  mysql -u root -p < base_datos\db_panaderia.sql"
