from abc import ABC, abstractmethod

class FiltroRSSI(ABC):
    
    @abstractmethod
    def filtrar(self, bssid: str, rssi: str):
        pass
    
    
    @abstractmethod
    def get_valor(self, bssid: str):
        pass
    
    
    @abstractmethod
    def actualizar(self, redes):
        pass
    
    
    @abstractmethod
    def get_nombre_metodo() -> str:
        pass