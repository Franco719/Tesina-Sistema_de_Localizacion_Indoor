from collections import deque
from statistics import median
from src.core.filters.filter_strategy import FiltroRSSI


class FiltroMediana(FiltroRSSI):


    def __init__(self, tamaño_ventana=5):
        self.tamaño_ventana = tamaño_ventana
        self.bssid = {}


    def filtrar(self, bssid, rssi):
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