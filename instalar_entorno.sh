#!/bin/bash

SISTEMA_OPERATIVO="$(uname -s)"

echo "Sistema detectado: $SISTEMA_OPERATIVO"
echo ""

if [ "$SISTEMA_OPERATIVO" = "Darwin" ]; then

    if ! command -v brew &> /dev/null; then
        echo "Homebrew no está instalado."
        echo "Instálalo desde https://brew.sh antes de continuar y vuelve a correr este script."
        exit 1
    fi

    if ! python3 -c "import tkinter" &> /dev/null; then
        brew install python-tk
    fi

    if ! command -v mysql &> /dev/null; then
        echo "MySQL no está instalado. Instalando con Homebrew..."
        brew install mysql
        brew services start mysql
    fi

elif [ "$SISTEMA_OPERATIVO" = "Linux" ]; then

    sudo apt update
    sudo apt install -y python3-tk python3-venv

    if ! command -v mysql &> /dev/null; then
        echo "MySQL no está instalado. Instalando..."
        sudo apt install -y mysql-server
        sudo systemctl start mysql
        sudo systemctl enable mysql
    fi

else
    echo "Sistema operativo no reconocido: $SISTEMA_OPERATIVO"
    exit 1
fi

echo ""
echo "Creando entorno virtual..."
python3 -m venv venv

echo "Instalando dependencias..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Se creó .env a partir de .env.example. Complétalo con tus credenciales."
fi

echo ""
python3 -c "import tkinter; print('tkinter OK', tkinter.TkVersion)"

echo ""
echo "Entorno listo."
echo "Para activar el entorno virtual en tus próximas sesiones:"
echo "  source venv/bin/activate"
echo ""
echo "Para cargar la base de datos:"
echo "  mysql -u root --default-character-set=utf8mb4 -p < base_datos/db_panaderia.sql"
