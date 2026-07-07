import time
from collections import deque
from src.config.settings import CENTRAL_BROKER_CONFIG


class Broker:
    def __init__(self):
        self.hostname = CENTRAL_BROKER_CONFIG["hostname"]
        self.port = CENTRAL_BROKER_CONFIG["port"]

        # parametros de la simulación del enlace
        self.bandwidth_bps = CENTRAL_BROKER_CONFIG["bandwidth_bps"]
        self.max_queue_size = CENTRAL_BROKER_CONFIG["max_queue_size"]

        # cola para simular la transmisión de mensajes a través del enlace
        self.queue = deque()

        # momento en el que el enlace se libera
        self.link_free_at = time.monotonic()

    def get_broker_info(self):
        return self.hostname, self.port

    def enqueue_message(self, payload_size_bytes):


        '''
        Encola un mensaje para simular la transmisión a través del enlace.
        Sigue la formula: tiempo_transmision = tamaño_mensaje_bits / ancho_banda_bps

        Args:
            payload_size_bytes (int): Tamaño del mensaje en bytes.

        Returns:
            float: Tiempo estimado de transmisión en segundos, o None si la cola está llena.
        '''
        now = time.monotonic()

        # si la cola está llena, no se puede agregar el mensaje a la cola
        if len(self.queue) >= self.max_queue_size:
            return None

        size_bits = payload_size_bytes * 8             # convertir bytes a bits
        transm_time = size_bits / self.bandwidth_bps   # calcular el tiempo de transmisión en segundos

        start = max(now, self.link_free_at)         # determinar el momento en que se puede iniciar la transmisión
        finish = start + transm_time                # calcular el momento en que se completará la transmisión

        self.link_free_at = finish    

        self.queue.append(
            {
                "arrival": now,
                "start": start,
                "finish": finish,
                "size_bytes": payload_size_bytes,
            }
        )

        return finish - now

    async def reserve_transmission(self, payload_size_bytes: int) -> float:
        loop = asyncio.get_running_loop()

        # Reservar el tiempo de transmisión para un mensaje de tamaño payload_size_bytes.
        # Devuelve el tiempo de espera estimado antes de que se pueda transmitir el mensaje.
        async with self._lock:
            now = loop.time()

            tx_time = (
                payload_size_bytes * 8
                / self.bandwidth_bps
            )

            start = max(now, self._link_free_at)
            deliver_at = start + tx_time

            self._link_free_at = deliver_at

            return max(0.0, deliver_at - now)