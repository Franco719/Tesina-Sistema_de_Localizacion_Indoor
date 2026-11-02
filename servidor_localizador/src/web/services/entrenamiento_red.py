from src.core.inference.modelo_red import ModeloNN
from src.core.models.muestra_wifi import MuestraWifi
from src.core.models.entrenamiento_red import EstadoEntrenamiento, Entrenamiento
import pandas as pd
from src.core.inference.gestor_modelos import GestorModelos
from src.core.task_entrenamiento import ejecutar_entrenamiento
from src.core.database import redis_client
from src.core.filters.filter_manager import filtro_prediccion
from datetime import datetime


class ServicioEntrenamiento:
    gestor = GestorModelos()

    def iniciar(self, metodo_filtrado: str, nombre_entrenamiento: str):
        # Registrar la tarea y enviarla al ejecutor.
        entrenamiento = Entrenamiento.crear_entrenamiento(
            metodo_filtrado = metodo_filtrado,
            nombre = nombre_entrenamiento
        )
        
        ejecutar_entrenamiento.delay(entrenamiento.id)
        # Devolver el identificador sin esperar el resultado.
        return entrenamiento.id
    
    
    def entrenar(self, id_entrenamiento: int):
        entrenamiento = Entrenamiento.get_entrenamiento_by_id(id_entrenamiento)
        
        if not entrenamiento:
            errores = ["No se ha encontrado el entrenamiento en la Base de Datos"]
            entrenamiento.abortar_entrenamiento(errores)
            return {
                "exito": False,
                "id_entrenamiento": id_entrenamiento
            }
        
        modelo = ModeloNN()
        dataframe = modelo.crear_dataframe(entrenamiento.metodo_filtrado)
        
        if not dataframe["exito"]:
            entrenamiento.abortar_entrenamiento(dataframe["mensaje"])
            return {
                "exito": False,
                "id_entrenamiento": id_entrenamiento
            } 
        
        datos_entrenamiento = {
            "estado": EstadoEntrenamiento(dataframe["estado"]),
            "cant_muestras_disponibles": dataframe["muestras_disponibles"],
            "cant_rafagas_generadas": dataframe["muestras_generadas"],
            "cant_bssids": dataframe["cantidad_caracteristicas"],
            "cant_salas": dataframe["cantidad_salas"],
        }
        
        entrenamiento.actualizar_entrenamiento(**datos_entrenamiento)
        
        preparacion = modelo.prepare_train()
        
        if not preparacion["exito"]:
            entrenamiento.abortar_entrenamiento(preparacion["mensaje"])
            return {
                "exito": False,
                "id_entrenamiento": id_entrenamiento
            }

        train = modelo.train()
        
        if not train["exito"]:
            entrenamiento.abortar_entrenamiento(train["mensaje"]) 
            return {
                "exito": False,
                "id_entrenamiento": id_entrenamiento
            }
        
        datos_entrenamiento = {
            "iteraciones": train["iteraciones"],
            "loss": train["loss"]
        }
        
        entrenamiento.actualizar_entrenamiento(**datos_entrenamiento)
        
        evaluacion = modelo.evaluar()
        
        if not evaluacion["exito"]:
            entrenamiento.abortar_entrenamiento(evaluacion["mensaje"]) 
            return {
                "exito": False,
                "id_entrenamiento": id_entrenamiento
            }
        
        datos_entrenamiento = {
            "accuracy": evaluacion["accuracy"],
        }
        
        entrenamiento.actualizar_entrenamiento(**datos_entrenamiento)

        # Obtener los BSSID en el mismo orden que las características de entrada.
        bssids = list(modelo.x.columns)

        # Obtener la configuración utilizada por la red.
        configuracion = modelo.modelo.get_params()

        # Guardar el modelo y calcular su hash.
        resultado_guardado = self.gestor.guardar(
            id_entrenamiento=entrenamiento.id,
            modelo=modelo.modelo,
            label_encoder=modelo.label_encoder,
            bssids=bssids,
            metodo_filtrado=entrenamiento.metodo_filtrado,
            configuracion=configuracion
        )

        # Registrar la ubicación y el hash del archivo en PostgreSQL.
        datos_entrenamiento = {
            "path_modelo": resultado_guardado["ruta"],
            "hash_modelo": resultado_guardado["hash"],
            "estado": EstadoEntrenamiento.COMPLETADO,
            "fecha_fin": datetime.now()
        }
        
        entrenamiento.actualizar_entrenamiento(**datos_entrenamiento)
        
        return {
            "exito": True,
            "id_entrenamiento": id_entrenamiento
        }
            
    
    def preparar_entrada(self, escaneo, bssids):
        datos = {
            bssid: escaneo.get(bssid, -100)
            for bssid in bssids
        }

        return pd.DataFrame([datos], columns=bssids)
    
    
    def predecir_posicion(self, id_entrenamiento, nodo_id: int):
        # 1. Cargar el artefacto guardado.
        artefacto = GestorModelos.cargar(id_entrenamiento)

        modelo = artefacto["modelo"]
        label_encoder = artefacto["label_encoder"]
        bssids = artefacto["bssids"]
        metodo_filtrado = artefacto["metodo_filtrado"]

        # 2. Recuperar el último escaneo.
        registros_redis = redis_client.obtener_lectura_cruda(nodo_id)

        # 3. Preparar la entrada.
        #filtro = filtro_prediccion.iniciar(metodo_filtrado, nodo_id)
        
        muestras = []
        
        for red in registros_redis:
        
            #rssi_puro = red.get("rssi")

            """rssi_filtrado = filtro.filtrar(
                red.get("bssid"),
                rssi_puro
            )"""
            
            muestras.append({
                "bssid": red.get("bssid"),
                "rssi": red.get("rssi")
            })
        
        datos_entrada = self.preparar_entrada(muestras, bssids)

        # 4. Ejecutar la predicción.
        prediccion = modelo.predict(datos_entrada)

        # 5. Convertir la clase numérica en el nombre de la sala.
        sala = label_encoder.inverse_transform(
            prediccion.astype(int)
        )[0]

        return {
            "sala_predicha": sala,
            "fecha_escaneo": datetime.now(),
            "metodo_filtrado": metodo_filtrado
        }