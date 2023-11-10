# PondAutomation
A collaboration for the development of an automated algae pond. This github repository serves as both the knowledge base of the system as well as the code backend. 

Each github 'branch' represents a different phase of the project. You can select which 'Phase' of the project you would like to view the code for in the dropdown above. 

### Folders
`pi_code` contains the scripts that run on the raspberry pi for operation
`config` contains configurations needed to run the system, this is where the users should update parameters such as `flood time` and `period between floods`
`data` contains the recorded sensor data and other useful information
`photos` contains photographs, screenshots, and other related media

# Phase I - Drain n' Fill Prototype
Goal: develop the simplest form of an automated drain and fill system. 

In this case, we aren't fully draining the system. We are simply allowing new water to enter the system and overflow into the overflow bin. 


## Schematic


## Setup (User Guide)

1. 
1. Set the inputs


## Operation and Failure Modes

1. Set the inputs

2. The solenoid is **normally closed**, which means:
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

## Computing
The RPi 

## State Transition Diagram

## Bill of Materials


## Photos




# Phase II -



# Phase III - 
