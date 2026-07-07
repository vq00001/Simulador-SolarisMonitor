RATE=54mbit
DELAY=50ms
LOSS=5%
IFACE=$(ip route | awk '/default/ {print $5}')

PASSWD_FILE="/etc/mosquitto/passwd"

users=(
    "server server_password"
    "panel panel_password"
    "visualizer visualizer_password"
)

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

# asignar permisos al archivo de contraseñas
sudo chmod 0700 "$PASSWD_FILE"
sudo chown mosquitto:mosquitto "$PASSWD_FILE"


echo "Configuración de Mosquitto finalizada"

# crear script de configuracion de red
sudo tc qdisc replace dev "$IFACE" root netem \
    rate "$RATE" \
    delay "$DELAY" \
    loss "$LOSS"
    
echo "Configuración de red finalizada"
