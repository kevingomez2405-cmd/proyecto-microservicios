import os 
import sqlite3 
from contextlib import closing
from fastapi import FastAPI, HTTPException

app = FastAPI(title='Catalogo de kits')
DB = os.getenv('CATALOGO_DB', 'catalogo.db') 
with closing(sqlite3.connect(DB)) as con: 
 con.execute('CREATE TABLE IF NOT EXISTS kits (' 
 'id INTEGER PRIMARY KEY, nombre TEXT NOT NULL)') 
 con.execute('INSERT OR IGNORE INTO kits VALUES (?, ?)', 
 (1, 'Kit de sensores')) 
 con.commit() 

@app.get('/salud')
def salud():
    return {'estado': 'ok'}
@app.get('/kits/{kit_id}')
def obtener_kit(kit_id: int): 
 with closing(sqlite3.connect(DB)) as con: 
  fila = con.execute('SELECT id, nombre FROM kits WHERE id=?', 
 (kit_id,)).fetchone() 
 if fila is None: 
  raise HTTPException(404, 'Kit inexistente') 
 return {'id': fila[0], 'nombre': fila[1]} 

