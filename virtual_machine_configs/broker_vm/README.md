# Instalar la Máquina virtual para el Broker

Esta instalacion automática ejecuta los pasos indicados en SolarisMonitor/README.md para montar el broker.


## Crear la ISO

Primero es necesario crear la iso a partir de los archivos ```user-data``` y ```meta-data``` provistos. 

En linux: 

```bash

cd ./Simulador-SolarisMonitor/virtual_machine_configs/broker_vm
sudo apt install cloud-image-utils
cloud-localds seed.iso user-data meta-data
```

o 
```bash
mkisofs -output seed.iso \
  -volid cidata \
  -joliet \
  -rock \
  user-data meta-data
```


Luego, para instalar el ISO recien creado con un hypervisor como VirtualBox se necesitará la [Ubuntu server ISO](https://ubuntu.com/download/server) como base. 

Importante: Cambiar en Configuracion/Red/Adaptador a Adaptador puente.


## Cargar Virtual Machine

Con VirtualBox Oracle los pasos son los siguientes.

- Crear una maquina virtual desde la sección Nueva Maquina. 
- Seleccionar la Ubuntu server ISO como sistema operativo
- Desmarcar la opcion de instalado automático de estar seleccionado
- Seleccionar los parámetros según preferencia propia. 
- Luego de crear la maquina, abrir configuracion (o settings) haciendo click derecho sobre ella. En la sección de almacenamiento/dispositivos seleccionar add atachment/optical disc. Luego navegar al directorio que contiene a la ISO recien creada y agregarla.
- En Configuracion/Red/Adaptador seleccionar adaptador de tipo puente (bridge).
- Finalmente iniciar la máquina virtual y responder ```yes``` cuando pregunte si instalar automáticamente.

Iniciar sesion con el usuario y contraseña, ambos con ```brokeradmin```, y ejecutar:

```bash
cd /home/brokeradmin/Simulador-SolarisMonitor/virtual_machine_configs/broker_vm
chmod +x ./broker_config.sh

# script para crear contraseñas, y configurar restricciones en la red
./broker_config.sh
```

## Verificacion Despues de la instalación

Iniciar sesion con el usuario y contraseña. En la simulación ambos son ```brokeradmin```.
Para verificar que el broker funciona correctamente se pueden ejecutar los comandos:

```bash
# debe ser broker-vm
hostname 
# debe ser una IP
hostname -I

systemctl status mosquitto
```

Desde otra máquina en la misma red:

```bash
ping broker-vm
```
