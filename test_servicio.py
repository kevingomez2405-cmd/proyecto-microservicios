import os
import tempfile
from pathlib import Path
import httpx
import pytest
from fastapi.testclient import TestClient

TEMP = tempfile.TemporaryDirectory()
os.environ['CATALOGO_DB'] = str(Path(TEMP.name) / 'c.db')
os.environ['SOLICITUDES_DB'] = str(Path(TEMP.name) / 's.db')
os.environ['API_TOKEN'] = 'token-ficticio-solo-pruebas'

import catalogo
import solicitudes

c = TestClient(catalogo.app)
s = TestClient(solicitudes.app)
H = {'X-API-Key': os.environ['API_TOKEN']}

@pytest.fixture(autouse=True)
def conectar(monkeypatch):
    monkeypatch.setattr(solicitudes.httpx, 'get',
        lambda url, **kw: c.get('/kits/' + url.rsplit('/', 1)[1]))

def test_catalogo():
    assert c.get('/kits/1').json()['nombre'] == 'Kit de sensores'
    assert c.get('/kits/999').status_code == 404

def test_crear_y_consultar():
    r = s.post('/solicitudes', headers=H,
               json={'kit_id': 1, 'cantidad': 2})
    assert r.status_code == 201
    q = s.get('/solicitudes/' + r.json()['id'], headers=H)
    assert q.json() == r.json()

@pytest.mark.parametrize('cantidad', [0, 6, '2', True])
def test_cantidad_invalida(cantidad):
    r = s.post('/solicitudes', headers=H,
               json={'kit_id': 1, 'cantidad': cantidad})
    assert r.status_code == 422

@pytest.mark.parametrize('cantidad', [1, 5])
def test_limites_validos(cantidad):
    assert s.post('/solicitudes', headers=H,
                  json={'kit_id': 1, 'cantidad': cantidad}).status_code == 201

def test_sin_permiso():
    assert s.post('/solicitudes', json={}).status_code == 401

def test_kit_inexistente():
    assert s.post('/solicitudes', headers=H,
                  json={'kit_id': 999, 'cantidad': 1}).status_code == 404

def test_fallo_red(monkeypatch):
    def fallar(*args, **kwargs):
        raise httpx.ConnectError('fallo simulado')
    monkeypatch.setattr(solicitudes.httpx, 'get', fallar)
    assert s.post('/solicitudes', headers=H,
                  json={'kit_id': 1, 'cantidad': 1}).status_code == 503

def test_contrato_roto(monkeypatch):
    monkeypatch.setattr(solicitudes.httpx, 'get',
        lambda *a, **k: httpx.Response(200, json={'id': 7}))
    assert s.post('/solicitudes', headers=H,
                  json={'kit_id': 1, 'cantidad': 1}).status_code == 503