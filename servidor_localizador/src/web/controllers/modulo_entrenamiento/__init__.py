from flask import current_app, flash
from flask import request, jsonify, Blueprint, render_template, redirect, url_for
from src.core.database.redis_client import db as redis_db
from src.core.filters.filter_manager import filtro_prediccion
from src.core.inference.gestor_modelos import GestorModelos
from src.web.services.red_service import RedNeuronalService
from src.core.models.entrenamiento_red import Entrenamiento
from src.web.schemas.modulo_entrenamiento import pre_entrenamiento_schema, cambio_nombre_schema
from marshmallow import ValidationError


bp = Blueprint("modulo_entrenamiento", __name__, url_prefix="/modulo_entrenamiento")


@bp.route('/entrenamiento', methods=['GET'])
def vista_entrenamiento():
    """Obtiene la vista de pre-entrenamiento por defecto para entrenar una red neuronal en base a un metodo de filtrado que se ingrese"""
    
    entrenamientos = Entrenamiento.get_entrenamientos()

    return render_template("entrenamiento.html", entrenamientos=entrenamientos)


@bp.route('/entrenar', methods=['POST'])
def entrenar():
    try:
        data_validada = pre_entrenamiento_schema.load(request.form)
    except ValidationError as err:
        for mensajes in err.messages.values():
            for mensaje in mensajes:
                flash(mensaje, "error")

        return redirect(url_for("modulo_entrenamiento.vista_entrenamiento"))

    metodo = data_validada["metodo_filtrado"]
    nombre = data_validada["nombre_entrenamiento"]

    try:
        RedNeuronalService().iniciar_entrenamiento(metodo, nombre)
    except Exception:
        current_app.logger.exception(
            "No se pudo iniciar el entrenamiento."
        )
        flash("No se pudo iniciar el entrenamiento. Revisá los registros del servidor.", "error")
        return redirect(url_for("modulo_entrenamiento.vista_entrenamiento"))

    flash("El entrenamiento fue enviado a la cola de ejecución.", "success")

    return redirect(url_for("modulo_entrenamiento.vista_entrenamiento"))


@bp.route('/eliminar_entrenamiento/<id_entrenamiento>', methods=['POST'])
def eliminar_entrenamiento(id_entrenamiento: int):
    
    entrenamiento = Entrenamiento.get_entrenamiento_by_id(id_entrenamiento)
    
    if entrenamiento is None:
        flash("No se encontró el entrenamiento que intentás eliminar.", "error")
        return redirect(url_for("modulo_entrenamiento.vista_entrenamiento"))

    Entrenamiento.eliminar_entrenamiento(id_entrenamiento)

    flash("El entrenamiento fue eliminado.", "success")

    return redirect(url_for("modulo_entrenamiento.vista_entrenamiento"))


@bp.route('/cambiar_nombre_entrenamiento/<id_entrenamiento>', methods=['POST'])
def cambiar_nombre(id_entrenamiento: int):
    try:
        data_validada = cambio_nombre_schema.load(request.form)
    except ValidationError as err:
        for mensajes in err.messages.values():
            for mensaje in mensajes:
                flash(mensaje, "error")
        
        return redirect(url_for("modulo_entrenamiento.vista_entrenamiento"))

    entrenamiento = Entrenamiento.get_entrenamiento_by_id(
        id_entrenamiento
    )

    if entrenamiento is None:
        flash("No se encontró el entrenamiento solicitado.", "error")
        return redirect(url_for("modulo_entrenamiento.vista_entrenamiento"))

    entrenamiento.actualizar_entrenamiento(
        nombre=data_validada["nuevo_nombre"]
    )

    flash("El nombre del entrenamiento se actualizó correctamente.", "success")

    return redirect(url_for("modulo_entrenamiento.vista_entrenamiento"))