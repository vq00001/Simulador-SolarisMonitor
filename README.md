
# Simulador SolarisMonitor

Sistema de simulación de red para la adquisición, transmisión, procesamiento y almacenamiento de datos generados por sensores en paneles solares fotovoltaicos.

El objetivo es permitir el monitoreo remoto del rendimiento de los paneles, facilitando la detección temprana de fallas y la identificación de equipos con bajo desempeño.

---

## Arquitectura general

El sistema se basa en una comunicación tipo MQTT entre:

* Publicadores (sensores simulados)
* Broker MQTT (Mosquitto)
* Suscriptores (procesamiento y análisis de datos)

```text
│
├───src
|   ├───__init__.py
|   │
|   ├───config
|   │   │   settings.py
|   │   └── __init__.py
|   │
|   ├───main
|   │   │   run_publisher.py
|   │   │   run_subscriber.py
|   │   └── __init__.py
|   │
|   ├───mqtt
|   │   │   client_factory.py
|   │   │   connection.py
|   │   │   definitions.py
|   │   │   publisher.py
|   │   │   suscriber.py
|   │   └───__init__.py
|   │
|   ├───nodes
|   │   │   solar_panel.py
|   │   └───__init__.py
|   │
|   └───topics
|       └───panel_topics.py
│
└───virtual_machine_configs
    └───grafana_vm
            autoinstall.yaml
            README.md

     
```
---

## Requisitos

* Python 3.8 o superior
* Ubuntu recomendado para el broker MQTT
* Mosquitto (broker MQTT)

---

## Instalación de dependencias Python

```bash
pip install -r requirements.txt
```

---

## Instalación de Mosquitto (broker MQTT)

Instalar Mosquitto en la máquina que actuará como broker:

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients -y
```

---

## Configuración del broker

![IMPORTANT]
```
Para instalacion semi-automatica con máquinas virtuales ir a ./virtual_machine_configs/broker_vm/README.md.
``` 

Para conectarse al broker sera necesario editar los siguientes archivos: 

1. /etc/mosquitto/mosquitto.conf
2. /etc/mosquitto/acl
3. /etc/mosquitto/conf.d/listener.conf

Si se quiere ejecutar la simulacion del proyecto se deberán reemplazar por los ejemplos en src/config/mosquitto_files. Nota: es necesario abrirlos con privilegios de administrador para editarlos. 

Crear usuarios y contraseñas de prueba:

```bash
# notar que solo el primer comando lleva -c para crear el archivo
sudo mosquitto/passwd -c /etc/mosquitto/passwd -b "panel" "panel_password"

sudo mosquitto/passwd /etc/mosquitto/passwd -b "server" "server_password"
sudo mosquitto/passwd /etc/mosquitto/passwd -b "visualizer" "visualizer_password"

# Asignar permisos para el archivo de contraseñas
# indispensable
sudo chmod 0700 /etc/mosquitto/passwd
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd

# aplicar cambios
sudo systemctl restart mosquitto 
```
---

## Configuración de red

El broker debe ser accesible desde otras máquinas de la red.

### Obtener IP del broker

```bash
hostname -I
```

---

### Configurar dirección del broker en el proyecto

Editar:

```
src/config/settings.py
```

Definir:

* Broker en red:

```bash
CENTRAL_BROKER_CONFIG = {
    "hostname": IP_DEL_BROKER,
    "port": 1883,
...
```

---

## Notas importantes

* Si el broker se ejecuta en una máquina distinta, todas las máquinas deben usar su IP.
* El puerto por defecto es `1883` y debe ser consistente en todo el sistema.
* Asegurarse de que el firewall permita conexiones entrantes al puerto `1883`.
