from src.core.database import db
from datetime import datetime
import pandas as pd

class MuestraWifi(db.Model):
    __tablename__ = 'muestras_wifi'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nodo_id = db.Column(db.Integer, nullable=False)
    sala = db.Column(db.String(50), nullable=False)
    bssid = db.Column(db.String(50), nullable=False)
    ssid = db.Column(db.String(32), nullable=False)
    rssi_puro = db.Column(db.Integer, nullable=False)
    rssi_filtrado = db.Column(db.Integer, nullable=True) 
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    metodo_filtrado = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return f"<Muestra {self.sala} - {self.ssid} | {self.bssid}: {self.rssi}dBm>"
    
    @classmethod
    def crear_muestra (cls, **kwargs):
        nueva_muestra = cls(**kwargs)
        
        db.session.add(nueva_muestra)
        
        # No hago commit debido a que este metodo es usado por la API cuando crea muestras, y hacer varios commits
        # seguidos no es conveniente. Por lo tanto, en la API.
        
        return nueva_muestra
    
    @classmethod
    def get_muestras_order_by_time(cls, filtro: str):
        return cls.query.filter_by(metodo_filtrado=filtro).order_by(cls.fecha_registro).all()
    
    
    @classmethod
    def obtener_ultimo_escaneo(cls, metodo_filtrado):
        muestras = cls.get_muestras_order_by_time(
            metodo_filtrado
        )

        if not muestras:
            raise ValueError("No hay muestras disponibles.")

        df = pd.DataFrame([
            {
                "fecha_registro": m.fecha_registro,
                "bssid": m.bssid,
                "rssi_filtrado": m.rssi_filtrado
            }
            for m in muestras
        ])

        # Utilizamos el mismo criterio temporal que durante el entrenamiento.
        df["fecha_escaneo"] = pd.to_datetime(
            df["fecha_registro"]
        ).dt.floor("s")

        # Identificamos el escaneo más reciente.
        fecha_ultimo_escaneo = df["fecha_escaneo"].max()

        ultimo_escaneo = df[
            df["fecha_escaneo"] == fecha_ultimo_escaneo
        ]

        # Si hay varias mediciones para un mismo BSSID,
        # utilizamos su RSSI promedio.
        return (
            ultimo_escaneo.groupby("bssid")["rssi_filtrado"]
            .mean()
        )