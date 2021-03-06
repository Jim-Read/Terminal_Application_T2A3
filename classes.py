import requests, json, os, xmltodict, time
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from rich import box, print
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
import PySimpleGUI as sg


# Clear screen function
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


# progress bar decorator for gui
def progress_bar_decorator(func):
    def inner(*args, **kwargs):
        for i in range(1, 300):
            sg.one_line_progress_meter('API calls', i + 1, 300, 'key', 'Retrieving Information ... ',(50, 50),orientation='h')
        returned = func(*args, **kwargs)
        return returned

    return inner


# progress bar for terminal
def progress_bar_decorator_term(func):
    def inner(*args, **kwargs):
        cls()
        with Progress() as progress:
            task1 = progress.add_task("[red]Getting Resources...", total=1000)
            task2 = progress.add_task("[green]Building...", total=1000)
            task3 = progress.add_task("[cyan]Finalizing...", total=1000)
            while not progress.finished:
                progress.update(task1, advance=20)
                progress.update(task2, advance=17)
                progress.update(task3, advance=15)
                time.sleep(0.02)
        returned = func(*args, **kwargs)
        return returned

    return inner


""" 
ISS class used to drive the main functions behind the scenes to get the content ready -  checks iss co ords
user co ords, time zones, locations, pass times, distance.
"""


class Iss:

    ''' Calls the ISS API to get its correct co ordinates '''

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
        # {'longitude': '-40.0998', 'latitude': '-47.3693'}
        return parameters

    ''' Gets the time zone of either ISS or user location appends to dict'''

    @staticmethod
    def get_timezone_location(parameters):

        # Make a request and update dictionary
        url = f"http://api.geonames.org/timezoneJSON?formatted=true&lat={parameters['latitude']}&lng={parameters['longitude']}&username=coder_academy_jim"
        response = (requests.get(url)).json()

        for key, value in response.items():
            if key == 'timezoneId':      # {
                parameters[key] = value  # 'timezoneId': 'Australia/Melbourne',
            if key == 'time':            # 'countryName': 'Australia',
                parameters[key] = value  # 'time': '2020-09-25 00:19'
            if key == 'countryName':     # }
                parameters[key] = value
            # response is equal 5 items in the dictionary if no timezone can be found
            elif len(response) == 5:
                parameters['timezoneId'] = "N/A"
                parameters['time'] = "N/A"
                parameters['countryName'] = "N/A"
        return parameters

    ''' Checking to see if iSS over land or water, if over land a location key is given and name key 
    is given if over water checking with geonames API calls '''

    @staticmethod
    def location_of_iss_at_input(parameters):

        url = f"http://api.geonames.org/ocean?lat={parameters['latitude']}&lng={parameters['longitude']}&username=coder_academy_jim"
        # update dictionary and add lat/long and location key if over land - return as dictionary
        try:
            geolocator = Nominatim(user_agent="check_if_over_water_or_not")
            location = geolocator.reverse(f"{parameters['latitude']}, {parameters['longitude']}")
            parameters['location'] = location
            parameters['longitude'] = parameters['longitude']  # }
            parameters['latitude'] = parameters['latitude']
            return parameters

        # if ISS over water, from API get xml file of waters and parse that and return name/location key in the dictionary instead
        except:
            print('\n The ISS is not currently over any land\n\n Gathering Information .....')
            # Test if the API is up
            try:
                response = requests.get(url)
                dict = json.loads(json.dumps(xmltodict.parse(response.text)))
                # {'geonames': {'ocean': {'geonameId': '4030875', 'name': 'North Pacific Ocean', 'distance': '0'}}}
            except:
                print('\nThe API is currently down - Please try again')

            #check over the converted nested dictionary for name key and add it to params dictionary
            for key, value in dict.items():
                for key, value in value.items():
                    for key, value in value.items():  # {
                        if key == 'name':  # 'name': 'South Atlantic Ocean'
                            # convert to location to make life easier
                            parameters['location'] = value
            return parameters

    ''' Get user input - check location with GEOPY and return dictionary '''

    @staticmethod
    def get_user_location():

        parameters = {}
        geolocator = Nominatim(user_agent="test")
        while_true = True
        while while_true:
            address = input('\nEnter an address, suburb, town, location: ')
            cls()
            try:
                location = geolocator.geocode(address)      # {
                parameters['latitude'] = location.latitude  # 'latitude': -37.8142176,
                parameters['longitude'] = location.longitude# 'longitude': 144.9631608,
                parameters['location'] = location.address   # 'location': 'City of Melbourne, Victoria, Australia'
                while_true = False  # }
            except:
                input('\nNothing could be found - Try again - Press Enter to continue')
                cls()
        return parameters

    ''' Same thing for terminal app - get users location but in gui that requires a pop up as there is no term window, 
    takes address arguement '''

    @staticmethod
    def get_user_location_gui_popup(address):

        parameters = {}
        geolocator = Nominatim(user_agent="test")
        while_true = True
        while while_true:
            cls()
            try:
                location = geolocator.geocode(address)        # {
                parameters['latitude'] = location.latitude    # 'latitude': -37.8142176,
                parameters['longitude'] = location.longitude  # 'longitude': 144.9631608,
                parameters['location'] = location.address     # 'location': 'City of Melbourne, Victoria, Australia'
                while_true = False  # }
            except:
                sg.Popup('Nothing could be found - Try again')
                break
        return parameters

    ''' checks the users location input and iss and then checks the approx pass time '''

    @staticmethod
    def get_pass_times_at_location(parameters):

        iss_co_ords = Iss.iss_current_co_ords()
        iss_co_ords_with_location = Iss.location_of_iss_at_input(iss_co_ords)
        iss_location_with_timezone = Iss.get_timezone_location(iss_co_ords_with_location)
        rise_times = []
        times = []
        response = requests.get(
            f"http://api.open-notify.org/iss-pass.json?lat={parameters['latitude']}&lon={parameters['longitude']}")
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

    ''' Takes user input - and checks the iss and runs another call through geopy geodesic to get distance '''

    @staticmethod
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


''' Astronaut class to call astros endpoint and return dictionary results and return them on terminal or gui '''


class Astronaut:

    ''' Calls astro API and displays it to the terminal only - writes to file and RICH table displays '''

    def get_astro():

        cls()
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
            table.add_column("Current Astronauts on the ISS", justify="left", style="green", no_wrap=True)
            table.add_row(astros)
            console = Console()
            console.print(table)
            return input('\nPress Enter to continue')
        except:
            return input('\nThe API is not callable - try again later\n\nPress Enter to continue')



''' Tables created with Rich, variables are called and these are used to display information to the terminal only '''


class Display_tables:
    ''' returns the current location of iss table '''

    @progress_bar_decorator_term
    def return_iss_location():

        cls()
        # get information about iss
        iss_co_ords = Iss.iss_current_co_ords()
        iss_co_ords_with_location = Iss.location_of_iss_at_input(iss_co_ords)
        iss_location_with_timezone = Iss.get_timezone_location(iss_co_ords_with_location)

        # build table and populate
        print('\n')
        table = Table(title="Current ISS location")
        table.add_column("Time Zone", justify="center", style="cyan", no_wrap=True)
        table.add_column(f"Location", justify="center", style="magenta")
        table.add_column("latitude", justify="left", style="green")
        table.add_column("longitude", justify="left", style="green")

        table.add_row(
            f"Zone: {iss_location_with_timezone['timezoneId']}\nCountry:{iss_location_with_timezone['countryName']}\n"
            f"Local time: {iss_location_with_timezone['time']}",
            f"{iss_location_with_timezone['location']}",f"{iss_location_with_timezone['latitude']}",
            f"{iss_location_with_timezone['longitude']}")

        console = Console()
        console.print(table)
        return input('\nPress Enter to continue')


    ''' returns the current pass times of iss table at user location '''

    @progress_bar_decorator_term
    def display_pass_times_at_location():

        cls()
        print('\n')
        # gets users lat/lon/location
        user_loc = Iss.get_user_location()
        # get timezone and add to users dictionary
        user_loc_with_timez = Iss.get_timezone_location(user_loc)
        #get passtimes of iss at users location
        loc_passtimes = Iss.get_pass_times_at_location(user_loc_with_timez)
        #append list to dictionary under times key
        passtimes = loc_passtimes['times']

        # Build table to display content

        table = Table(title="Times and Dates of Next Approx ISS Flyovers At Location")

        table.add_column("Time Zone", justify="center", style="cyan", )
        table.add_column("Next 5 Passes", justify="center", style="white", no_wrap=True)
        table.add_column("Location", justify="center", style="magenta")
        table.add_column("latitude", justify="centre", style="green")
        table.add_column("longitude", justify="centre", style="green")

        # Location can sometimes have only 4 passes listed, meaning ISS just passed by recently
        if len(passtimes) == 4:
            table.add_row(
                f"Zone: {user_loc_with_timez['timezoneId']}\nCountry:{user_loc_with_timez['countryName']}\n"
                f"Local time: {user_loc_with_timez['time']}",
                f"{passtimes[0]}\n{passtimes[1]}\n{passtimes[2]}\n{passtimes[3]}\n N/A",
                f"{user_loc_with_timez['location']}", f"{user_loc_with_timez['latitude']}",
                f"{user_loc_with_timez['longitude']}")
        else:
            table.add_row(
                f"Zone: {user_loc_with_timez['timezoneId']}\nCountry:{user_loc_with_timez['countryName']}\n"
                f"Local time: {user_loc_with_timez['time']}",
                f"{passtimes[0]}\n{passtimes[1]}\n{passtimes[2]}\n{passtimes[3]}\n{passtimes[4]}\n",
                f"{user_loc_with_timez['location']}",
                f"{user_loc_with_timez['latitude']}",
                f"{user_loc_with_timez['longitude']}")

        console = Console()
        console.print(table)
        return input('\nPress Enter to continue')

    ''' returns the current distance table of location to iss '''

    @progress_bar_decorator_term
    def display_distance():

        cls()
        user_location = Iss.get_user_location()
        user_loc_with_timez = Iss.get_timezone_location(user_location)
        distance_from_l_iss = Iss.measure_distance(user_loc_with_timez)

        table = Table(title="Distance Between User Location and ISS\n")
        table.add_column("Time Zone", style="cyan")
        table.add_column("Location", justify="center", style="magenta")
        table.add_column("latitude", justify="center", style="green")
        table.add_column("longitude", justify="center", style="green")
        table.add_column("Distance From Local To ISS", justify="right", style="green")

        table.add_row(
            f"ISS\nZone: {distance_from_l_iss['iss']['timezoneId']}\nCountry: {distance_from_l_iss['iss']['countryName']}\n"
            f"Local Time: {distance_from_l_iss['iss']['time']}",
            f"{distance_from_l_iss['iss']['location']}", f"{distance_from_l_iss['iss']['latitude']}",
            f"{distance_from_l_iss['iss']['longitude']}")

        table.add_row("------------", "------------", "------------", "------------")

        table.add_row(
            f"Local\nZone: {distance_from_l_iss['timezoneId']}\nCountry: {distance_from_l_iss['countryName']}\n"
            f"Local Time: {distance_from_l_iss['time']}",
            f"{distance_from_l_iss['location']}", f"{distance_from_l_iss['latitude']}",
            f"{distance_from_l_iss['longitude']}", f'{distance_from_l_iss["distance"]} kms')

        console = Console()
        console.print(table)
        return input('\nPress Enter to continue')

    ''' returns the current location of iss for the gui application '''

    @progress_bar_decorator
    def gui_iss_info():

        iss_co_ords = Iss.iss_current_co_ords()
        iss_co_ords_with_location = Iss.location_of_iss_at_input(iss_co_ords)
        iss_location_with_timezone = Iss.get_timezone_location(iss_co_ords_with_location)
        return iss_location_with_timezone


''' GUI class to run the front end and make calls to the ISS and Astronaut class '''


class Gui:
    ''' Create the GUI Front end and populate buttons, fields etc '''

    @progress_bar_decorator_term

    def make_gui():

        # create theme, layout and define window properties
        # create buttons/labels on tab layout

        sg.theme('Darkblack')

        tab_layout = [[sg.T('ISS', justification='center', size=(80, 1), background_color='gray', text_color='white')],
                       [sg.T('Location:', size=(8, 1)),sg.T('', key='-iss_location-', size=(80, 1), background_color='black', text_color='white')],
                       [sg.T('Country:', size=(8, 1)),sg.T('', key='-iss_countryName-', size=(80, 1),background_color='black',text_color='white')],
                       [sg.T('Time Zone:'), sg.T('',key='-iss_timezoneId-',size=(80, 1),background_color='black', text_color='white')],
                       [sg.T('Time/Date:'), sg.T('', key='-iss_time-', size=(80, 1), background_color='black', text_color='white')],
                       [sg.T('Latitude:', size=(8, 1)),sg.T('', size=(8, 1), key='-iss_lat-', background_color='black', text_color='white'),
                        sg.T('Longitude', size=(8, 1)),sg.T('', size=(7, 1), key='-iss_lon-', background_color='black', text_color='white')],
                       [sg.T(''), sg.T('')],
                       [sg.T('User Location', justification='center', size=(80, 1), background_color='gray',text_color='white')],
                       [sg.T('Address:', size=(8, 1)),sg.T('', size=(80, 1), key='-local_location-', background_color='black', text_color='white')],
                       [sg.T('Country:', size=(8, 1)),sg.T('', size=(80, 1), key='-local_countryName-', background_color='black', text_color='white')],
                       [sg.T('Time Zone:', size=(8, 1)),sg.T('', size=(80, 1), key='-local_timezoneId-',background_color='black', text_color='white')],
                       [sg.T('Time/Date', size=(8, 1)),sg.T('', size=(80, 1), key='-local_time-', background_color='black', text_color='white')],
                       [sg.T('Latitude:', size=(8, 1)),sg.T('', size=(7, 1), key='-local_latitude-', background_color='black', text_color='white'),
                        sg.T('Longitude', size=(7, 1)),sg.T('', size=(7, 1), key='-local_longitude-', background_color='black', text_color='white')],
                       [sg.T('Distance', size=(8, 1)),sg.T('', key="-iss_distance-", size=(10, 1), background_color='black', text_color='white')]]

        # lays out all the elements on the screen
        layout = [[sg.TabGroup([[sg.Tab('Iss Locator', tab_layout, tooltip='tip', element_justification='center')]])],
                  [sg.Button('ISS'), sg.Button('Astronauts'), sg.Button('Passes'), sg.Button('Measure'),
                   sg.Button('Help'), sg.Button('About'), sg.Button('Clear'), sg.Button('Exit')],
                  [sg.Image(filename='HDEV3.png', size=(750, 150))]]

        window = sg.Window('ISS Tracker', layout, default_element_size=(500, 500))

        # create loop that constantly checks for user input/button presses/etc

        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Exit'):
                window.close()  # destroy window and break loop - return to terminal menu
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
                    # after all fields on scren are updated, pass times pops up on screen
                    sg.popup(
                        f'\nThe next 5 Passes at Location:\n\n1st -  {time_zones["times"][0]}\n2nd - {time_zones["times"][1]}\n'
                        f'3rd -  {time_zones["times"][2]}\n4th -  {time_zones["times"][3]}\n5th -  {time_zones["times"][4]}\n\n',
                        title="Next 5 Passes", line_width=120)
                    window['-iss_distance-'].update(f"{distance['distance']} kms")
                except:  # sometimes some locations have 4 times - usually because the ISS just passed recently
                    window['-iss_distance-'].update(f"{distance['distance']} kms")
                    sg.popup(
                        f'\n          The next 4 Passes at Location:\n1st -  {time_zones["times"][0]}\n2nd - {time_zones["times"][1]}\n'
                        f'3rd -  {time_zones["times"][2]}\n4th -  {time_zones["times"][3]}',
                        title="Next 4 Passes", line_width=120)

            if event == 'Measure':  # pop up asks for user input - checks this - gets iss information and measures - updates all fields on the screen
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
                    with open('astros.txt', 'r') as astros:
                        astros = astros.read()
                    sg.popup(f'Astronauts onboard ISS\n{astros}', title="Astronauts", line_width=150)
                except:
                    sg.popup_error('There was no connection to API')

            if event == "Help":  # Help file is called and a pop up with the contents is displayed
                with open('help.txt', 'r') as file:
                    help_file = file.read()
                sg.popup(f'{help_file}', title="Help", line_width=150)

            if event == "About":  # About file is called and a pop up with the contents is displayed
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
            '1': Display_tables.return_iss_location,
            '2': Astronaut.get_astro,
            '3': Display_tables.display_pass_times_at_location,
            '4': Display_tables.display_distance,
            '5': Menu.help_text,
            '6': Menu.about_text,
            '8': Gui.make_gui}

    ''' define the actual persistant menu that will be underneath all applications - even when gui is quit - returns to this - 1-8 selections '''

    def menu(self):
        print('\n')
        menu_start = True
        while menu_start:  # Draw menu to screen via rich tables
            cls()
            table = Table(title="")

            table.add_column("Menu", justify="left")
            table.add_row( "\n What do you want to do:\n\n (1) Show current ISS position\n (2) Show current Astronauts on board\n "
                           "(3) Get time ISS passes at location\n (4) Measure distance between location and ISS\n "
                           "(5) Help\n (6) About\n (7) Quit\n (8) GUI \n")
            console = Console()
            console.print(table)

            operation = input('Select an option: ')
            try:  # Try all selections and if any thing is wrong - catch all - repeat menu
                if operation in self.operations:
                    programme = self.operations.get(f'{operation}')
                    #menu_start = False
                    programme()
                elif operation == '7':
                    menu_start = False
                    exit()
            except:
                input("Please select an option between 1 - 8\nPress Enter to Continue\n")
                cls()
                print()

    ''' Help and About files needed to be displayed to window '''

    @staticmethod
    @progress_bar_decorator_term
    def help_text():
        cls()
        with open('help.txt', 'r') as help_file:
            print(help_file.read())
        return input('Press enter')

    @staticmethod
    @progress_bar_decorator_term
    def about_text():
        cls()
        with open('about.txt', 'r') as help_file:
            print(help_file.read())
        return input('Press enter')






