
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

Editar o crear el archivo de configuración de listener:

```bash
sudo nano /etc/mosquitto/conf.d/listener.conf
```

Agregar:

```conf
listener 1883
allow_anonymous true
```

Reiniciar el servicio:

```bash
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

* Broker en máquina local:

```
localhost
```

* Broker en red:

```
IP_DEL_BROKER
```

---

## Notas importantes

* Si el broker se ejecuta en una máquina distinta, todas las máquinas deben usar su IP.
* El puerto por defecto es `1883` y debe ser consistente en todo el sistema.
* Asegurarse de que el firewall permita conexiones entrantes al puerto `1883`.

---

## Ejecución del sistema

### Ejecutar publicadores

```bash
python -m src.main.run_publishers
```

---

### Ejecutar suscriptores

```bash
python -m src.main.run_subscribers
```

---

## Ejecución en múltiples terminales

Es posible ejecutar publicadores y suscriptores en distintas terminales de una misma máquina para pruebas locales.

