# Ejecutar funciones desde una terminal con privilegios de administrador

import argparse
import subprocess

from src.config.settings import CENTRAL_BROKER_CONFIG

CONFIG_FILE = "/etc/mosquitto/conf.d/listener.conf"
PASSWD_FILE = "/etc/mosquitto/passwd"
PORT = CENTRAL_BROKER_CONFIG["port"]

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
    },
]


def create_configuration_file() -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        file.write(f"listener {PORT}\n")
        file.write("allow_anonymous false\n")
        file.write(f"password_file {PASSWD_FILE}\n")


def create_password_file() -> None:
    for user in USERS:
        subprocess.run(
            ["mosquitto_passwd", "-b", PASSWD_FILE, user["name"], user["password"]],
            check=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["automatic", "manual"])
    args = parser.parse_args()

    mode = args.mode

    if mode is None:
        mode = (
            input(
                "¿Crear archivos de configuracion manual o automaticamente? "
                "[automatic/manual]: "
            )
            .strip()
            .lower()
        )

    if mode == "manual":
        print(
            "Omitiendo la creación de archivos de configuración y contraseñas. "
            "Por favor, cree los archivos listener.conf y passwd manualmente "
            "según las instrucciones en "
            "Simulador_SolarisMonitor/virtual_machine_configs/broker_vm/README.md."
        )
    else:
        print(
            "Creando archivos de configuración y contraseñas de prueba "
            "automáticamente..."
        )
        create_configuration_file()
        create_password_file()
