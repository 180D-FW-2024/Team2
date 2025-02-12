# Team2

Please check demo_final_code for the most updated versions of the integrated code!



command.txt explains how to run it


![1021739348227_ pic](https://github.com/user-attachments/assets/cb48981d-76cc-447c-9b9b-7caabc84eed1)

SoleMate is a shoe asseccory structured navigation system comprising two main components: SoleMate-hand and SoleMate-shoe, each powered by a Raspberry Pi 4.

### System Components
**SoleMate-hand**
- Features a Raspberry Pi 4 as a voice control interface
- Integrates with Google Maps and GPS module
- Processes voice commands for destination input
- Provides voice output for navigation instructions
- Transmits real-time directional data to SoleMate-shoe


**SoleMate-shoe**
- Utilizes a Raspberry Pi 4 mounted on a shoe cover
- Incorporates 6 vibration motors for directional feedback
- Includes an IMU for orientation sensing
- Features a camera for obstacle detection
- Processes fall detection through IMU sensors

  
### Functionality
The system operates through a coordinated workflow where SoleMate-hand receives user voice
commands and determines the route using GPS and Google Maps integration. This information
is transmitted to SoleMate-shoe, which uses the IMU to compare the intended direction with the
user's current foot orientation. The vibration motors then activate to guide the user in the correct
direction.

### Safety Features
- Real-time obstacle detection and avoidance through camera monitoring
- Automatic rerouting when obstacles are detected
- Emergency alert system for fall detection
- Turn-by-turn navigation with haptic feedback
