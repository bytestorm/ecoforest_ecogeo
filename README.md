Ecoforest EcoGeo heat pump integration PoC WIP

![flow](https://github.com/bytestorm/ecoforest_ecogeo/blob/master/flow.png?raw=true)

```yaml
type: custom:power-flow-card-plus
entities:
  battery:
    state_of_charge: sensor.solarman_battery_soc
  grid:
    entity: sensor.ebfhbb_power_electric
    display_state: one_way_no_zero
    name: Consumption
    color:
      consumption:
        - 78
        - 122
        - 39
  solar:
    display_zero_state: true
  home:
    entity: sensor.ebfhbb_power_output
    icon: mdi:hvac
    subtract_individual: false
    override_state: true
    secondary_info:
      entity: sensor.ebfhbb_t_outdoor
      unit_of_measurement: °C
      decimals: 1
  individual:
    - entity: sensor.ebfhbb_power_cooling
      display_zero_state: false
      name: Cooling
      secondary_info:
        entity: sensor.ebfhbb_t_cooling
        unit_of_measurement: °C
        display_zero: false
        decimals: 1
      icon: mdi:snowflake
      display_zero: true
      color:
        - 0
        - 213
        - 255
    - entity: sensor.ebfhbb_power_heating
      display_zero: true
      name: Heating
      icon: mdi:heating-coil
      secondary_info:
        entity: sensor.ebfhbb_t_heating
        unit_of_measurement: °C
      color:
        - 203
        - 37
        - 37
      decimals: 1
      display_zero_state: false
    - name: DHW
      icon: mdi:water-boiler
      color:
        - 212
        - 154
        - 28
      decimals: 1
      display_zero: true
      secondary_info:
        entity: sensor.ebfhbb_t_dhw
        unit_of_measurement: °C
        decimals: 1
      display_zero_state: false
      entity: '0'
clickable_entities: true
display_zero_lines:
  mode: show
  transparency: 50
  grey_color:
    - 189
    - 189
    - 189
use_new_flow_rate_model: true
w_decimals: 0
kw_decimals: 1
min_flow_rate: 5
max_flow_rate: 5
max_expected_power: 2000
min_expected_power: 0.01
watt_threshold: 1000
transparency_zero_lines: 0
disable_dots: true
```
