from collections import deque
from src.core.filters.filter_strategy import FiltroRSSI


class FiltroMedia(FiltroRSSI):

    def __init__(self, tamaño_ventana=5):
        self.tamaño_ventana = tamaño_ventana
        self.bssid = {}


    def actualizar(self, redes):
        for red in redes:
            self.filtrar(
                red.bssid,
                red.rssi
            )


    def filtrar(self, bssid, rssi):

        if bssid not in self.bssid:
            self.bssid[bssid] = deque(
                maxlen=self.tamaño_ventana
            )

        self.bssid[bssid].append(rssi)

        return sum(self.bssid[bssid]) / len(self.bssid[bssid])


    def get_valor(self, bssid):

        valores = self.bssid.get(bssid)

        if not valores:
            return None

        return sum(valores) / len(valores)


    def get_nombre_metodo(self):
        return "Media"