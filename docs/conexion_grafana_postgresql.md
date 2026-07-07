# Configuración de PostgreSQL para permitir acceso remoto desde Grafana

Esta guía describe cómo configurar un servidor PostgreSQL para permitir que una instancia de Grafana ubicada en otra máquina se conecte y consulte una base de datos mediante un **Data Source** de PostgreSQL.

## Escenario

- **Servidor PostgreSQL:** Máquina donde se encuentra la base de datos.
- **Servidor Grafana:** Máquina independiente desde donde se consultarán los datos.
- **Base de datos:** `solarismonitor`
- **Usuario:** `solaris`

## Datos necesarios

| Parámetro | Valor |
|-----------|-------|
| Host PostgreSQL | `IP_DEL_SERVIDOR_POSTGRESQL` |
| Host Grafana | `IP_DEL_SERVIDOR_GRAFANA` |
| Puerto PostgreSQL | `5432` |
| Base de datos | `solarismonitor` |
| Usuario | `solaris` |
| Contraseña | `solaris123` |

---

# 1. Configurar la autenticación en PostgreSQL

Editar el archivo `pg_hba.conf`:

```bash
sudo vim /etc/postgresql/18/main/pg_hba.conf
```

Buscar la siguiente línea:

```text
local   all             all                                     peer
```

Reemplazarla por:

```text
local   all             all                                     scram-sha-256
```

Luego agregar la siguiente regla para permitir conexiones desde el servidor donde se ejecuta Grafana:

```text
host    solarismonitor    solaris    IP_DEL_SERVIDOR_GRAFANA/32    scram-sha-256
```

> [!NOTE]
> Reemplazar `IP_DEL_SERVIDOR_GRAFANA` por la dirección IP del servidor donde está instalado Grafana.

---

# 2. Habilitar conexiones remotas

Editar el archivo de configuración de PostgreSQL:

```bash
sudo vim /etc/postgresql/18/main/postgresql.conf
```

Buscar la directiva:

```text
#listen_addresses = 'localhost'
```

Descomentarla y modificarla por:

```text
listen_addresses = 'localhost,IP_DEL_SERVIDOR_POSTGRESQL'
```

También es posible aceptar conexiones desde cualquier interfaz utilizando:

```text
listen_addresses = '*'
```

> [!NOTE]
> Por motivos de seguridad, se recomienda escuchar únicamente en las direcciones IP necesarias.

---

# 3. Reiniciar PostgreSQL

Aplicar los cambios reiniciando el servicio:

```bash
sudo systemctl restart postgresql
```

---

# 4. Verificar la conectividad

Antes de configurar Grafana, se recomienda validar que PostgreSQL acepta conexiones tanto de forma local como desde el servidor donde se ejecuta Grafana.

## Desde el servidor PostgreSQL (conexión local)

```bash
psql -U solaris -d solarismonitor -W
```

Esta prueba verifica que la base de datos, el usuario y la autenticación funcionan correctamente en el servidor PostgreSQL.

## Desde el servidor Grafana (conexión remota)

```bash
psql -h IP_DEL_SERVIDOR_POSTGRESQL -U solaris -d solarismonitor -W
```

Esta prueba verifica que:

- Existe conectividad de red entre ambos servidores.
- PostgreSQL está aceptando conexiones remotas.
- La configuración de `pg_hba.conf` permite el acceso desde la IP del servidor Grafana.
- El usuario `solaris` puede autenticarse correctamente.

Si ambas pruebas son exitosas, Grafana podrá utilizar las mismas credenciales para conectarse a la base de datos.

---

# 5. Configurar el Data Source en Grafana

En Grafana, crear un nuevo **Data Source** de tipo **PostgreSQL** con la siguiente configuración:

| Campo | Valor |
|--------|-------|
| Host | `IP_DEL_SERVIDOR_POSTGRESQL:5432` |
| Database | `solarismonitor` |
| User | `solaris` |
| Password | `solaris123` |

Seleccionar **Save & Test** para verificar la conexión.

> [!TIP]
> Si la configuración es correcta, Grafana mostrará un mensaje indicando que la conexión con PostgreSQL fue exitosa.

---

# Consideraciones

- Verificar que el puerto **5432/TCP** esté habilitado en el firewall del servidor PostgreSQL.
- Confirmar que exista conectividad de red entre el servidor de Grafana y el servidor PostgreSQL.
- Restringir el acceso únicamente a la IP del servidor Grafana mediante la configuración de `pg_hba.conf`.
