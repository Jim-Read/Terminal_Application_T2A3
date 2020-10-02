import requests, json, os, xmltodict, time
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from rich import box, print
from rich.console import Console
from rich.table import Table
import PySimpleGUI as sg




# Clear screen function
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

#progress bar decorator for gui
def progress_bar_decorator(func):
    def inner(*args, **kwargs):
        for i in range(1, 300):
            sg.one_line_progress_meter('API calls', i+1, 300, 'key','Retrieving Information ... ', (50,50), orientation='h')
        returned = func(*args, **kwargs)
        return returned
    return inner



''' Menu class used to drive the application and have other features utilize class functions and return parameters as such and correct table '''



class Iss:

    @staticmethod
    def iss_current_co_ords():

        ''' Get response from API and make it readible in python via JSON, create a new list from dict value and
        extract the information needed and store in a new dictionary and return as parameters'''

        # test to confirm API is up for ISS location
        url_for_current_position = "http://api.open-notify.org/iss-now.json"
        try:
            response = requests.get(url_for_current_position)
            iss_info = response.json()
        except:
            print('\nThe API is currently down - Press try again later')

        # create new dictionary with required values needed from API json response
        convert_list = [value for key, value in iss_info.items() if key == 'iss_position']
        parameters = {}
        for co_ords in convert_list:
            for key, value in co_ords.items():
                if key == 'latitude':
                    parameters[key] = value
                elif key == 'longitude':
                    parameters[key] = value
        # return dict with lat and long of current iss position
        return parameters  # {'longitude': '-40.0998', 'latitude': '-47.3693'}


    def get_timezone_location(parameters):
        url = f"http://api.geonames.org/timezoneJSON?formatted=true&lat={parameters['latitude']}&lng={parameters['longitude']}&username=coder_academy_jim"
        response = (requests.get(url)).json()  
        ## Make a request and convert from json to dictionary
        for key, value in response.items():

            if key == 'timezoneId':      # {
                parameters[key] = value  # 'timezoneId': 'Australia/Melbourne',
            if key == 'time':            # 'countryName': 'Australia',
                parameters[key] = value  # 'time': '2020-09-25 00:19'
            if key == 'countryName':     # }
                parameters[key] = value

            elif len(response) == 5: # key !='timezoneId' or 'timecountry' or 'name':
                parameters['timezoneId'] = "N/A"
                parameters['time'] = "N/A"
                parameters['countryName'] = "N/A"
        return parameters


    def location_of_iss_at_input(parameters):

        ''' Checking to see if iSS over land or water, if over land a location key is given and name key is given if over water '''

        #create new dictionary and add lat/long and location key if over land - return as variable
        try:                                                                                             # {
            geolocator = Nominatim(user_agent="check_if_over_water_or_not")                              # 'longitude': '22.4747',
            location = geolocator.reverse(f"{parameters['latitude']}, {parameters['longitude']}")        # 'latitude': '10.8322',
            parameters['location'] = location                                                            # 'location': Location(Vakaga,(9.8250502, 22.376363, 0.0))
            parameters['longitude'] = parameters['longitude']                                            # }
            parameters['latitude'] = parameters['latitude']
            return parameters

        #if ISS over water, from API get xml file of waters and parse that and return name key in the dictionary instead and returns that
        except:
            print('\n The ISS is not currently over any land\n\n Gathering Information .....')
            time.sleep(0.2)
            # Test if the API is up
            try:
                response = requests.get(f"http://api.geonames.org/ocean?lat={parameters['latitude']}&lng={parameters['longitude']}&username=coder_academy_jim")
                dict = json.loads(json.dumps(xmltodict.parse(response.text)))  #{'geonames': {'ocean': {'geonameId': '4030875', 'name': 'North Pacific Ocean', 'distance': '0'}}}
            except:
                print('\nThe API is currently down - Please try again')

            for key, value in dict.items():
                for key, value in value.items():
                    for key, value in value.items():  # {
                        if key == 'name':  # 'name': 'South Atlantic Ocean', convert to location to make life easier
                            parameters['location'] = value
            return parameters


    ''' Get user input - check location with GEOPY and return dictionary '''

    def get_user_location():
        parameters = {}
        geolocator = Nominatim(user_agent="test")
        while_true = True
        while while_true:
            address = input('\nEnter an address, suburb, town, location: ')
            cls()
            try:
                location = geolocator.geocode(address)  # {
                parameters['latitude'] = location.latitude  # 'latitude': -37.8142176,
                parameters['longitude'] = location.longitude  # 'longitude': 144.9631608,
                parameters['location'] = location.address  # 'location': 'City of Melbourne, Victoria, Australia'
                while_true = False  # }
            except:
                input('\nNothing could be found - Try again - Press Enter to continue')
                cls()
        return parameters


    ''' Same thing for terminal app - get users location but in gui that requres a pop up as there is no term window takes address arguement '''

    def get_user_location_gui_popup(address):
        parameters = {}
        geolocator = Nominatim(user_agent="test")
        while_true = True
        while while_true:
            cls()
            try:
                location = geolocator.geocode(address)  # {
                parameters['latitude'] = location.latitude  # 'latitude': -37.8142176,
                parameters['longitude'] = location.longitude  # 'longitude': 144.9631608,
                parameters['location'] = location.address  # 'location': 'City of Melbourne, Victoria, Australia'
                while_true = False  # }
            except:
                sg.Popup('Nothing could be found - Try again')
                break
        return parameters


    ''' checks the users location input and iss and then checks the approx pass time '''

    def get_pass_times_at_location(parameters):
        iss_co_ords = Iss.iss_current_co_ords()
        iss_co_ords_with_location = Iss.location_of_iss_at_input(iss_co_ords)
        iss_location_with_timezone = Iss.get_timezone_location(iss_co_ords_with_location)
        rise_times = []
        times = []
        response = requests.get(f"http://api.open-notify.org/iss-pass.json?lat={parameters['latitude']}&lon={parameters['longitude']}")
        pass_times = response.json()['response']
        for passes in pass_times:
            time = passes['risetime']
            rise_times.append(time)
        for risetime in rise_times:
            time = datetime.fromtimestamp(risetime)
            times.append(time)
        parameters['times'] = times
        parameters['iss'] = iss_location_with_timezone
        return parameters


    ''' Takes user input - and checks the iss adn runs another call through geopy geodesic to get distance '''


    def measure_distance(parameters):
        iss_co_ords = Iss.iss_current_co_ords()
        iss_co_ords_with_location = Iss.location_of_iss_at_input(iss_co_ords)
        iss_location_with_timezone = Iss.get_timezone_location(iss_co_ords_with_location)

        co_ords_location = []
        co_ords_iss = []

        for key, value in iss_co_ords_with_location.items():
            if key == "latitude":
                co_ords_iss.insert(0, value)
            if key == "longitude":
                co_ords_iss.append(value)

        for key, value in parameters.items():
            if key == "latitude":
                co_ords_location.insert(0, value)
            if key == "longitude":
                co_ords_location.append(value)

        distance = geodesic(co_ords_location, co_ords_iss).kilometers.__round__()
        parameters['iss'] = iss_location_with_timezone
        parameters['distance'] = distance
        return parameters



''' Astronaut class to call astros endpoint and return dictinary results and return them on terminal or gui'''

class Astronaut:

    def get_astro():
        try:
            astro_call = requests.get("http://api.open-notify.org/astros.json")
            iss_astros = astro_call.json()
            num = 1
            with open('astros.txt', 'w') as astro_file:
                for person in iss_astros['people']:
                    astro_file.write("\n")
                    astro_file.write(f' {(num)} - ' + person['name'])
                    astro_file.write("\n")
                    num += 1
            print('\n Gathering information...')
            time.sleep(1)
            with open('astros.txt', 'r') as astros:
                astros = astros.read()

            table = Table(title="")
            table.add_column("Current Astronauts on the ISS", justify="left", style="cyan", no_wrap=True)
            table.add_row(astros)
            console = Console()
            console.print(table)
        except:
            print('The API is not callable - try again later')

    @progress_bar_decorator
    def gui_astros():
        astro_call = requests.get("http://api.open-notify.org/astros.json")
        iss_astros = astro_call.json()
        num = 1
        with open('astros.txt', 'w') as astro_file:
            for person in iss_astros['people']:
                astro_file.write("\n")
                astro_file.write(f' {(num)} - ' + person['name'])
                astro_file.write("\n")
                num += 1
        print('\n Gathering information...')
        time.sleep(1)
        with open('astros.txt', 'r') as astros:
            astros = astros.read()
        return astros



''' Tables created with Rich, variables are called and these are used to display information to the terminal only '''


class Display_tables:

    ''' returns the current location of iss table '''

    def return_iss_location():
        #get informaiton about iss
        iss_co_ords = Iss.iss_current_co_ords()
        iss_co_ords_with_location = Iss.location_of_iss_at_input(iss_co_ords)
        iss_location_with_timezone = Iss.get_timezone_location(iss_co_ords_with_location)  # adds timezone if availe to iss dict

        #build table and populate 
        table = Table(title="Current ISS location")
        table.add_column("Time Zone", justify="center", style="cyan", no_wrap=True)
        table.add_column(f"Location", justify="center", style="magenta")
        table.add_column("latitude", justify="left", style="green")
        table.add_column("longitude", justify="left", style="green")

        table.add_row(f"Zone: {iss_location_with_timezone['timezoneId']}\nCountry:{iss_location_with_timezone['countryName']}\nLocal time: {iss_location_with_timezone['time']}",
                      f"{iss_location_with_timezone['location']}",
                      f"{iss_location_with_timezone['latitude']}", f"{iss_location_with_timezone['longitude']}")

        console = Console()
        return console.print(table)


    ''' returns the current pass times of iss table at user location '''

    def display_pass_times_at_location():

        print('\n')
        user_loc = Iss.get_user_location()
        # gets users lat/lon/location
        user_loc_with_timez = Iss.get_timezone_location(user_loc)  # get timezone and add to users dictionary latest file
        loc_passtimes = Iss.get_pass_times_at_location(user_loc_with_timez)
        passtimes = loc_passtimes['times']

        # Build table to display content

        table = Table(title="Times and Dates of Next Approx ISS Flyovers At Location")

        table.add_column("Time Zone", justify="center", style="cyan", )
        table.add_column("Next 5 Passes", justify="center", style="cyan", no_wrap=True)
        table.add_column("Location", justify="center", style="magenta")
        table.add_column("latitude", justify="centre", style="green")
        table.add_column("longitude", justify="centre", style="green")

        if len(passtimes) == 4:
            table.add_row(f"Zone: {user_loc_with_timez['timezoneId']}\nCountry:{user_loc_with_timez['countryName']}\nLocal time: {user_loc_with_timez['time']}",f"{passtimes[0]}\n{passtimes[1]}\n{passtimes[2]}\n{passtimes[3]}\n N/A",
                          f"{user_loc_with_timez['location']}", f"{user_loc_with_timez['latitude']}",
                          f"{user_loc_with_timez['longitude']}")
        else:
            table.add_row(f"Zone: {user_loc_with_timez['timezoneId']}\nCountry:{user_loc_with_timez['countryName']}\nLocal time: {user_loc_with_timez['time']}",f"{passtimes[0]}\n{passtimes[1]}\n{passtimes[2]}\n{passtimes[3]}\n{passtimes[4]}\n",
                          f"{user_loc_with_timez['location']}",
                          f"{user_loc_with_timez['latitude']}",
                          f"{user_loc_with_timez['longitude']}")

        console = Console()
        return console.print(table)


    ''' returns the current distance table of location to iss '''

    def display_distance():

        user_location = Iss.get_user_location()
        user_loc_with_timez = Iss.get_timezone_location(user_location)
        distance_from_l_iss = Iss.measure_distance(user_loc_with_timez)

        table = Table(title="Distance Between User Location and ISS\n")
        table.add_column("Time Zone", style="cyan")
        table.add_column("Location", justify="center", style="magenta")
        table.add_column("latitude", justify="center", style="green")
        table.add_column("longitude", justify="center", style="green")
        table.add_column("Distance From Local To ISS", justify="right", style="green")

        table.add_row(f"ISS\nZone: {distance_from_l_iss['iss']['timezoneId']}\nCountry: {distance_from_l_iss['iss']['countryName']}\nLocal Time: {distance_from_l_iss['iss']['time']}",
                      f"{distance_from_l_iss['iss']['location']}", f"{distance_from_l_iss['iss']['latitude']}", f"{distance_from_l_iss['iss']['longitude']}")

        table.add_row("------------", "------------", "------------", "------------")

        table.add_row(
            f"Local\nZone: {distance_from_l_iss['timezoneId']}\nCountry: {distance_from_l_iss['countryName']}\nLocal Time: {distance_from_l_iss['time']}",
            f"{distance_from_l_iss['location']}", f"{distance_from_l_iss['latitude']}",
            f"{distance_from_l_iss['longitude']}",f'{distance_from_l_iss["distance"]} kms')


        console = Console()
        return console.print(table)


    ''' returns the current location of iss for the gui application '''

    @progress_bar_decorator
    def gui_iss_info():
        iss_co_ords = Iss.iss_current_co_ords()
        iss_co_ords_with_location = Iss.location_of_iss_at_input(iss_co_ords)
        iss_location_with_timezone = Iss.get_timezone_location(iss_co_ords_with_location)  # adds timezone if availe to iss dict
        return iss_location_with_timezone



''' GUI class to run the front end and make calls to the ISS and Astronaut class '''

class Gui:

''' Create the GUI Front end and populate buttons, fields etc '''

    @progress_bar_decorator
    def make_gui():

        #create theme, layout and define window propteries

        sg.theme('Darkblack')
        tab1_layout =  [[sg.T('ISS',)], [sg.T('Location:', size=(8,1)), sg.T('',key='-iss_location-', size=(80,1),background_color='white', text_color='black')], [sg.T('Country:', size=(8,1)), sg.T('',key='-iss_countryName-', size=(80,1),background_color='white', text_color='black')], [sg.T('Time Zone:'), sg.T('',key='-iss_timezoneId-', size=(80,1),background_color='white', text_color='black')], [sg.T('Time/Date:'), sg.T('',key='-iss_time-', size=(80,1),background_color='white', text_color='black')], [sg.T('Latitude:', size=(8,1)), sg.T('', size=(8,1), key='-iss_lat-',background_color='white', text_color='black'),sg.T('Longitude', size=(8,1)), sg.T('', size=(7,1), key='-iss_lon-',background_color='white', text_color='black')], [sg.T(''), sg.T('')], [sg.T('Input Location:')], [sg.T('Address:', size=(8,1)), sg.T('', size=(80,1), key='-local_location-',background_color='white', text_color='black')], [sg.T('Country:', size=(8, 1)), sg.T('', size=(80,1),key='-local_countryName-',background_color='white', text_color='black')], [sg.T('Time Zone:', size=(8,1)), sg.T('', size=(80,1),key='-local_timezoneId-',background_color='white', text_color='black')], [sg.T('Time/Date', size=(8,1)), sg.T('', size=(80,1),key='-local_time-',background_color='white', text_color='black')], [sg.T('Latitude:', size=(8,1)), sg.T('', size=(7,1),key='-local_latitude-',background_color='white', text_color='black'),sg.T('Longitude', size=(7,1)), sg.T('', size=(7,1),key='-local_longitude-',background_color='white', text_color='black')], [sg.T('Distance', size=(8,1)), sg.T('', key="-iss_distance-", size=(10,1),background_color='white', text_color='black')], [sg.Image(filename='../tttttttttttttttttttttt/HDEV3.png', size=(1000, 350))]]


        layout = [[sg.TabGroup([[sg.Tab('Iss Locator', tab1_layout, tooltip='tip', element_justification='center')]])],
                  [sg.Button('ISS'), sg.Button('Astronauts'), sg.Button('Passes'), sg.Button('Measure'),sg.Button('Help'), sg.Button('About'), sg.Button('Clear'), sg.Button('Exit')]]

        window = sg.Window('My window with tabs', layout, default_element_size=(80,800))

        #create loop that constantly checks for user input/button presses/etc

        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                window.close()  # destoy window and break loop - return to terminal menu
                break

            if event == 'ISS':  # update all fields on screen - keys match text outputs
                iss_info = Display_tables.gui_iss_info()
                window['-iss_location-'].update(f"{iss_info['location']}")
                window['-iss_countryName-'].update(f"{iss_info['countryName']}")
                window['-iss_timezoneId-'].update(f"{iss_info['timezoneId']}")
                window['-iss_time-'].update(f"{iss_info['time']}")
                window['-iss_lat-'].update(f"{iss_info['latitude']}")
                window['-iss_lon-'].update(f"{iss_info['longitude']}")


            if event == 'Passes':  # pop asks user for input - checked and updates all fields - pop up times
                geolocator = Nominatim(user_agent="test")
                address = sg.popup_get_text('Enter an address, suburb, town, location')
                try:
                    location = geolocator.geocode(address)
                    user_local = Iss.get_user_location_gui_popup(address)
                    pass_times = Iss.get_pass_times_at_location(user_local)
                    time_zones = Iss.get_timezone_location(user_local)
                    distance = Iss.measure_distance(time_zones)

                    window['-local_location-'].update(f"{time_zones['location']}")
                    window['-local_countryName-'].update(f"{time_zones['countryName']}")
                    window['-local_timezoneId-'].update(f"{time_zones['timezoneId']}")
                    window['-local_time-'].update(f"{time_zones['time']}")
                    window['-local_latitude-'].update(f"{time_zones['latitude']}")
                    window['-local_longitude-'].update(f"{time_zones['longitude']}")

                    window['-iss_location-'].update(f"{time_zones['iss']['location']}")
                    window['-iss_countryName-'].update(f"{time_zones['iss']['countryName']}")
                    window['-iss_timezoneId-'].update(f"{time_zones['iss']['timezoneId']}")
                    window['-iss_time-'].update(f"{time_zones['iss']['time']}")
                    window['-iss_lat-'].update(f"{time_zones['iss']['latitude']}")
                    window['-iss_lon-'].update(f"{time_zones['iss']['longitude']}")
                    #after all fields on scren are updated, pass times pops up on screen
                    sg.popup(f'\nThe next 5 Passes at Location:\n\n1st -  {time_zones["times"][0]}\n2nd - {time_zones["times"][1]}\n3rd -  {time_zones["times"][2]}\n4th -  {time_zones["times"][3]}\n5th -  {time_zones["times"][4]}\n\n', title="Next 5 Passes", line_width=120)
                    window['-iss_distance-'].update(f"{distance['distance']} kms")
                except:  #sometimes some locations have 4 times - usualy because the iSS just passed recently
                    window['-iss_distance-'].update(f"{distance['distance']} kms")
                    sg.popup(f'\n          The next 4 Passes at Location:\n1st -  {time_zones["times"][0]}\n2nd - {time_zones["times"][1]}\n3rd -  {time_zones["times"][2]}\n4th -  {time_zones["times"][3]}', title="Next 4 Passes", line_width=120)



            if event == 'Measure':  #pop up asks for user input - checks this - gets iss information and measures - updates all fields on the screen
                geolocator = Nominatim(user_agent="test")
                address = sg.popup_get_text('Enter an address, suburb, town, location')
                try:
                    location = geolocator.geocode(address)
                    user_local = Iss.get_user_location_gui_popup(address)
                    pass_times = Iss.get_pass_times_at_location(user_local)
                    time_zones = Iss.get_timezone_location(user_local)
                    distance = Iss.measure_distance(time_zones)

                    window['-local_location-'].update(f"{distance['location']}")
                    window['-local_countryName-'].update(f"{distance['countryName']}")
                    window['-local_timezoneId-'].update(f"{distance['timezoneId']}")
                    window['-local_time-'].update(f"{distance['time']}")
                    window['-local_latitude-'].update(f"{distance['latitude']}")
                    window['-local_longitude-'].update(f"{distance['longitude']}")

                    window['-iss_location-'].update(f"{distance['iss']['location']}")
                    window['-iss_countryName-'].update(f"{distance['iss']['countryName']}")
                    window['-iss_timezoneId-'].update(f"{distance['iss']['timezoneId']}")
                    window['-iss_time-'].update(f"{distance['iss']['time']}")
                    window['-iss_lat-'].update(f"{distance['iss']['latitude']}")
                    window['-iss_lon-'].update(f"{distance['iss']['longitude']}")

                    window['-iss_distance-'].update(f"{distance['distance']} kms")
                except:
                    sg.popup_error('There was no connection to API')



            if event == 'Astronauts':  # Astros endpoint is called and a pop up displays who is on board
                try:
                    astros_on_iss = Astronaut.gui_astros()
                    sg.popup(f'Astronauts onboard ISS\n{astros_on_iss}', title="Astronauts", line_width=150)
                except:
                    sg.popup_error('There was no connection to API')


            if event == "Help":  # Help file is called and a pop up with the contents is displayed
                with open('help.txt', 'r') as file:
                    help_file = file.read()
                sg.popup(f'{help_file}', title="Help", line_width=150)

            if event == "About":  # ABout file is called and a pop up with the contents is displayed
                with open('about.txt', 'r') as file:
                    about_file = file.read()
                sg.popup(f'{about_file}', title="Help", line_width=150)
            

            if event == "Clear":  # Clear event will remove all values on the screen to empty strings
                window['-local_location-'].update("")
                window['-local_countryName-'].update("")
                window['-local_timezoneId-'].update("")
                window['-local_time-'].update("")
                window['-local_latitude-'].update("")
                window['-local_longitude-'].update("")

                window['-iss_location-'].update("")
                window['-iss_countryName-'].update("")
                window['-iss_timezoneId-'].update("")
                window['-iss_time-'].update("")
                window['-iss_lat-'].update("")
                window['-iss_lon-'].update("")
                window['-iss_distance-'].update("")




''' Menu class used to drive the terminal app, calls are made to ISS class to get data like object through dict of operations '''


class Menu:

''' create a dictionary of operation for the user to select '''

    def __init__(self):
        self.operations = {
            'current': Display_tables.return_iss_location,
            'astros': Astronaut.get_astro,
            'get': Display_tables.display_pass_times_at_location,
            'measure': Display_tables.display_distance,
            'help': Menu.help_text,
            'about': Menu.help_text,
            'gui': Gui.make_gui }


''' define the actual persistant menu that will be underneath all applications - even when gui is quit - returns to this - 1-8 selections '''


    def menu(self):
        print('\n')
        menu_start = True
        while menu_start:  # Draw menu to screen via rich tables
            table = Table(title="")

            table.add_column("Menu", justify="left", style="magenta")

            table.add_row("\n What do you want to do:\n\n (1) Show current ISS position\n (2) Show current Astronauts on board\n (3) Get time ISS passes at location\n (4) Measure distance between location and ISS\n (5) Help\n (6) About\n (7) Quit\n (8) Gui TEST\n")
            console = Console()
            console.print(table)

            operation = input('Select an option: ')

            try:  # Try all selections and if any thing is wrong - catch all - repeat menu
                if operation.strip() == '1':  #  option gets the relevant object and then calls on it when needed
                    current = self.operations.get('current')
                    current()
                elif operation.strip() == '2':
                    astros = self.operations.get('astros')
                    astros()
                elif operation.strip() == '3':
                    get = self.operations.get('get')
                    get()
                elif operation.strip() == '4':
                    measure = self.operations.get('measure')
                    measure()
                elif operation.strip() == '5':
                    help = self.operations.get('help')
                    help()
                elif operation.strip() == '6':
                    about = self.operations.get('about')
                    about()
                elif operation.strip() == '7':
                    exit()
                elif operation.strip() == '8':
                    gui = self.operations.get('gui')
                    gui()
                else:
                    input("Please select an option between 1 - 8\nPress Enter to Continue\n")
                    cls()
                    print()
            except:
                Menu.menu(self)

    ''' Help and ABout files needd to be displayed to window '''

    @staticmethod
    def help_text():
        cls()
        with open('help_file.txt', 'r') as help_file:
            print(help_file.read())
        input('Press enter')
        return Menu.menu()

    @staticmethod
    def about_text():
        cls()
        with open('about.txt', 'r') as help_file:
            print(help_file.read())
        input('Press enter')
        return Menu.menu()






