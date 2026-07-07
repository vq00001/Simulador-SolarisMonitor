from datetime import datetime

from src.server.models.tipo_medicion import TipoMedicion
from sqlalchemy import select


async def registrar_tipo_medicion(
    session,
    *,
    tipo: str,
    unidad : str,
    commit = False
) -> TipoMedicion:
    """
    Registra un nuevo Tipo de Medición en la base de datos.
    """

    tipo_medicion = TipoMedicion(
        tipo=tipo,
        unidad_medida=unidad,
    )

    session.add(tipo_medicion)

    if commit:
        await session.commit()
        await session.refresh(tipo_medicion)

    return tipo_medicion

async def get_by_tipo(session, tipo: str) -> TipoMedicion:
    """
    Obtiene un Tipo de Medición por su tipo.
    """
    result = await session.execute(
        select(TipoMedicion).where(TipoMedicion.tipo == tipo)
    )
    return result.scalar_one_or_none()

