from sqlalchemy import select

from src.server.database.init_db import init_db
from src.server.enums.tipos_medicion import TipoMedicionEnum
from src.server.database.session import SessionLocal
from src.server.models.tipo_medicion import TipoMedicion
from src.server.services.tipo_medicion_services import registrar_tipo_medicion
import asyncio

async def main():
    init_db()

    async with SessionLocal() as session:
        try:
            result = await session.execute(
                select(TipoMedicion).limit(1)
            )

            if result.scalar_one_or_none() is None:
                await registrar_tipo_medicion(
                    session,
                    tipo=TipoMedicionEnum.TEMPERATURA.value,
                    unidad="°C"
                )

                await registrar_tipo_medicion(
                    session,
                    tipo=TipoMedicionEnum.IRRADIANCIA.value,
                    unidad="W/M2"
                )

                await registrar_tipo_medicion(
                    session,
                    tipo=TipoMedicionEnum.POTENCIA.value,
                    unidad="Watts"
                )

                await session.commit()

        except Exception:
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())