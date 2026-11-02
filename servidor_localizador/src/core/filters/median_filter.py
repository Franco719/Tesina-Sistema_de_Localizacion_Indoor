from collections import deque
from src.core.filters.filter_strategy import FiltroRSSI


class FiltroMedia(FiltroRSSI):

    def __init__(self, nodo_id: int, tamaño_ventana=5):
        self.nodo = nodo_id
        self.tamaño_ventana = tamaño_ventana
        self.bssid = {}
        self.finalizado = False


    def actualizar(self, redes):
        for red in redes:
            self.filtrar(
                red.bssid,
                red.rssi
            )


    def filtrar(self, bssid, rssi , estado = None):
        
        self.finalizado = False

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
    
    
    def finalizar(self):
        if self.finalizado:
            return
        
        self.finalizado = True