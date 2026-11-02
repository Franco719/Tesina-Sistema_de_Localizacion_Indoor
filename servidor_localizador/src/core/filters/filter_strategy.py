from abc import ABC, abstractmethod

class FiltroRSSI(ABC):
    
    @abstractmethod
    def filtrar(self, bssid: str, rssi: str, estado = None):
        pass
    
    
    @abstractmethod
    def get_valor(self, bssid: str):
        pass
    
    
    @abstractmethod
    def actualizar(self, redes):
        pass
    
    
    @abstractmethod
    def get_nombre_metodo(self) -> str:
        pass
    
    
    @abstractmethod
    def finalizar(self):
        pass