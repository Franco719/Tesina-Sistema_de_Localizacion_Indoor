from src.core.filters.filter_factory import crear_filtro
from threading import Lock


class FiltroManager:

    def __init__(self):
        self.filtro_actual = None
        self.lock = Lock()

    def iniciar(self, metodo, nodo_id: int, sala: str = None , ventana=None):
        with self.lock:
            self.filtro_actual = crear_filtro(metodo, nodo_id, sala, ventana)

    def obtener(self):
        with self.lock:
            return self.filtro_actual

    def finalizar(self):
        with self.lock:
            if self.filtro_actual is None:
                return

            self.filtro_actual.finalizar()
            self.filtro_actual = None


filtro_muestreo = FiltroManager()
filtro_prediccion = FiltroManager()