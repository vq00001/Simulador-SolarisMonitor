from dataclasses import dataclass

# clase para definir los topicos de los paneles que se van a utilizar en el proyecto
class PanelTopics:
    class Solar:
        ROOT = "solar_panel_data"
        TEMPERATURE = f"{ROOT}/temperature"
        POWER = f"{ROOT}/power"
        IRRADIANCE = f"{ROOT}/irradiance"
        ALL = f"{ROOT}/#"

    class Weather:
        ROOT = "weather_data"
        TEMPERATURE = f"{ROOT}/temperature"
        LUMINOSITY = f"{ROOT}/luminosity"
        ALL = f"{ROOT}/#"
