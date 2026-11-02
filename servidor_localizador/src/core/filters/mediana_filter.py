from collections import deque
from statistics import median
from src.core.filters.filter_strategy import FiltroRSSI


class FiltroMediana(FiltroRSSI):


    def __init__(self, nodo_id: int, tamaño_ventana=5):
        self.nodo_id = nodo_id
        self.tamaño_ventana = tamaño_ventana
        self.bssid = {}
        self.finalizado = False


    def filtrar(self, bssid, rssi, estado = None):
        self.finalizado = False
        
        if bssid not in self.bssid:
            self.bssid[bssid] = deque(maxlen=self.tamaño_ventana)

        self.bssid[bssid].append(rssi)

        return median(self.bssid[bssid])
    

    def actualizar(self, redes):

        for red in redes:

            if red.bssid not in self.bssid:
                self.bssid[red.bssid] = deque(
                    maxlen=self.tamaño_ventana
                )

            self.bssid[red.bssid].append(red.rssi)


    def get_valor(self, bssid: str):
        valores = self.bssid.get(bssid)

        if not valores:
            return None

        return median(valores)


    def get_nombre_metodo(self):
        return "Mediana"
    
    
    def finalizar(self):
        if self.finalizado:
            return
        
        self.finalizado = True