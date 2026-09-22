from flask import request, jsonify, Blueprint, render_template, redirect, url_for
from src.core.database import db as pg_db
from src.core.database.redis_client import db as redis_db
from src.core.models.muestra_wifi import MuestraWifi


bp = Blueprint("modulo_entrenamiento", __name__, url_prefix="/modulo_entrenamiento")


@bp.route('/pre-entrenamiento', methods=['GET'])
def vista_entrenamiento():
    """Obtiene la vista de pre-entrenamiento por defecto para ingresar la sala en la que se realiza el entrenamiento"""
    redis_db.delete("Sala_Actual")

    return render_template("entrenamiento.html")

@bp.route('/entrenamiento', methods=['POST'])
def iniciar_muestreo():
    """Obtiene la vista de entrenamiento"""
    
    nombre_sala = request.form.get("nombre_sala", "").strip()
    
    if nombre_sala:
        print(f"ANTES DE GUARDAR EN REDIS: {nombre_sala}")
        redis_db.set("Sala_Actual", nombre_sala, ex=300) # Después de 5 minutos aproximadamente, se detedrá el entrenamiento por la expiracion de la variable. Es apropósito para evitar un muestreo no deseado
        print(f"DESPUES DE GUARDAR EN REDIS: {redis_db.get("Sala_Actual")}")
    
    return render_template("entrenamiento.html", sala_activa=nombre_sala)


@bp.route('/entrenamiento/redes_vivas', methods=['GET'])
def obtener_redes_vivas():
    """Obtiene las últimas 10 redes guardadas en la Base de Datos para la sala en entrenamiento"""
    sala_actual = redis_db.get("Sala_Actual")
    
    print(f"SALA OBTENID AL ACTUALIZAR: {sala_actual}")
    
    if not sala_actual:
        return jsonify({
            "activo": False,
            "muestras": []
        })

    ultimas_muestras = MuestraWifi.query.filter_by(sala=sala_actual)\
                                        .order_by(MuestraWifi.fecha_registro.desc())\
                                        .limit(10).all()
                                        
    lista_json = [{"ssid": m.ssid, "rssi_puro": m.rssi_puro, "bssid": m.bssid} for m in ultimas_muestras]
    return jsonify({
        "activo": True,
        "muestras": lista_json
    })


@bp.route('/entrenamiento/salir', methods=['POST'])
def salir_entrenamiento():
    """Permite detener el entrenamiento ante una salida abrupta de la página"""
    redis_db.delete("Sala_Actual")
    return "", 204 