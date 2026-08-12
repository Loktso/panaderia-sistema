# Sistema de Gestión de Ventas - Panadería

Sistema de escritorio para controlar producción diaria, ventas, sobrantes
y ganancias de una panadería. Incluye login local, login con Google, y
perfiles de acceso (administrador, vendedor, cliente registrado, invitado).

## Tecnologías

- Python 3 + Tkinter (interfaz gráfica)
- MySQL (base de datos, SQL puro sin ORM)
- bcrypt (contraseñas)
- Google OAuth (login externo)
- Envío de correo con Gmail (verificación de registro)
- matplotlib (gráficas)
- reportlab / openpyxl (reportes PDF / Excel)
- Pillow (imágenes de productos)

## Estructura del proyecto

```
panaderia_sistema/
├── main.py                    # punto de entrada, abre la vitrina pública
├── config.py                  # configuración cargada desde .env
├── base_datos.py              # todo el acceso a MySQL (CRUD)
├── modelos.py                 # clases: EPUsuario y sus roles, EPProducto, etc.
├── calculadora_porcentajes.py # módulo matemático central (% compuesto)
├── validaciones.py            # validación de cédula ecuatoriana y entradas numéricas
├── conexiones_externas.py     # login con Google (OAuth)
├── verificacion_correo.py     # envío del código de verificación por correo
├── exportar_reportes.py       # exportación de ventas a PDF y Excel
├── facturas.py                # generación de facturas simuladas en PDF
├── alertas.py                 # alertas automáticas de sobrante/merma
├── estilos.py                 # paleta de colores y categorías centralizadas
├── ventanas/
│   ├── login.py
│   ├── panel_admin.py
│   ├── panel_vendedor.py
│   ├── panel_invitado.py      # vitrina pública / catálogo / carrito
│   └── componentes_ui.py
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
Editar `.env` con los datos de tu base de datos MySQL, tus credenciales de
Google OAuth (opcional, para el login con Google) y tu cuenta de Gmail con
contraseña de aplicación (opcional, para el correo de verificación).

### 4. Cargar la base de datos
```bash
mysql -u root --default-character-set=utf8mb4 -p < base_datos/db_panaderia.sql
```
Esto crea las 7 tablas del sistema y carga un administrador y un vendedor
de prueba, además de 5 productos de ejemplo.

**Usuarios de prueba** (cambiar la contraseña en producción):
- Administrador: `admin@panaderia.com` / `Admin123!`
- Vendedor: `vendedor@panaderia.com` / `Vendedor123!`

### 5. Ejecutar
```bash
source venv/bin/activate
python3 main.py
```
La aplicación abre directamente en la vitrina pública (catálogo), desde
donde el administrador y el vendedor pueden iniciar sesión para acceder a
su panel.

## Roles del sistema

- **Invitado**: navega el catálogo público sin cuenta, filtra por
  categoría, busca productos y arma un carrito simulado.
- **Cliente**: se registra con verificación por correo o con Google,
  puede facturarse con sus datos (validación real de cédula ecuatoriana).
- **Vendedor**: registra la producción diaria y consulta sus propias ventas.
- **Administrador**: CRUD de usuarios y productos, reportes con gráficas,
  configuración de alertas de sobrante.

## Justificación matemática: porcentaje compuesto

El sistema aplica el concepto de porcentaje compuesto (aumentos o
disminuciones porcentuales sucesivas) en:

- Historial de precios de productos (cada cambio de precio queda
  registrado con su porcentaje de variación)
- Descuentos sucesivos en ventas (dos descuentos aplicados en cadena,
  no sumados directamente)
- Proyecciones de ganancias y reducción de merma a lo largo del tiempo