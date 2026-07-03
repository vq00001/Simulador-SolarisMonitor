from datetime import datetime

from src.server.models.panel import Panel
from sqlalchemy import select


async def registrar_panel(
    session,
    *,
    uid: str,
    commit = False
) -> Panel:
    """
    Registra un nuevo panel en la base de datos.
    """

    panel = Panel(
        uid=uid
    )

    session.add(panel)

    if commit:
        await session.commit()
        await session.refresh(panel)

    return panel

async def get_panel_by_uid(session, uid: str) -> Panel:
    """
    Obtiene un panel por su UID.
    """
    result = await session.execute(
        select(Panel).where(Panel.uid == uid)
    )
    panel = result.scalar_one_or_none()
    return panel 

async def get_panel_by_uid_or_create(session, uid: str) -> Panel:
    """
    Obtiene un panel por su UID. Si no existe, lo crea.
    """
    panel = await get_panel_by_uid(session, uid)
    if panel is None:
        panel = await registrar_panel(session, uid=uid, commit=True)
    return panel