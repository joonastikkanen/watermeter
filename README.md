# Raspberry PI Watermeter using camera

NOT FULLY TESTED YEAT!!

I was inspired by old project nohn's project about using raspberry PI camera as to bring smartness to old school watermeter. I also added tensorflow to analyze the images from jomjols's project.

Links:
* The nohn's project: https://github.com/nohn/watermeter/tree/main
* The jomjols project: https://github.com/jomjol/water-meter-system-complete

## HomeAssistant sensor

```yaml
sensor:
  - platform: rest
    name: Water
    resource: "http://ip.or.hostname.of.watermeter:3000/"
    scan_interval: 60
    unit_of_measurement: 'm³'
    device_class: water
    state_class: total_increasing
```
