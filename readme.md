# LabKits - Sistema de Solicitudes de Kits de Laboratorio

## Propósito
Dos microservicios (Catálogo y Solicitudes) que permiten consultar kits disponibles
y registrar solicitudes de préstamo. Proyecto didáctico del programa ADSO - SENA.

## Archivos
- `catalogo.py` - Servicio de consulta de kits (puerto 8001)
- `solicitudes.py` - Servicio de gestión de solicitudes (puerto 8002)
- `test_servicios.py` - Suite de 12 pruebas automáticas
- `contar.py` - Script auxiliar para contar filas en solicitudes.db
- `requirements.txt` - Dependencias del proyecto

## Instalación
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt

## Variables de entorno
- `API_TOKEN` (obligatoria): clave de al menos 16 caracteres para proteger Solicitudes
- `CATALOGO_URL` (opcional): dirección de Catálogo. Por defecto: http://127.0.0.1:8001

## Comandos de arranque

### Terminal 1 - Catálogo
```bash
python -m uvicorn catalogo:app --port 8001

## solicitud- terminal 2
$env:API_TOKEN="clave-local-de-practica-2026"
python -m uvicorn solicitudes:app --port 8002

##verificacion
Catálogo: http://127.0.0.1:8001/salud → {"estado":"ok"}
Solicitudes: http://127.0.0.1:8002/salud → {"estado":"ok"}
Documentación interactiva: /docs en cada puerto

##pruebas
python -m pytest -q
Se esperan 12 pruebas aprobadas.

##limitaciones
No hay idempotencia: cada POST válido crea una nueva solicitud
No hay reserva de stock físico
No hay transacciones distribuidas entre servicios
La clave API_TOKEN es compartida, no identifica usuarios
/salud solo verifica que el proceso responde, no sus dependencias