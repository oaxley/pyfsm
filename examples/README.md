 This two examples use the amtFSM library to simulate the Bendix/King NAVCOM (KY196).  
You can have a view [here](http://avionicsmasters.com/avionics/comms/bendix-king-ky-196.html).  
The frequency range for this kind of hardware is between 118.000 MHz and 135.975 MHz.

The following commands are supported:
- o: put the COM module ON or OFF
- q: increase the frequency by 1MHz
- a: decreaser the frequency by 1MHz
- w: increase the frequency by 25kHz
- s: decrease the frequency by 25kHz
- u: swap active and standby frequencies

Use CTRL+C to exit the program.

**comradio-2.py** uses the external YAML file to initialize the FSM.