from src.core.database import db
from datetime import datetime

class MuestraWifi(db.Model):
    __tablename__ = 'muestras_wifi'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nodo_id = db.Column(db.String(10), nullable=False)
    sala = db.Column(db.String(50), nullable=False)
    ssid = db.Column(db.String(32), nullable=False)
    rssi_puro = db.Column(db.Integer, nullable=False)
    rssi_filtrado = db.Column(db.Integer, nullable=True) 
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    metodo_filtrado = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return f"<Muestra {self.sala} - {self.ssid}: {self.rssi}dBm>"
    
    @classmethod
    def crear_muestra (cls, **kwargs):
        nueva_muestra = cls(**kwargs)
        
        db.session.add(nueva_muestra)
        
        # No hago commit debido a que este metodo es usado por la API cuando crea muestras, y hacer varios commits
        # seguidos no es conveniente. Por lo tanto, en la API.
        
        return nueva_muestra