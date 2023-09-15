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

sensor:
  - platform: battery_planner
    currency: SEK
```

Call the battery planner services by e.g. creating a script that can by used in automations or buttons

scripts.yaml
```yaml
reschedule_battery:
  alias: "Reschedule battery"
  sequence:
    - service: battery_planner.reschedule
      data:
        # Battery SoC in %
        battery_soc: "{{ (states('sensor.battery_state_of_charge')|float) | round(1) }}"
        # Price series for import and export prices, split into today and tomorrow since this is how the nordpool integtaion provides the data
        import_prices_today: "{{ state_attr('sensor.electricity_price_import', 'today') }}"
        import_prices_tomorrow: "{{ state_attr('sensor.electricity_price_import', 'tomorrow') }}"
        export_prices_today: "{{ state_attr('sensor.electricity_price_export', 'today') }}"
        export_prices_tomorrow: "{{ state_attr('sensor.electricity_price_export', 'tomorrow') }}"
        # The cost of cycling one kWh of energy in the battery (battery cost / capacity (kWh) / lifetime charge cycles)
        battery_cycle_cost: 83
        # Extra price margin to add on top import price + battery cycle cost that the diff between import and export must exceed
        price_margin: 10
        # If no charge cycles can be made and the battery is empty, charge the battery if import price is below this threshold
        low_price_threshold: 20

charge_battery:
  alias: "Charge battery"
  sequence:
    - service: battery_planner.charge
      data:
        battery_soc: "{{ (states('sensor.battery_state_of_charge')|float) | round(1) }}"
        power: 3000
```
