# variables de configuracion de red
RATE=54mbit
DELAY=2ms
LOSS=0.1%
IFACE=$(ip route | awk '/default/ {print $5}')

PASSWD_FILE="/etc/mosquitto/passwd"

users=(
    "server server_password"
    "panel panel_password"
    "visualizer visualizer_password"
)

# asegurar que el los servicios esten disponibles
sudo systemctl enable avahi-daemon
sudo systemctl enable mosquitto
ls /etc/mosquitto
# mover archivos de configuracion de mosquitto a /etc/mosquitto
sudo cp -f  /home/brokeradmin/Simulador-SolarisMonitor/src/config/mosquitto_files/mosquitto.conf /etc/mosquitto
sudo cp -f  /home/brokeradmin/Simulador-SolarisMonitor/src/config/mosquitto_files/acl /etc/mosquitto
sudo chown mosquitto:mosquitto /etc/mosquitto/mosquitto.conf
sudo chown mosquitto:mosquitto /etc/mosquitto/acl

# aplicar cambios de configuracion de mosquitto
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v
sudo systemctl restart mosquitto

# crear usuarios y contraseñas para mosquitto
first=true
for entry in "${users[@]}"; do
    read -r username password <<< "$entry"

    # crear archivo de contraseñas si no existe
    if $first; then
        sudo mosquitto_passwd -c -b "$PASSWD_FILE" "$username" "$password"
        first=false
    else
        sudo mosquitto_passwd -b "$PASSWD_FILE" "$username" "$password"
    fi
done
              

echo "Configuración de Mosquitto finalizada"

# crear script de configuracion de red
sudo tc qdisc replace dev "$IFACE" root netem \
    rate "$RATE" \
    delay "$DELAY" \
    loss "$LOSS"
    
echo "Configuración de red finalizada"

