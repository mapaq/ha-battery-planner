# ha-battery-planner
Home Assistant integration that plans the charging and discharging of a home battery based on electricity price

A secrets file specifying the used API and needed credentials must be created in the Home Assistant config directory, where the configuration.yaml file is located.

secrets.json
```json
{
    "battery_planner": {
        "api": "example_battery_api",
        "host": "127.0.0.1",
        "username": "theuser",
        "password": "thepassword"
    }
}
```