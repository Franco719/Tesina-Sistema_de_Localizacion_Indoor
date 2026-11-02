import pandas as pd
from pandas import DataFrame
from src.core.models.muestra_wifi import MuestraWifi
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report
from src.core.filters.filter_manager import filtro_muestreo


class ModeloNN:
    
    CANT_MUESTRAS_NECESARIAS = 100

    def __init__(self):
        self.df = None
        self.x = None
        self.y = None
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.label_encoder = None
        self.modelo = None


    def crear_dataframe(self, filtro):
        muestras = MuestraWifi.get_muestras_order_by_time(filtro)

        cantidad_muestras = len(muestras)

        if cantidad_muestras < self.CANT_MUESTRAS_NECESARIAS:
            return {
                "exito": False,
                "etapa": "preparacion_datos",
                "estado": "datos_insuficientes",
                "mensaje": [
                    f"Se necesitan al menos {self.CANT_MUESTRAS_NECESARIAS} muestras. Se encontraron {cantidad_muestras}."
                ],
                "muestras_disponibles": cantidad_muestras,
                "muestras_requeridas": self.CANT_MUESTRAS_NECESARIAS
            }

        self.df = pd.DataFrame([
            {
                "sala": m.sala,
                "fecha_registro": m.fecha_registro,
                "bssid": m.bssid,
                "rssi_filtrado": m.rssi_filtrado
            }
            for m in muestras
        ])

        self.df["fecha_escaneo"] = (self.df["fecha_registro"].dt.floor("s"))

        self.df = self.df.pivot_table(
            index=["fecha_escaneo", "sala"],
            columns="bssid",
            values="rssi_filtrado",
            aggfunc="mean"
        ).reset_index()

        self.df = self.df.fillna(-100)

        # Información resumida para el servicio.
        salas = self.df["sala"].str.strip()

        self.y = salas

        return {
            "exito": True,
            "etapa": "preparacion_datos",
            "estado": "completado",
            "mensaje": "DataFrame preparado correctamente.",
            "muestras_disponibles": cantidad_muestras,
            "muestras_generadas": len(self.df),
            "cantidad_caracteristicas": len(
                self.df.drop(columns=["fecha_escaneo", "sala"]).columns
            ),
            "cantidad_salas": int(salas.nunique()),
            "salas": sorted(salas.unique().tolist())
        }
        

    def prepare_train(self):
        """Prepara y verifica el dataframe para el entrenamiento"""
        if self.df is None:
            return {
                "exito": False,
                "etapa": "preparacion_entrenamiento",
                "estado": "error",
                "mensaje": "Primero debe prepararse el DataFrame."
            }

        self.x = self.df.drop(
            columns=["fecha_escaneo", "sala"]
        )

        self.y = self.df["sala"].str.strip()

        # Verificar que cada clase tenga suficientes muestras para dividir los datos de manera estratificada.
        distribucion = self.y.value_counts()

        clases_insuficientes = distribucion[distribucion < 2]

        if not clases_insuficientes.empty:
            return {
                "exito": False,
                "etapa": "preparacion_entrenamiento",
                "estado": "datos_insuficientes",
                "mensaje": (
                    "Cada sala necesita al menos dos muestras para realizar la división estratificada."
                ),
                "salas_insuficientes": {
                    sala: int(cantidad)
                    for sala, cantidad in clases_insuficientes.items()
                }
            }

        self.x_train, self.x_test, self.y_train, self.y_test = (
            train_test_split(
                self.x,
                self.y,
                test_size=0.2,
                random_state=42,
                stratify=self.y
            )
        )

        self.label_encoder = LabelEncoder()

        self.y_train = self.label_encoder.fit_transform(
            self.y_train
        )

        self.y_test = self.label_encoder.transform(
            self.y_test
        )

        return {
            "exito": True,
            "etapa": "preparacion_entrenamiento",
            "estado": "completado",
            "mensaje": "Datos de entrenamiento preparados.",
            "muestras_totales": len(self.x),
            "muestras_entrenamiento": len(self.x_train),
            "muestras_test": len(self.x_test),
            "cantidad_caracteristicas": self.x_train.shape[1],
            "cantidad_clases": len(self.label_encoder.classes_),
            "clases": self.label_encoder.classes_.tolist(),
            "distribucion_clases": {
                sala: int(cantidad)
                for sala, cantidad in distribucion.items()
            }
        }


    def train(self):
        """Entrena la red con el dataframe preparado"""
        if self.x_train is None or self.y_train is None:
            return {
                "exito": False,
                "etapa": "entrenamiento",
                "estado": "error",
                "mensaje": (
                    "Primero deben prepararse los datos de entrenamiento."
                )
            }

        self.modelo = MLPClassifier(
            hidden_layer_sizes=(32, 16),
            activation="relu",
            solver="adam",
            max_iter=1000,
            random_state=42
        )

        self.modelo.fit(self.x_train, self.y_train)

        return {
            "exito": True,
            "etapa": "entrenamiento",
            "estado": "completado",
            "mensaje": "Modelo entrenado correctamente.",
            "iteraciones": int(self.modelo.n_iter_),
            "loss": float(self.modelo.loss_),
            "convergio": bool(
                self.modelo.n_iter_ < self.modelo.max_iter
            )
        }
        

    def evaluar(self):
        """Evalua la precisión de la red entrenada"""
        if self.modelo is None:
            return {
                "exito": False,
                "etapa": "evaluacion",
                "estado": "error",
                "mensaje": "Primero debe entrenarse el modelo."
            }

        self.predicciones = self.modelo.predict(self.x_test)

        accuracy = accuracy_score(
            self.y_test,
            self.predicciones
        )

        reporte = classification_report(
            self.y_test,
            self.predicciones,
            labels=list(range(len(self.label_encoder.classes_))),
            target_names=self.label_encoder.classes_,
            output_dict=True,
            zero_division=0
        )

        predicciones_detalladas = []

        salas_reales = self.label_encoder.inverse_transform(
            self.y_test
        )

        salas_predichas = self.label_encoder.inverse_transform(
            self.predicciones
        )

        for real, predicha in zip(
            salas_reales,
            salas_predichas
        ):
            predicciones_detalladas.append({
                "real": str(real),
                "predicha": str(predicha),
                "correcta": bool(real == predicha)
            })

        return {
            "exito": True,
            "etapa": "evaluacion",
            "estado": "completado",
            "mensaje": "Evaluación finalizada.",
            "accuracy": float(accuracy),
            "reporte_clasificacion": reporte,
            "predicciones": predicciones_detalladas
        }
        
"""
# LO agregue pero nose si queda, estaba desmotivado :(     
class EntrenarModelo:
    red = ModeloNN
    filtro = str
    
    
    def __init__(self, filtro: str):
        if filtro in ["Kalman", "Sin Filtro", "Mediana", "Media"]:
            filtro_manager.finalizar()
            self.red = ModeloNN()
            self.filtro = filtro
            
            
    def entrenar(self):
        self.red.crear_dataframe(self.filtro)
        log_preparation = self.red.prepare_train()
        log_train = self.red.train()
        
        return log_preparation + log_train
        
"""
        

        


"""for indice, fila in df_pivot.head(10).iterrows():
        print(f"\n--- Escaneo {indice} ---")
        print(f"Fecha: {fila['fecha_escaneo']}")
        print(f"Sala: {fila['sala']}")

        for bssid in df_pivot.columns[2:]:
            print(f"{bssid}: {fila[bssid]}")"""