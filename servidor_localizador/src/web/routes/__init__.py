from src.web.api.esp32_receiver import bp as esp32_receiver
from src.web.controllers.modulo_muestreo import bp as muestreo
from src.web.controllers.modulo_entrenamiento import bp as entrenamiento
from src.web.controllers.modulo_prediccion import bp as prediccion


def register(app):
    app.register_blueprint(esp32_receiver)
    app.register_blueprint(muestreo)
    app.register_blueprint(entrenamiento)
    app.register_blueprint(prediccion)