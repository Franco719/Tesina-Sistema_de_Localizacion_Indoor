from src.core.database import db
from datetime import datetime
import threading
import uuid
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func


class EstadoKalman(db.Model):
    __tablename__ = 'estados_kalman'

    #id = db.Column(db.Integer, primary_key=True)
    nodo_id = db.Column(db.Integer, nullable=False, primary_key=True)
    bssid = db.Column(db.String(50), nullable=False, primary_key=True)
    sala = db.Column(db.String(50), nullable=False, primary_key=True)

    x = db.Column(db.Float, nullable=False)
    p = db.Column(db.Float, nullable=False)

    q = db.Column(db.Float, nullable=False)
    r = db.Column(db.Float, nullable=False)

    fecha_actualizacion = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )
    
    
    @classmethod
    def guardar_estado(cls, nodo_id, bssid, sala,  x, p, q, r):
        # Valores por defecto y prueba (eventualmente se pueden modificar a modo de prueba para la validacion del filtro): 
            # "x" es la estimacion actual del RSSI, como no hay ninguna cuando se crea, es None
            # "p" es la incertidumbre inicial de la estimacion, y se considera baja
            # "q" es la razon de cambio del RSSI, o ruido provocado en el proceso de filtrado, y se considera bajo 
            # "r" es el ruido de la medicion, y se considera que tiene un ruido considerable

        ejecucion = uuid.uuid4().hex[:8]

        print(
            f"[{ejecucion}] Hilo: {threading.current_thread().name} "
            f"Buscando nodo={nodo_id}, bssid={bssid}, sala={sala}"
        )

        estado = cls.query.filter_by(
            nodo_id=nodo_id,
            bssid=bssid,
            sala=sala
        ).first()

        print(f"[{ejecucion}] Resultado: {estado}")        



        sentencia = insert(cls).values(
            nodo_id=nodo_id,
            bssid=bssid,
            sala=sala,
            x=x,
            p=p,
            q=q,
            r=r
        )

        sentencia = sentencia.on_conflict_do_update(
            index_elements=["nodo_id", "bssid", "sala"],
            set_={
                "x": sentencia.excluded.x,
                "p": sentencia.excluded.p,
                "q": sentencia.excluded.q,
                "r": sentencia.excluded.r,
                "fecha_actualizacion": func.now()
            }
        )

        try:
            db.session.execute(sentencia)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Se hizo rollback: {e}")
            #raise
    
    @classmethod
    def get_estado(cls, bssid: str, nodo_id: int, sala: str):
        return cls.query.filter_by(
            nodo_id=nodo_id,
            bssid=bssid,
            sala=sala
        ).first()