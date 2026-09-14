from functools import wraps
from flask import session
from flask import redirect, render_template
from flask import url_for
from flask import abort
from src.core.database.redis_client import db as redis_db


def limpìar_sala_actual(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        redis_db.delete("Sala_Actual")
        return f(*args, **kwargs)
    return wrapper