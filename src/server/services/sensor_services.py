from datetime import datetime

from src.server.models.sensor import Sensor


async def registrar_sensor(
    session,
    *,
    panel_id: int,
    tipo_medicion_id: int,
    commit = False
) -> Sensor:
    """
    Registra un nuevo Sensor en la base de datos.
    """

    sensor = Sensor(
        panel_id=panel_id,
        tipo_medicion_id=tipo_medicion_id,
    )

    session.add(sensor)

    if commit:
        await session.commit()
        await session.refresh(sensor)

    return sensor

