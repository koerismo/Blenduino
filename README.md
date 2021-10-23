# Blenduino
A blender plugin that adds animate-able Arduino digital output (with PWM) integration.

## Requirements
- PyFirmata
- Blender 2.9+

## Instructions
1. Run the following command in console: `<BLENDER INSTALL DIRECTORY>/python/bin/python<VERSION NUMBER>.exe -m pip install pyfirmata`
2. Install the addon through Blender's settings.
3. Navigate to any object's properties, go to the Arduino Integration section, enter the device port, and connect to the device.
4. Set the object's pin number, and animate the pin value.
