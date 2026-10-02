from src.core.filters.filter_strategy import FiltroRSSI
from src.core.models.estado_kalman import EstadoKalman


class FiltroKalman(FiltroRSSI):


    def __init__(self):
        self.filtros = {}


    def filtrar(self, bssid, rssi):

        if bssid not in self.filtros:
            self.filtros[bssid] = Kalman1D()

        return self.filtros[bssid].actualizar(rssi)


    def get_valor(self, bssid):

        filtro = self.filtros.get(bssid)

        if filtro is None:
            return None

        return filtro.estado.x


    def actualizar(self, redes):

        for red in redes:
            self.filtrar(red.bssid, red.rssi)


    def get_nombre_metodo(self):
        return "Kalman"


class Kalman1D:


    def __init__(self, estado=None):
        self.estado = estado or EstadoKalman()


    def actualizar(self, medicion):

        if self.estado.x is None:
            self.estado.x = medicion
            return self.estado.x

        # Predicción
        self.estado.p += self.estado.q

        # Ganancia de Kalman
        k = self.estado.p / (
            self.estado.p + self.estado.r
        )

        # Corrección
        self.estado.x += k * (
            medicion - self.estado.x
        )

        # Nueva incertidumbre
        self.estado.p = (
            1 - k
        ) * self.estado.p

        return self.estado.x