
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
├── docs
├── src
│   |
│   ├── config  
│   │   └── mosquitto_files
│   ├── main
│   │
│   ├── mqtt
│   │  
│   ├── nodes
│   │   
│   └── server
│       |
│       ├── database
│       │   
│       ├── enums
│       ├── handlers
│       │  
│       ├── models
│       └── services
|
└── virtual_machine_configs
    ├── broker_vm
    └── grafana_vm
     
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
sudo mosquitto_passwd -c /etc/mosquitto/passwd -b "panel" "panel_password"
sudo mosquitto_passwd /etc/mosquitto/passwd -b "server" "server_password"
sudo mosquitto_passwd /etc/mosquitto/passwd -b "visualizer" "visualizer_password"
sudo mosquitto_passwd /etc/mosquitto/passwd -b "actuator" "actuator_password"

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

## Configuracion del server 

Para utilizar el server seguir los siguientes pasos: 

(1) Desde una maquina cualquiera con linux:
Instalar:
- postgresql
- postgresql-client
- git
- python
- python-venv
- python-pip

Ej: sudo apt install postgresql

(2) Crear base de datos, correr:
- systemctl enable postgresql --now
- sudo -u postgres psql -c "CREATE USER solaris WITH PASSWORD 'solaris123';"
- sudo -u postgres createdb -O solaris solarismonitor

(3) Preparar el entorno:
- Clonar este repositorio
- Crear entorno virtual de python
- Correr pip install -r requirements.txt
- Crear datos base con python3 -m src.server.crear_db

(4) Asegurar que el Broker este corriendo y correr python3 -m src.server.server 

Con esto el servidor ya estará funcionando.

**Nota:** Se recomienda hacer este proceso en la misma maquina virtual en la que este el broker, ya que tienen muchas dependencias comunes y se puede descomentar el segmento comentado en user-data para preparar más cosas automaticamente.

## Simulador de paneles

Para correr los paneles solo necesita instalar los requerimientos del sistema y correr python3 -m src.main.run_simulation.py, el broker debe estar activo en la red.

**Nota**: Es posible que falle al intentar ejecutarlo a la primera, esto se debe a fallos en el mDNS de avahi-daemon en la cual no se traduce el hostname del broker correctamente, despues de un par de intentos funcionará.

## Configuracion Grafana

![IMPORTANT]

Para instalacion semi-automatica del servidor Grafana con maquinas virtuales dirigirse al README.md de /virtual_machine_configs/grafana_vm/README.md. Luego para conectarlo al servidor revisar en /docs/conexion_grafana_postgresql.md y crear_panel_grafana.md

## Configuración

Para ajustar las configuraciones del sistema puede acceder a src.config.settings.py, ahi estarán todas las variables configurables, para un entorno empresarial claramente se escogerian contraseñas que no sean publicas.
