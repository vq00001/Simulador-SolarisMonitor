from enum import Enum

class TipoMedicionEnum(str, Enum):
    TEMPERATURA = "temperatura"
   # LUMINOSIDAD = "luminosidad"
    IRRADIANCIA = "irradiancia"
    POTENCIA = "potencia"