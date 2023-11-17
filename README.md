# PondAutomation
A collaboration for the development of an automated algae pond. This github repository serves as both the knowledge base of the system as well as the code backend. 

Each github 'branch' represents a different phase of the project. You can select which 'Phase' of the project you would like to view the code for in the dropdown above. 

### File Structure
`PondAutomation/`
|`configs/` contains configurations needed to run the system  
| `data/` upon running the script, outputs are stored here  
| |---- `DATETIME/`  
| | |---- `pond_settings_used.csv` contains the configurations used  
| | |---- `DATETIME_sensor_data` contains sensor measurements (future work)  
| `functions/` contains the scripts that run on the raspberry pi for operation  
| `graphics/` contains diagrams and photos, some of which are used in this guide  
`automate_pond.py` is the single script that needs to be run by the user, it controls the entire process  

### System Requirements
The following describes the platform the code runs on, other configurations have not been tested
- RaspberryPi 4B
- python3

Python Libraries
- standard libraries
- RPi.GPIO library, which should come pre-installed on standard Raspbian OS systems


### Accessing the Code
If you are new to git and plan to use its features, you should see this [beginner guide](https://medium.com/@PhilParisi/getting-started-with-github-for-people-who-hate-github-1f25b071930d) (amongst others). 

If you plan to edit code and contribute to this project, you should clone the repository `git clone https://github.com/PhilParisi/PondAutomation`.

If you simply want a local copy of the code to play around with, you can either clone (like above) or click the green `Code` button and `Download ZIP` to your local system.


# Phase I - Drain n' Fill Prototype
Goal: develop the simplest form of an automated drain and fill system. 

In this case, we aren't fully draining the tank. We are simply allowing new water to enter the system and overflow into the overflow bin. 


## Schematic
The below schematic shows the wiring of electrical components and application.
![Pond Schematic](graphics/pond_schematic.png)

## Running the Program
1. Ensure this repository is present on your system (either clone or copied)
2. Ensure physical setup matches schematic (TODO: you can adjust your RPi GPIO inputs in the `configs/rpi_connections.py` file)
3. Connect to the RPi (wifi or ethernet connection + remote desktop or SSH)
4. Open a command line or terminal
5. Navigate into the project folder that contains this code, likely `cd PondAutomation`
6. Launch the automation file with `python3 automate_pond.py`
7. Answers any questions the scripts as for
8. Program should run!
9. Use CTRL+C to kill the program


## Operation and Failure Modes

The solenoid is **normally closed**, which means:
  - In a 'flood' emergency, **stop** the flow of water by unplugging the RPi or Solenoid (either one should cause the flow the stop)
  - In a 'no flow' emergency, you can try: resetting the RPi, consulting the programmer, providing water manually  

### Inputs

### Outputs
- the solenoid is programmed to open and close at intervals set in the 'Inputs' section
- data is written to .csv files in the 

## Key Hardware
1. RaspberryPi 4B (2GB RAM)
2. Relay
3. Solenoid (6-12V)
4. Breadboard w/ Diode


## State Transition Diagram
Below is the state transition diagram which describes the behavior of the system, and how the program transitions to different states. This is also called the 'control flow'. 
![state transition diagram](graphics/pond_statetransition.png)



# Phase II -



# Phase III - 
