from pathlib import Path
import joblib
import hashlib
from src.core.models.entrenamiento_red import Entrenamiento, EstadoEntrenamiento
from dotenv import load_dotenv
import os
from src.core.inference.modelo_red import ModeloNN
from src.core.database import db
from src.core.models.muestra_wifi import MuestraWifi
import pandas as pd

load_dotenv()

class GestorModelos:

    def __init__(self):
        path_modelos = os.environ.get("PATH_MODELOS")

        if not path_modelos:
            raise ValueError("No está definida la variable PATH_MODELOS.")

        self.directorio_modelos = Path(path_modelos)
        self.directorio_modelos.mkdir(parents=True, exist_ok=True)
        

    def guardar(self, id_entrenamiento, modelo, label_encoder, bssids, metodo_filtrado, configuracion):
        ruta = (
            self.directorio_modelos
            / f"modelo_{id_entrenamiento}.joblib"
        )
        
        if not ruta:
            raise ValueError("No está definida la variable PATH_MODELOS.")

        artefacto = {
            "modelo": modelo,
            "label_encoder": label_encoder,
            "bssids": list(bssids),
            "metodo_filtrado": metodo_filtrado,
            "configuracion": configuracion
        }

        joblib.dump(artefacto, ruta)

        hash_modelo = self.calcular_hash(ruta)

        return {
            "ruta": str(ruta),
            "hash": hash_modelo
        }
    

    def cargar_red(self, id_entrenamiento: int = None):
        
        if id_entrenamiento:
            entrenamiento = Entrenamiento.get_entrenamiento_by_id(id_entrenamiento)
            
            if entrenamiento is None:
                return {"exito": False, "error": "No existe el entrenamiento en la base de datos."}
            
        else:
            try:
                entrenamiento = Entrenamiento.get_entrenamiento_activo()
            except ValueError as e:
                return {"exito": False, "error": e}


        if not entrenamiento.path_modelo or not entrenamiento.hash_modelo:
            return {"exito": False, "error": "El entrenamiento no tiene un modelo registrado."}

        ruta = Path(entrenamiento.path_modelo)

        if not ruta.is_file():
            return {"exito": False, "error": "No se encontró el archivo del modelo."}

        hash_actual = self.calcular_hash(ruta)

        if hash_actual != entrenamiento.hash_modelo:
            return {"exito": False, "error": "El archivo del modelo fue alterado."}

        return {"exito": True, "artefacto": joblib.load(ruta)}
    
    
    def calcular_hash(self, ruta):
        sha256 = hashlib.sha256()

        with open(ruta, "rb") as archivo:
            for bloque in iter(lambda: archivo.read(8192), b""):
                sha256.update(bloque)

        return sha256.hexdigest()