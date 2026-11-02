from src.web import create_app

flask_app = create_app()
celery = flask_app.extensions["celery"]

# Como ejecutar el worker:
# poetry run celery -A celery_worker.celery worker --loglevel=info --concurrency=1
# concurrency es 1 para evitar que dos entrenamientos tomen datos simultaneamente