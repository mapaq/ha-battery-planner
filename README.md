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

configuration.yaml
```yaml
battery_planner:
  # The total energy capacity of the battery in Watts (W)
  capacity: 5000
  # The maximum allowed state of charge (SoC) in percent as in integer number (80 = 80%)
  upper_soc_limit: 80
  # The minimum allowed state of charge (SoC) in percent as in integer number (5 = 5%)
  lower_soc_limit: 5
  # The maximum allowed power when charging (W)
  max_charge_power: 1000
  # The maximum allowed power when discharging (W)
  max_discharge_power: 2000
  # The difference between charge and discharge price must be above this to schedule a charge cycle
  price_margin: 1.0
  # If below this price, the battery will charge even if not discharging the same day and store for later use
  cheap_price: 0.2

sensor:
  - platform: battery_planner
    currency: SEK
```