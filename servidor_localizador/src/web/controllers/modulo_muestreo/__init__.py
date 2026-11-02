from flask import request, jsonify, Blueprint, render_template, redirect, url_for
#from src.core.filters.filter_factory import crear_filtro
#from src.core.database import db as pg_db
from src.core.database.redis_client import db as redis_db
from src.core.models.muestra_wifi import MuestraWifi
#from src.core.inference.modelo_red import ModeloNN
#from src.core.inference.gestor_modelos import GestorModelos
from src.web.schemas.modulo_muestreo import pre_muestreo_schema
from marshmallow import ValidationError
from src.core.filters.filter_manager import filtro_muestreo
import pandas as pd
#from servidor_localizador.src.core.task_entrenamiento import probar_celery


bp = Blueprint("modulo_muestreo", __name__, url_prefix="/modulo_muestreo")


@bp.route('/pre-muestreo', methods=['GET'])
def vista_muestreo():
    """Obtiene la vista de pre-muestreo por defecto para ingresar la sala en la que se realiza el muestreo"""
    filtro_muestreo.finalizar()
    redis_db.delete("Sala_Actual")
    
    """gestor = GestorModelos()
    #gestor.entrenar()
    
    artefacto = gestor.cargar(1)
    print("Modelo cargado correctamente.")
    print("Claves del artefacto:", artefacto.keys())
    print("BSSID utilizados:", artefacto["bssids"])
    print("Método de filtrado:", artefacto["metodo_filtrado"])
    print("Configuración:", artefacto["configuracion"])
    
    resultado = gestor.probar_prediccion(1)

    print("Sala predicha:", resultado["sala_predicha"])
    print("Escaneo utilizado:", resultado["fecha_escaneo"])
    print("Método:", resultado["metodo_filtrado"])
    
    
    resultado = probar_celery.delay()
    
    print("ID de la tarea:", resultado.id)
    print("Estado inicial:", resultado.status)
    print("¿Terminó?:", resultado.ready())"""
    

    return render_template("muestreo.html")

@bp.route('/muestreo', methods=['POST'])
def iniciar_muestreo():
    """Inicia una sesión de muestreo."""

    try:
        data_validada = pre_muestreo_schema.load(request.form)
    except ValidationError as err:
        return jsonify({
            "status": "error",
            "errors": err.messages
        }), 422

    sala = data_validada["nombre_sala"]
    metodo = data_validada["metodo_filtrado"]
    nodo_id = data_validada["nodo_id"]
    ventana = data_validada.get("ventana")
    
    #filtro_muestreo.iniciar(metodo, ventana)

    if sala:

        redis_db.set("Sala_Actual", sala, ex=300)
        redis_db.set("Metodo_Filtrado", metodo, ex=300)

        if ventana is not None:
            redis_db.set("Ventana", ventana, ex=300)

        """filtro_actual = crear_filtro(
            metodo,
            ventana
        )"""
        filtro_muestreo.iniciar(metodo, nodo_id, sala, ventana)

    return render_template(
        "muestreo.html",
        sala_activa=sala
    )


@bp.route('/muestreo/redes_vivas', methods=['GET'])
def obtener_redes_vivas():
    """Obtiene las últimas 10 redes guardadas en la Base de Datos para la sala en muestreo"""
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


@bp.route('/muestreo/salir', methods=['POST'])
def salir_muestreo():
    """Permite detener el muestreo ante una salida abrupta de la página"""
    redis_db.delete("Sala_Actual")
    filtro_muestreo.finalizar()
    return "", 204
