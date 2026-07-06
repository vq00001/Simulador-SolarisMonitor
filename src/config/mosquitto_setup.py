# Ejecutar funciones desde una terminal con privilegios de administrador 

import subprocess
import os
import argparse
from src.config.settings import CENTRAL_BROKER_CONFIG, PANEL_CLIENT_CONFIG, SERVER_CLIENT_CONFIG, VISUALIZER_CLIENT_CONFIG


port = CENTRAL_BROKER_CONFIG["port"]


CONFIG_FILE = "/etc/mosquitto/mosquitto.conf"
PASSWD_FILE = "/etc/mosquitto/passwd"

USERS = [
    PANEL_CLIENT_CONFIG,
    SERVER_CLIENT_CONFIG,
    VISUALIZER_CLIENT_CONFIG
]

def create_password_file():

    for user in USERS:
        subprocess.run(
            [
                "mosquitto_passwd",
                "-b",
                "/etc/mosquitto/passwd",
                    user["username"],
                    user["password"]
                ],
                check=True
            )



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["automatic", "manual"],
    )
    args = parser.parse_args()

    mode = args.mode

    if mode is None:
        mode = input(
            "¿Crear constraseñas manual o autmaticamente?"
            "[automatic/manual]: "
        ).strip().lower()

    if mode == "manual":
        print("Omitiendo la creación de contraseñas. Por favor, cree asignar las constraseñas a los usuarios manualmente según las instrucciones en Simulador_SolarisMonitor/virtual_machine_configs/broker_vm/README.md.")
    
    else:
        print("Creando contraseñas de prueba automáticamente...")
        create_password_file()
