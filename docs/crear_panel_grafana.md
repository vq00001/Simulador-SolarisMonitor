# Creación de Paneles en Grafana

Cada panel del dashboard utiliza la misma consulta SQL, variando únicamente el valor del campo `tm.tipo` para mostrar el tipo de medición correspondiente.

## Pasos

1. Crear un nuevo **Time Series Panel**.
2. Seleccionar el **DataSource PostgreSQL** previamente configurado.
3. Cambiar el editor a **Code**.
4. Pegar la siguiente consulta SQL:

```sql
SELECT
    m.timestamp AS "time",
    m.valor
FROM medicion m
JOIN tipo_medicion tm
    ON m.tipo_medicion_id = tm.id
WHERE tm.tipo = '<TIPO_MEDICION>'
ORDER BY m.timestamp;
```

5. Reemplazar `<TIPO_MEDICION>` por el tipo de medición que se desea visualizar.

## Ejemplos

### Temperatura

```sql
SELECT
    m.timestamp AS "time",
    m.valor
FROM medicion m
JOIN tipo_medicion tm
    ON m.tipo_medicion_id = tm.id
WHERE tm.tipo = 'temperatura'
ORDER BY m.timestamp;
```

## Personalización del panel

Para cada panel se recomienda configurar:

- **Visualización:** Time Series.
- **Título:** Nombre de la medición
- **Unidad:** Según corresponda (°C, %, lux, etc.).
- **Rango temporal:** Configurable desde el selector de tiempo del dashboard.

## Agregar nuevos paneles

Para agregar una nueva variable monitoreada:

1. Duplicar un panel existente.
2. Modificar únicamente el valor de `tm.tipo` en la cláusula `WHERE`.
3. Cambiar el título y, si corresponde, la unidad de visualización.

No es necesario modificar el resto de la consulta SQL.