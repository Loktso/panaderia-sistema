# Sistema de Gestión de Ventas - Panadería

Sistema de escritorio para controlar producción diaria, ventas, sobrantes
y ganancias de una panadería. Incluye login local, login con Google y
Facebook, y perfiles de acceso (administrador, vendedor, invitado).

## Tecnologías

- Python 3 + Tkinter (interfaz gráfica)
- MySQL (base de datos)
- bcrypt (contraseñas)
- Google OAuth / Facebook OAuth (login externo)
- matplotlib (gráficas)
- reportlab / openpyxl (reportes PDF / Excel)

## Estructura del proyecto

```
panaderia_sistema/
├── main.py
├── config.py
├── base_datos.py
├── modelos.py
├── calculadora_porcentajes.py
├── conexiones_externas.py
├── alertas.py
├── modo_offline.py
├── exportar_reportes.py
├── ventanas/
├── base_datos/db_panaderia.sql
├── requirements.txt
└── instalar_entorno.sh
```

## Instalación

### 1. Instalar Tkinter (solo Linux)
```bash
sudo apt install python3-tk python3-venv
```

### 2. Correr el instalador
```bash
bash instalar_entorno.sh
```
Esto crea el entorno virtual, instala las dependencias y genera el `.env`
a partir de `.env.example`.

### 3. Configurar credenciales
Editar `.env` con los datos de tu base de datos MySQL local.

### 4. Cargar la base de datos
```bash
mysql -u root --default-character-set=utf8mb4 -p < base_datos/db_panaderia.sql
```

### 5. Ejecutar
```bash
source venv/bin/activate
python3 main.py
```

## Justificación matemática: porcentaje compuesto

El sistema aplica el concepto de porcentaje compuesto (aumentos o
disminuciones porcentuales sucesivas) en:

- Historial de precios de productos (cada cambio de precio queda
  registrado con su porcentaje de variación)
- Descuentos sucesivos en ventas (dos descuentos aplicados en cadena,
  no sumados directamente)
- Proyecciones de ganancias y reducción de merma a lo largo del tiempo
