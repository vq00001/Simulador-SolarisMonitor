from datetime import datetime

from src.server.models.medicion import Medicion


async def registrar_medicion(
    session,
    *,
    #sensor_id: int,
    panel_id: int,
    tipo_medicion_id: int,
    valor: float,
    timestamp: datetime,
    commit = False
) -> Medicion:
    """
    Registra una nueva medición en la base de datos.
    """
    
    medicion = Medicion(
        #sensor_id=sensor_id,
        panel_id=panel_id,
        tipo_medicion_id=tipo_medicion_id,
        valor=valor,
        timestamp=timestamp,
    )

    session.add(medicion)

    if commit:
        await session.commit()
        await session.refresh(medicion)

    return medicion

