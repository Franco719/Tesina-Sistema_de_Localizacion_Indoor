from src.core.filters.filter_strategy import FiltroRSSI
from src.core.models.estado_kalman import EstadoKalman


class FiltroKalman(FiltroRSSI):

    def __init__(self, nodo_id: int, sala: str):
        self.nodo = nodo_id
        self.sala = sala
        self.filtros = {}
        self.finalizado = False


    def filtrar(self, bssid, rssi):
        self.finalizado = False

        if bssid not in self.filtros:
            estado = EstadoKalman.get_estado(bssid, self.nodo, self.sala)
            
            print(f"Nodo: {self.nodo}")
            print(f"BSSID: {bssid}")
            print(f"Sala: {self.sala}")
            print(f"Estado recuperado: {estado}")
            
            self.filtros[bssid] = Kalman1D(estado)

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
    
    
    def finalizar(self):
        if self.finalizado:
            return

        for bssid, filtro in self.filtros.items():
            filtro.guardar(self.nodo, bssid, self.sala)

        self.finalizado = True


class Kalman1D:

    def __init__(self, estado=None):
        if estado is None:
            self.x = None
            self.p = 1.0
            self.q = 0.01
            self.r = 1.0
        else:
            self.x = estado.x
            self.p = estado.p
            self.q = estado.q
            self.r = estado.r


    def actualizar(self, medicion):

        if self.x is None:
            self.x = medicion
            return self.x

        # Predicción
        self.p += self.q

        # Ganancia de Kalman
        k = self.p / (
            self.p + self.r
        )

        # Corrección
        self.x += k * (
            medicion - self.x
        )

        # Nueva incertidumbre
        self.p = (
            1 - k
        ) * self.p

        return self.x
    
    
    def guardar(self, nodo_id: int, bssid: str, sala: str):
        EstadoKalman.guardar_estado(
            nodo_id=nodo_id,
            bssid=bssid,
            sala=sala,
            x=self.x,
            p=self.p,
            q=self.q,
            r=self.r
        )