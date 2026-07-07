# Instalar la Máquina virtual para el Broker

Esta instalacion automática ejecuta los pasos indicados en SolarisMonitor/README.md para montar el broker.


## Crear la ISO

Primero es necesario crear la iso a partir de los archivos ```user-data``` y ```meta-data``` provistos. 

En linux: 

```bash
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

- Luego de crear la maquina, abrir configuracion (o settings) haciendo click derecho sobre ella. En la sección de almacenamiento 


### Verificacion Despues de la instalación

Para verificar que el broker funciona correctamente se pueden ejecutar los comandos:

```bash
hostname
systemctl status mosquitto
```

Desde otra máquina:

```bash
ping broker-vm
```
