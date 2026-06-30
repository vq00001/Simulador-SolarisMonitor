# Ejecutar funciones desde una terminal con privilegios de administrador 

import subprocess
import os
import argparse
from src.config.settings import CENTRAL_BROKER_CONFIG["port"] as PORT


CONFIG_FILE = "/etc/mosquitto/conf.d/listener.conf"
PASSWD_FILE = "/etc/mosquitto/passwd"

USERS = [
    {
        "name": "admin",
        "password": "admin_password",
    },
    {
        "name": "server",
        "password": "server_password",
    },
    {
        "name": "visualizer",
        "password": "visualizer_password",
    },
    {
        "name": "panel",
        "password": "panel_password",
    }
]

def create_configuration_file():
   

    with open("/etc/mosquitto/conf.d/listener.conf", "w") as file:
        file.write(f"listener {PORT}\n")
        file.write("allow_anonymous false\n")
        file.write("password_file /etc/mosquitto/passwd\n")

def create_password_file():

    for user in USERS:
        subprocess.run(
            [
                "mosquitto_passwd",
                "-b",
                "/etc/mosquitto/passwd",
                    user["name"],
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
            "¿Crear archivos de configuracion manual o autmaticamente?"
            "[automatic/manual]: "
        ).strip().lower()

    if mode == "manual":
        print("Omitiendo la creación de archivos de configuración y contraseñas. Por favor, cree los archivos listener.conf y passwd manualmente según las instrucciones en Simulador_SolarisMonitor/virtual_machine_configs/broker_vm/README.md.")
    
    else:
        print("Creando archivos de configuración y contraseñas de prueba automáticamente...")
        create_configuration_file()
        create_password_file()
