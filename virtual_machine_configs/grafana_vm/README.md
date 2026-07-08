# Ubuntu Server with Grafana
Esta carpeta contiene una ISO personalizada de **Ubuntu Server LTS** para el despliege de **Grafana**, configurado para  una instalación automática mediante `autoinstall` (Subiquity + Cloud-Init NoCloud).

## Qué hace esta ISO

Al arrancar desde la ISO personalizada:

- Instala Ubuntu automáticamente.
- Configura usuario, red y particionado según `autoinstall.yaml`.
- Instala los paquetes necesarios junto con Grafana.
- Aplica configuraciones base del sistema.
- Finaliza sin intervención manual.

No requiere interacción durante la instalación.

## Requisitos

- ISO original de Ubuntu Server LTS.
- Archivo `autoinstall.yaml` adaptado a la configuración deseada.
- Conexión a Internet por cable de red (Ethernet), activa y estable durante toda la instalación.
- Herramientas necesarias:

```sh
sudo apt update
sudo apt install xorriso
```

> [!IMPORTANT]
> Esta instalación ejecuta múltiples tareas que dependen de Internet.
> Es imprescindible iniciar el sistema con cable de red conectado y verificar que la conexión sea estable.
> Si la conexión se interrumpe durante el proceso, el instalador puede fallar.

## Construcción de la ISO personalizada

### 1. Preparar entorno

```sh
mkdir -p ~/autoinstall-iso
cd ~/autoinstall-iso

sudo mkdir -p /mnt/iso
sudo mount -o loop ORIGINAL_ISO.iso /mnt/iso
```

### 2. Copiar contenido de la ISO

```sh
mkdir iso-work
cp -rT /mnt/iso iso-work
sudo umount /mnt/iso
```

### 3. Agregar configuración NoCloud

Crear estructura:

```sh
mkdir -p iso-work/nocloud
touch iso-work/nocloud/meta-data
touch iso-work/nocloud/user-data
```

Copiar el contenido de:

```text
autoinstall.yaml
```

dentro de:

```text
iso-work/nocloud/user-data
```

`meta-data` puede permanecer vacío.

> [!IMPORTANT]
> Cambie la contraseña del usuario en `autoinstall.yaml`. Genere el hash con `mkpasswd -m sha-512` e ingréselo en la configuración.

### 4. Modificar GRUB para autoinstall

Editar:

```sh
vim iso-work/boot/grub/grub.cfg
```

Agregar o modificar la entrada:

```conf
set timeout=5

menuentry "Autoinstall Ubuntu Server" {
    set gfxpayload=keep
    linux   /casper/vmlinuz quiet autoinstall ds=nocloud\;s=/cdrom/nocloud/ ---
    initrd  /casper/initrd
}
```

Esto indica al kernel que active el modo `autoinstall` y utilice el datasource local `nocloud`.

### 5. Generar ISO personalizada

```sh
cd iso-work

xorriso -as mkisofs \
  -r \
  -V "Ubuntu 26.04 LTS amd64" \
  -o ../custom_ubuntu.iso \
  -J -l \
  -iso-level 3 \
  -partition_offset 16 \
  -b boot/grub/i386-pc/eltorito.img \
  -c boot.catalog \
  -no-emul-boot \
  -boot-load-size 4 \
  -boot-info-table \
  -eltorito-alt-boot \
  -e EFI/boot/bootx64.efi \
  -no-emul-boot \
  -isohybrid-gpt-basdat \
  .

cd ..
```

Se generará:

```text
custom_ubuntu.iso
```

## Instalación del sistema

El procedimiento de instalación depende del entorno donde se desplegará la imagen.

- **Equipo físico:** es necesario preparar un medio de instalación (USB).
- **Máquina virtual:** basta con montar el archivo ISO como unidad óptica virtual.

---

### Instalación en un equipo físico

#### Preparación del medio de instalación

##### Opción 1 — Grabar la ISO en un USB con `dd`

Identifique el dispositivo USB:

```sh
lsblk
```

Grabe la imagen:

```sh
sudo dd if=custom_ubuntu.iso of=/dev/sdX bs=4M status=progress && sync
```

Reemplace `/dev/sdX` por el dispositivo correspondiente al USB.

> [!WARNING]
> ⚠️ Esto borra completamente el contenido del USB.

##### Opción 2 — Usar Ventoy (recomendado)

Se recomienda utilizar **Ventoy**, ya que permite almacenar múltiples imágenes ISO en un mismo USB sin necesidad de volver a grabarlo.

Una vez instalado Ventoy copie `custom_ubuntu.iso` al USB.

#### Instalación

> [!WARNING]
> Antes de iniciar la instalación, verifique que el equipo esté conectado mediante Ethernet y que la conexión a Internet sea estable. Si la conexión se interrumpe durante el proceso, la instalación puede fallar.

1. Inicie el equipo desde el USB.
2. Seleccione **Autoinstall Ubuntu Server**.
3. Espere a que finalice la instalación automática.

---

### Instalación en una máquina virtual

1. Cree una nueva máquina virtual con las características de hardware deseadas.
2. Configure `custom_ubuntu.iso` como unidad óptica (CD/DVD) de la máquina virtual.
3. Inicie la máquina virtual desde la imagen ISO.
4. Seleccione **Autoinstall Ubuntu Server**.
5. Espere a que finalice la instalación automática.

> [!WARNING]
> Asegúrese de que la máquina virtual tenga acceso a Internet durante la instalación.

---

## Finalización

Al finalizar la instalación, el sistema quedará configurado con:

- Ubuntu Server instalado.
- Grafana desplegado y en ejecución (`http://<IP_DEL_SERVIDOR>:3000`).
- Configuración básica de seguridad aplicada.
- Acceso remoto mediante SSH habilitado.

> [!NOTE]
> El usuario para iniciar sesión en el sistema es `grafana-admin`. La contraseña corresponde a la definida durante la configuración inicial de la imagen.

### Acceso a Grafana

Una vez que el sistema haya iniciado correctamente:

1. Obtenga la dirección IP del servidor ejecutando:

  ```sh
  ip addr
  ```

2. Desde otro equipo conectado a la misma red (o desde el navegador de la máquina virtual si corresponde), abra:

  ```text
  http://<IP_DEL_SERVIDOR>:3000
  ```

  Por ejemplo:

  ```text
  http://192.168.1.100:3000
  ```

3. Inicie sesión en Grafana utilizando las credenciales configuradas durante la instalación.

Si el acceso no es posible, verifique que el puerto **3000** sea accesible y que el servicio de Grafana esté en ejecución.