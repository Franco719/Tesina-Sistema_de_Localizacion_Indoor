from flask import request, jsonify, Blueprint, render_template, redirect, url_for
from src.core.database.redis_client import guardar_lectura_cruda, db as redis_db
from src.core.database import db
from src.core.models.muestra_wifi import MuestraWifi
from src.web.schemas.esp32_receiver import wifi_records_schema
from marshmallow import ValidationError
from dotenv import load_dotenv
import os
from datetime import datetime

bp = Blueprint("api", __name__, url_prefix="/api")
load_dotenv()

@bp.route('/localizar', methods=['POST'])
def recibir_datos_esp32():
    """Recibe los datos de Wi-Fi que percibe y envía la placa ESP32, y los guarda en Redis (si no se está tomando muestras
    para entrenamiento) o en la Base de Datos (si se está tomando muestras para entrenamiento)"""
    
    token_recibido = request.headers.get("API-Key")
    if token_recibido != os.environ.get("SECRET_KEY"):
        print("¡Intento de acceso no autorizado bloqueado!")
        return jsonify({"status": "error", "message": "No autorizado"}), 401
    
    if not request.is_json:
        return jsonify({"status": "error", "message": "Se esperaba formato JSON"}), 400

    try:
        data_validada = wifi_records_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"status": "error", "errors": err.messages}), 422
    
    sala = redis_db.get("Sala_Actual")
    nodo_id = "01" # Por ahora hardcodeado, luego si hay más de uno hay que modificar en el esp32 para que mande el id
    
    if not sala:
        # Modo producción: Solo guarda la lectura instantánea de Redis para localizar sin una nueva lectura
        guardar_lectura_cruda(nodo_id, data_validada)
        print(f"📡 [Nodo {nodo_id}] Guardadas {len(data_validada)} redes validadas en Redis.")
    
    else:
        # Modo entrenamiento: Recorre la lista validada e iserta en la Base de Datos
        print(f"📥 [ENTRENAMIENTO - {sala}] Guardando ráfaga en Base de Datos Local.")
        for red in data_validada:
            MuestraWifi.crear_muestra(
                nodo_id=nodo_id,
                sala=sala,
                ssid=red.get("ssid"),
                rssi_puro=red.get("rssi"),
                #fecha_registro=datetime.now()
            )
            
        # El commit lo hago acá para no hacer uno por cada muestra guardada.
        db.session.commit()
    
    return jsonify({"status": "success", "message": "Lectura almacenada con éxito"}), 200