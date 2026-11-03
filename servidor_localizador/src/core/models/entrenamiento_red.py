from src.core.database import db
from datetime import datetime
from enum import Enum

    
class EstadoEntrenamiento(Enum):
    PENDIENTE = "pendiente"
    EJECUTANDO = "ejecutando"
    COMPLETADO = "completado"
    FALLIDO = "fallido"


class Entrenamiento(db.Model):
    __tablename__ = 'entrenamiento'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.Enum(EstadoEntrenamiento), default=EstadoEntrenamiento.PENDIENTE)
    metodo_filtrado = db.Column(db.String(32), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.now)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    cant_muestras_disponibles = db.Column(db.Integer, nullable=True) # Cantidad de muestras tomadas de la base
    cant_rafagas_generadas = db.Column(db.Integer, nullable=True) # Cantidad de escaneos (en un escaneo, se toman varias muestras)
    cant_bssids = db.Column(db.Integer, nullable=True)
    cant_salas = db.Column(db.Integer, nullable=True)
    accuracy = db.Column(db.Float, nullable=True)
    loss = db.Column(db.Float, nullable=True)
    iteraciones = db.Column(db.Integer, nullable=True)
    path_modelo = db.Column(db.Text, nullable=True)
    errores = db.Column(db.Text, nullable=True)
    hash_modelo = db.Column(db.String(64), nullable=True) # Como al cargar joblib.load() se ejecuta código, creo un hash para al menos verificar que no haya sido modificado antes de cargarlo
    borrado = db.Column(db.Boolean, nullable=True, default=False)
    activo = db.Column(db.Boolean, nullable=True, default=False)
    
    
    @classmethod
    def crear_entrenamiento (cls, **kwargs):
        nuevo_entrenamiento = cls(**kwargs)
        
        db.session.add(nuevo_entrenamiento)
        db.session.commit()
        
        return nuevo_entrenamiento

    @classmethod
    def get_entrenamiento_by_id(cls, id: int):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def get_entrenamientos(cls):
        return cls.query.filter_by(borrado=False).all()
    
    @classmethod
    def get_entrenamiento_activo(cls):
        entrenamiento = cls.query.filter_by(borrado=False, activo=True).all()
        
        if len(entrenamiento) != 1:
            print(len(entrenamiento))
            raise ValueError("Más de una red se encuentra activa, verifique el panel de modelos entrenados")
        
        return entrenamiento.pop()
    
    @classmethod
    def eliminar_entrenamiento(cls, id: str) -> bool:
        """Deletes the user sended by email, and returns if it was deleted or not"""
        entrenamiento = cls.get_entrenamiento_by_id(id)

        if entrenamiento:
            entrenamiento.borrado = True
            db.session.commit()
            return True
        else:
            return False
    
    def abortar_entrenamiento(self, errores: list[str]):
        self.estado = EstadoEntrenamiento.FALLIDO
        if self.errores:
            self.errores += f"{"".join(errores)}"
        else:
            self.errores = f"{"".join(errores)}"
        
        db.session.commit() 
        
    def guardar_ejecucion(self):
        self.estado = EstadoEntrenamiento.EJECUTANDO
        
        db.session.commit()
        
    def actualizar_entrenamiento(self, **kwargs):
        for attribute, value in kwargs.items():
            match attribute:
                case "estado":
                    self.estado = value
                case "fecha_fin":
                    self.fecha_fin = value
                case "cant_muestras_disponibles":
                    self.cant_muestras_disponibles = value
                case "cant_rafagas_generadas":
                    self.cant_rafagas_generadas = value
                case "cant_bssids":
                    self.cant_bssids = value
                case "cant_salas":
                    self.cant_salas = value
                case "accuracy":
                    self.accuracy = value
                case "loss":
                    self.loss = value
                case "iteraciones":
                    self.iteraciones = value
                case "path_modelo":
                    self.path_modelo = value
                case "errores":
                    self.errores = value
                case "hash_modelo":
                    self.hash_modelo = value
                    
        db.session.commit()