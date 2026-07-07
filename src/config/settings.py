import os

CENTRAL_BROKER_CONFIG = {
    "hostname": "broker-vm",
    "port": 1883,
    "topic_prefix": "solar_panel_data",

    # Simulación del enlace
    "bandwidth_bps": 1_000_000,  # 1 Mbps
    "max_queue_size": 10000,

    "qos": 1,
    "keepalive": 60,
    "use_tls": False,
}

# usuarios y contraseñas de prueba para los clientes MQTT
PANEL_CLIENT_CONFIG = {
    "username": "panel",
    "password": "panel_password"
}

SERVER_CLIENT_CONFIG = {
    "username": "server",
    "password": "server_password"
}

VISUALIZER_CLIENT_CONFIG = {
    "username": "visualizer",
    "password": "visualizer_password"
}

ACTUATOR_CLIENT_CONFIG = {
    "username": "actuator",
    "password": "actuator_password"
}