# variables de configuracion de red
RATE=54mbit
DELAY=2ms
LOSS=0.1%
IFACE=$(ip route | awk '/default/ {print $5}')

# asegurar que el los servicios esten disponibles
sudo systemctl enable avahi-daemon
sudo systemctl enable mosquitto

# mover archivos de configuracion de mosquitto a /etc/mosquitto
sudo mv /home/brokeradmin/Simulador-SolarisMonitor/virtual_machine_configs/broker_vm/mosquitto.conf /etc/mosquitto
sudo mv /home/brokeradmin/Simulador-SolarisMonitor/virtual_machine_configs/broker_vm/acl /etc/mosquitto
sudo chown mosquitto:mosquitto /etc/mosquitto/mosquitto.conf
sudo chown mosquitto:mosquitto /etc/mosquitto/acl

python3 /home/brokeradmin/Simulador-SolarisMonitor/config/mosquitto_setup.py --mode automatic

# aplicar cambios de configuracion de mosquitto
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
sudo systemctl restart mosquitto

# crear script de configuracion de red
sudo tc qdisc replace dev "$IFACE" root netem \
    rate "$RATE" \
    delay "$DELAY" \
    loss "$LOSS"
    
echo "Configuración de red finalizada"