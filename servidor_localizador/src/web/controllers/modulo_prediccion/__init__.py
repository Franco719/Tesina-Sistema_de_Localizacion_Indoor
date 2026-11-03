from flask import request, jsonify, Blueprint, render_template, redirect, url_for
from src.web.services.red_service import RedNeuronalService


bp = Blueprint("modulo_prediccion", __name__, url_prefix="/modulo_prediccion")


@bp.route('/', methods=['GET'])
def vista_prediccion():
    
    return render_template("prediccion.html")
    
    
@bp.route("/predecir_posicion", methods=["POST"])
def predecir():

    red_service = RedNeuronalService()
    prediccion = red_service.predecir_posicion(1)

    if not prediccion["exito_prediccion"]:
        return render_template(
            "prediccion.html",
            error=prediccion["error"]
        )

    return render_template(
        "prediccion.html",
        prediccion=prediccion
    )