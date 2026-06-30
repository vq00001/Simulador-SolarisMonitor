# Instalar la Máquina virtual para el Broker

Esta instalacion automática ejecuta los pasos indicados en SolarisMonitor/README.md para montar el broker.


### Crear la ISO

Primero crear la iso a partir de los archivos provistos. 

En linux: 

```bash
genisoimage -output seed.iso \
  -volid cidata \
  -joliet \
  -rock \
  user-data meta-data
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


### Verificacion Despues de la instalación

Para verificar que el broker funciona correctamente se pueden ejecutar los comandos:

```bash
hostname
systemctl status mosquitto
systemctl status avahi-daemon
```

Desde otra máquina:

```bash
ping broker-vm.local
```
