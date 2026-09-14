from src.web.api.esp32_receiver import bp as esp32_receiver
from src.web.controllers.modulo_entrenamiento import bp as entrenamiento


def register(app):
    app.register_blueprint(esp32_receiver)
    app.register_blueprint(entrenamiento)