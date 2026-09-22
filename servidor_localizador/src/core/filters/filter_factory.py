from src.core.filters.kalman_filter import FiltroKalman
from src.core.filters.filter_strategy import FiltroRSSI
from src.core.filters.mediana_filter import FiltroMediana
from src.core.filters.median_filter import FiltroMedia


def crear_filtro(metodo, ventana=None):

    if metodo == "Kalman":
        return FiltroKalman()

    if metodo == "Mediana":
        return FiltroMediana(ventana)

    if metodo == "Media":
        return FiltroMedia(ventana)

    if metodo == "Ninguno":
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