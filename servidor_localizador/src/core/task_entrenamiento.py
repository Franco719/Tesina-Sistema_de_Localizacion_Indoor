from celery import shared_task


@shared_task
def ejecutar_entrenamiento(id_entrenamiento: int):
    from src.web.services.entrenamiento_red import ServicioEntrenamiento
    
    servicio = ServicioEntrenamiento()
    servicio.entrenar(id_entrenamiento)