from flask import request, jsonify, Blueprint, render_template, redirect, url_for
from src.core.filters.filter_factory import crear_filtro
from src.core.database import db as pg_db
from src.core.database.redis_client import db as redis_db
from src.core.models.muestra_wifi import MuestraWifi
from src.web.schemas.modulo_entrenamiento import pre_entrenamiento_schema
from marshmallow import ValidationError
from src.core.filters.filter_manager import filtro_manager


bp = Blueprint("modulo_entrenamiento", __name__, url_prefix="/modulo_entrenamiento")


@bp.route('/pre-entrenamiento', methods=['GET'])
def vista_entrenamiento():
    """Obtiene la vista de pre-entrenamiento por defecto para ingresar la sala en la que se realiza el entrenamiento"""
    filtro_manager.finalizar()
    redis_db.delete("Sala_Actual")

    return render_template("entrenamiento.html")

@bp.route('/entrenamiento', methods=['POST'])
def iniciar_muestreo():
    """Inicia una sesión de entrenamiento."""

    try:
        data_validada = pre_entrenamiento_schema.load(request.form)
    except ValidationError as err:
        return jsonify({
            "status": "error",
            "errors": err.messages
        }), 422

    sala = data_validada["nombre_sala"]
    metodo = data_validada["metodo_filtrado"]
    ventana = data_validada.get("ventana")
    
    filtro_manager.iniciar(metodo, ventana)

    if sala:

        redis_db.set("Sala_Actual", sala, ex=300)
        redis_db.set("Metodo_Filtrado", metodo, ex=300)

        if ventana is not None:
            redis_db.set("Ventana", ventana, ex=300)

        filtro_actual = crear_filtro(
            metodo,
            ventana
        )

    return render_template(
        "entrenamiento.html",
        sala_activa=sala
    )


@bp.route('/entrenamiento/redes_vivas', methods=['GET'])
def obtener_redes_vivas():
    """Obtiene las últimas 10 redes guardadas en la Base de Datos para la sala en entrenamiento"""
    sala_actual = redis_db.get("Sala_Actual")
    
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
    filtro_manager.finalizar()
    return "", 204