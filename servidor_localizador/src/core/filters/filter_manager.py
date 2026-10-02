from src.core.filters.filter_factory import crear_filtro


class FiltroManager:

    def __init__(self):
        self.filtro_actual = None

    def iniciar(self, metodo, ventana=None):
        self.filtro_actual = crear_filtro(metodo, ventana)

    def obtener(self):
        return self.filtro_actual

    def finalizar(self):
        self.filtro_actual = None


filtro_manager = FiltroManager()