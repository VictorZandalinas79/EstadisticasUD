# UD Atzeneta Analytics Dashboard

Panel de análisis deportivo para el equipo UD Atzeneta, incluyendo estadísticas de rendimiento y seguimiento médico.

## Características

- 🔐 **Sistema de autenticación** completo con login y logout
- 📊 **Dashboard de rendimiento** del equipo con evolución de KPIs
- 🏥 **Área médica** para seguimiento de lesiones y estado físico
- 📱 **Diseño responsivo** adaptado a móviles y escritorio
- 📄 **Exportación a PDF** de informes para compartir
- 🔄 **Actualización automática** de datos en tiempo real

## Estructura del Proyecto

```
ud_atzeneta_app/
│
├── app.py               # Archivo principal que inicializa la aplicación
├── config.py            # Configuración global (BD, credenciales, etc.)
├── requirements.txt     # Dependencias del proyecto
│
├── assets/              # Archivos estáticos
│   ├── escudo.png       # Logo del equipo
│   └── custom.css       # Estilos personalizados
│
├── pages/               # Módulos de cada página
│   ├── __init__.py      # Inicialización del módulo
│   ├── login.py         # Página de login
│   ├── home.py          # Página principal (dashboard)
│   ├── performance.py   # Página de análisis de rendimiento
│   └── medical.py       # Página de área médica
│
└── utils/               # Funciones auxiliares
    ├── __init__.py
    ├── database.py      # Funciones para conectar con la BD
    └── helpers.py       # Funciones de utilidad
```

## Requisitos

- Python 3.8 o superior
- MySQL (base de datos)
- Bibliotecas Python listadas en `requirements.txt`

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tu-usuario/ud-atzeneta-analytics.git
   cd ud-atzeneta-analytics
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configura la base de datos en `config.py` (las credenciales actuales son para desarrollo)

## Ejecución

Para iniciar la aplicación en modo desarrollo:

```
python app.py
```

La aplicación estará disponible en: http://127.0.0.1:8050/

## Credenciales de demostración

- Usuario: `admin`
- Contraseña: `admin`

## Personalización

Para modificar la aplicación:

- Ajusta los estilos en `assets/custom.css`
- Configura los parámetros de la aplicación en `config.py`
- Modifica las consultas a la base de datos en `utils/database.py`

## Licencia

© 2024 UD Atzeneta - Todos los derechos reservados