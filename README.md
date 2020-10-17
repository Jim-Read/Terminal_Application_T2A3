# JimRead_T2A3 - ISS Tracker

A python terminal application that tracks the ISS, you can get passtimes, location of ISS, measure distance and get who is on board 
There is also a GUI version of the application

### Instructions and Help

> Python must be installed on the system preferebly 3.7 or higher.
> Clone repository to machine.
>pip install -r requirements

The GUI can be launched from the terminal instead of using the menu system
```
.python main.py --gui
```
```
--help will display the usage and some help content
```

### Application Purpose and Scope

>> Develop and describe an algorithmic solution for an application that utilises two way communication over a network (300 - 500 words)

The application I have created monitors and tracks the International Space Station in real time.  Not only its present position is gathered via the Open Notify API calls, more information is pulled on its location through the geopy python library which links to google street maps API and if over land, gets the current data and time, time zone and country and address OR it will find the body of water it is currently over.  Also, the user can check a location and find out the next 5 pass times of the ISS over that location, estimated time is given of a Passover.  The user can also measure the distance between their chosen location and the ISS currently in orbit.  Utilizing these concepts, I have developed a terminal application around solving these issues one could have when wanting to view, see, or check where the ISS could be at any given time.

Users are asked to enter an address, location or place of interest and a check will be made if its valid or not and return a result that will be used to check for more attributes, this is the same for when measuring distances.  By asking for user input, it allowed the application more functionality than just the standard calls.  
ISS, astronaut, menu, display tables and GUI classes were created to solve this issue, the Menu class has a persistent menu function object while loop created in Rich tables that runs on terminal, all menu options are 1-8 with only numerical input allowed.  All menu options – except quit, will default back to the main menu after completion.  User input is requested in pass times and measure options.  Help and about files are already created and pulled form root and displayed to screen.  About works similar – file on root being read to screen. User input is required to progress back to the main menu.   All menu options are driven by a dictionary which stores the class object methods and runs when called.
The Astronaut class contains methods within that make calls to the open notify API -  astro endpoint and a dictionary is received.  This is then parsed through json and stored in a file on the root, and read back in a created rich table display, which loops back to the main menu.  In the GUI front end – this is a pop up ontop of the main window.

ISS class was created to handle the bulk of the work the application does.  Many methods were created to achieve this.  First a call to Open Notify API was needed to get the coordinates, another method was created to use these co ordinates and return the location through the use of geopy python library which uses API calls to get location info from co ords.  This dictionary given is updated and returned.  Another method was created to take in a dictionary of parameters(co ords and location) and checks it for the current time zone – this updates the given dictionary and returns the updated one.  This can be used however we need in displaying content – be it current ISS position or used for measuring and pass times.  Measuring method takes in user input first, if unsuccessful it will prompt user to keep trying – input is not strict, one-word address work, but will use the first address it finds so being specific helps.  This method takes in an updated dictionary – a method is run to get the users location – this is checked over geopy and a dictionary is created and updated and returned – this is used in the measure and pass time functions – which take them in and get updated with the relevant information be it the distance or the next 5 passes at location.  These functions utilise input, get updated and returned to be used in displaying the content to screen.   

Display tables class is pretty straight forward, back end code designed to take in the outputs of the ISS class methods and applies them in a readable format for terminal window. Rich tables python library used for this; the methods created in this class are for each option in the menu.  Each call takes the output of the called upon users actions and displays it in some readable way.  

GUI class creates a window outside of the terminal that has the same functionality or the terminal application, with small changes.  A function for how to handle input, displaying the help/about and astronauts was created to address these changes as the GUI is driven by mouse clicks and keyboard input.   The GUI window function is needed to create the window, create the display(buttons content, etc) and then add the functionality to it.  All buttons have a function or call assigned to it, as the GUI function has an event menu driven to keep the application running, this is achieved with a while loop, the terminal while loop menu is still running as well – quitting the GUI throws you back into the terminal app menu.   The GUI method receives output when a button is clicked – the calls are made in the back ground using the ISS class and the GUI function updates the values on the screen.   When pass times button is clicked – a popup will appear asking for input – incorrect gives the error nothing can be found – or if successful all values will update and a popup with the next pastimes will appear.  This also will update all values on screen and included current distance from local to ISS.  Measure works similar – popup asking for input – and all values displayed to screen – no popups.  A clear option was created just to remove all values on screen.  

Python Libraries:
Rich - 7.0.0
Used to drive the display of the content to terminal window, the menu, all options a user could select use this to display whatever needed to the screen in a readable format. Other modules used in this library are, box, print console, tables, some colour.

Xmltodict – 0.12.0
When the ISS is checked through geopys street maps API calls, if it can’t find one, it will check its location to see if its over water, this gets returned as an xml file, this is used to convert it to a python dictionary.

Geopy – 2.0.0
Modules used – geopy.geocoders – Nominatim and geopy.distance – geodesic.  Nomination is used to parse the users input against the API calls it can make and returns the coordinates.  When checking for the location a reverse lookup is done and if unsuccessful a call is made to the ocean endpoint. Geoppy.distance – geodesic measure the distance between two coordinates and accounts for curvature of the Earth rather than a straight line and not the hypotenuse.

PySimpleGUI – 4.29.0
Python library that drives GUI development, used to create a launch screen that display labels and fields to store data, all standard use of buttons and flow were used/

Standard Python Library:
Requests  - requests~=2.24.0
Used to make API calls to end points. 

Json:
Used to parse requests from API calls into a readable python format and to be able to be used in a program

Os:
Usage only limited as a function to clear the screen

Time:
Sleep module is used to put in some delays

Datetime:
Used to convert UTC time to a readable format


### Features

- Track the ISS current location - gets timezone and location if over land or which body of water
- Get who is currently on board the ISS
- Get the next time the ISS passes over a location
- Measure the distance from any location on Earth to the ISS
- GUI Interface as well as the default Terminal 

![terminal1](/docs/JimRead_T2A3_term1.jpg)
![terminal1](/docs/JimRead_T2A3_term2a.jpg)
![terminal2](/docs/JimRead_T2A3_term2.jpg)
![terminal1](/docs/JimRead_T2A3_term2b.jpg)
![terminal3](/docs/JimRead_T2A3_term3.jpg)
![terminal4](/docs/JimRead_T2A3_gui1.jpg)
![terminal4](/docs/JimRead_T2A3_gui1a.jpg)
![terminal4](/docs/JimRead_T2A3_gui3ab.jpg)
![terminal5](/docs/JimRead_T2A3_gui2.jpg)
![terminal6](/docs/JimRead_T2A3_gui3.jpg)
![terminal7](/docs/JimRead_T2A3_gui4.jpg)

## Control Flow

![Control Flow Diagram](/docs/JimRead_T2A3-flowchart.png)


## Implementation Plan

![trello plan](/docs/JimRead_T2A3_START.jpg)
![trello plan](/docs/JimRead_T2A3_MIDDLE.jpg)
![trello plan](/docs/JimRead_T2A3_END.jpg)

## Testing

Created some tests that check the API is up and running when deployign via the CI/CD pipeline for automation, without these calls being alive the application will run but you will get prompts tha tthe API is down.  GUI will still load.  All buttons/options return the results.  All functions deemed working and erros handled. 

![CICD workflow](/docs/JimRead_T2A3-CDCD.jpg) 
![CICD workflow](/docs/JimRead_T2A3_TESTS.jpg) 
