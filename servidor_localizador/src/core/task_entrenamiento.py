from celery import shared_task


@shared_task
def ejecutar_entrenamiento(id_entrenamiento: int):
    from servidor_localizador.src.web.services.red_service import RedNeuronalService
    
    servicio = RedNeuronalService()
    servicio.entrenar_red(id_entrenamiento)