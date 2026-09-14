import redis
import json
from config import REDIS_HOST, REDIS_PORT

# decode_responses=True traduce automáticamente los bytes de Redis a texto (strings) de Python
db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def guardar_lectura_cruda(nodo_id: str, datos_wifi: list):
    """Guarda en Redis el último JSON recibido desde el ESP32."""
    clave = f"nodo:{nodo_id}:crudo"
    db.set(clave, json.dumps(datos_wifi))

def obtener_lectura_cruda(nodo_id: str) -> list:
    """Recupera de Redis el último array de redes Wi-Fi guardado."""
    clave = f"nodo:{nodo_id}:crudo"
    datos = db.get(clave)
    return json.loads(datos) if datos else []
