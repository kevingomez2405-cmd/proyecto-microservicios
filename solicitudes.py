import os
import secrets
import sqlite3
import logging
from contextlib import closing
from uuid import uuid4
import httpx
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field, ValidationError

DB = os.getenv('SOLICITUDES_DB', 'solicitudes.db')
CATALOGO = os.getenv('CATALOGO_URL', 'http://127.0.0.1:8001')
TOKEN = os.environ['API_TOKEN']

if len(TOKEN) < 16:
    raise RuntimeError('API_TOKEN requiere al menos 16 caracteres')

log = logging.getLogger('uvicorn.error')
app = FastAPI(title='Solicitudes de kits')

with closing(sqlite3.connect(DB)) as con:
    con.execute('CREATE TABLE IF NOT EXISTS solicitudes('
                'id TEXT PRIMARY KEY, kit_id INTEGER NOT NULL,'
                'cantidad INTEGER NOT NULL CHECK(cantidad BETWEEN 1 AND 5))')
    con.commit()

class Entrada(BaseModel):
    kit_id: int = Field(gt=0, strict=True)
    cantidad: int = Field(ge=1, le=5, strict=True)

class Kit(BaseModel):
    id: int = Field(gt=0, strict=True)
    nombre: str

def autorizar(x_api_key: str = Header(default='')):
    if not secrets.compare_digest(x_api_key, TOKEN):
        raise HTTPException(401, 'Credencial invalida')

# --- BLOQUE 2: Consultar a Catálogo ---
def consultar_kit(kit_id):
    try:
        respuesta = httpx.get(f'{CATALOGO}/kits/{kit_id}', timeout=2.0, trust_env=False)
    except httpx.RequestError:
        raise HTTPException(503, 'Catalogo no disponible')
    
    if respuesta.status_code == 404:
        raise HTTPException(404, 'Kit inexistente')
    if respuesta.status_code != 200:
        raise HTTPException(503, 'Respuesta no utilizable del catalogo')
    
    try:
        kit = Kit.model_validate(respuesta.json())
        if kit.id != kit_id:
            raise ValueError('Identificador inesperado')
    except (ValueError, ValidationError):
        raise HTTPException(503, 'Contrato del catalogo invalido')
    
    return kit

# --- BLOQUE 3: Rutas ---
@app.get('/salud')
def salud():
    return {'estado': 'ok'}

@app.post('/solicitudes', status_code=201, dependencies=[Depends(autorizar)])
def crear(entrada: Entrada):
    consultar_kit(entrada.kit_id)
    identificador = str(uuid4())
    with closing(sqlite3.connect(DB)) as con:
        with con:
            con.execute('INSERT INTO solicitudes VALUES(?,?,?)',
                        (identificador, entrada.kit_id, entrada.cantidad))
    log.info('solicitud_creada id=%s', identificador)
    return {'id': identificador, **entrada.model_dump()}

@app.get('/solicitudes/{identificador}', dependencies=[Depends(autorizar)])
def obtener(identificador: str):
    with closing(sqlite3.connect(DB)) as con:
        fila = con.execute('SELECT id, kit_id, cantidad FROM solicitudes WHERE id=?',
                           (identificador,)).fetchone()
    if fila is None:
        raise HTTPException(404, 'Solicitud inexistente')
    return dict(zip(['id', 'kit_id', 'cantidad'], fila))