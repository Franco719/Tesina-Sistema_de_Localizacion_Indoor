from src.core.filters.kalman_filter import FiltroKalman
from src.core.filters.filter_strategy import FiltroRSSI
from src.core.filters.mediana_filter import FiltroMediana
from src.core.filters.median_filter import FiltroMedia


def crear_filtro(metodo, nodo_id: int, sala: str, ventana=None):

    match metodo:
        
        case "Kalman":
            return FiltroKalman(nodo_id, sala)

        case "Mediana":
            return FiltroMediana(nodo_id, ventana)

        case "Media":
            return FiltroMedia(nodo_id, ventana)

        case "Ninguno":
            return SinFiltro()

    raise ValueError(f"Método desconocido: {metodo}")


class SinFiltro(FiltroRSSI):

    def filtrar(self, bssid: str, rssi: int):
        return rssi


    def get_valor(self, bssid: str):
        return None


    def actualizar(self, redes):
        return None


    def get_nombre_metodo(self) -> str:
        return "Ninguno"
    
    
    def finalizar(self):
        pass