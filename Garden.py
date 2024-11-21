import pandas as pds  # Used for reading in csv files for quick plant adding
import random  # Used for randomly generating ideal conditions
import Weather  # Weather event storage, used for handling duration ticking and storing data
import threading  # Used for the game loop along with time
import time  # Used to determine game speed


class Garden:
    """
    Class for handling garden events and management
    """
    def __init__(self, read_in_file=None, weather_file=None):
        """
        Creates a new instance of a garden and begins a separate thread for game ticks\n
        Can take in a string file name for a csv file to read into
        :param read_in_file: str
        """
        self.plants = []
        self.forecast = []  # Example of a queue
        self.history = []  # Example of a stack
        self.plant_log = {}  # Use a dict for storing (plant name)<->(id) pairs
        self.tps = 10  # Change this value to alter the game speed

        if read_in_file:  # Allows for a file to be passed on initialization to read into
            self.read_in(read_in_file)

        if weather_file:
            self.weather_read_in(weather_file)

        self.save()
        self.__start_ticking__()  # Begin the game loop

    def __tick__(self):
        tps = self.tps
        save = 300
        while True:
            save -= 1

            if save == 0:
                save = 300
                self.save()

            time.sleep(tps)

            if len(self.forecast) == 0:  # Checks if there are no more weather events and adds endless if necessary
                # print("\nNo Weather conditions remain :: Using endless weather condition")
                self.forecast.append(Weather.Weather("0000-00-00", "ENDLESS", -700, 70))  # END OF DAYS!!!

                # Some people come to my code for academic purposes, others come for the jokes

            self.forecast[0].tick()

            # Pops expired weather events when duration is less than 0
            # Will not pop it if the duration is -700 since that denotes an endless weather event
            # Endless weather events will never be popped and their duration will not be decremented
            # Endless weather events can be configured manually or will occur when a forecast ends
            if self.forecast[0].duration <= 0 and not self.forecast[0].duration == -700:
                self.forecast.pop(0)

            current_temp = self.forecast[0].temp
            current_weather = self.forecast[0].weather

            for plant in self.plants:
                if plant.water > 0:
                    if current_weather == "Cloudy":
                        plant.growth_multiplier = 0.8  # Cloudy weather is not helpful for plants
                    elif current_weather == "Rainy":
                        plant.water = 100  # The watering can of the cosmos | Plants don't need watering in rain because: https://www.youtube.com/watch?v=YRL4uIVzVWI
                        plant.growth_multiplier = 1.0  # Reset growth multiplier from previous cycle
                    else:  # On Sunny, ENDLESS, or Unknown weather
                        plant.growth_multiplier = 1.0

                    if plant.ideal_conditions["min_temp"] >= current_temp >= plant.ideal_conditions["max_temp"]:
                        plant.growth_multiplier *= 1.5  # Grows 50% faster in ideal temp range

                    # Soil depletes watering_rate * (temp / 60) or 1 if it would be less than 1 and grows plant by the sum of growth_rate * growth_modifier
                    plant.grow(current_temp)

    def __str__(self):  # Gets a stringified list representing all the plants
        """
        Returns a string representation of garden including all plants housed and their properties
        :return: str
        """
        stringified_garden = "ID, Name, Species, Growth Rate, Watering Frequency, Height, Health, Temperature Range\n"
        for plant in self.plants:
            stringified_garden += (str(plant.get_synopsis(False)) + "\n")

        return stringified_garden

    def water_all(self):
        """
        Waters all plants in the garden
        :return: None
        """
        for plant in self.plants:
            plant.water_plant()

    def get_health_all(self):
        """
        Returns a list of all the plant's health
        :return: list()
        """
        status = []
        for plant in self.plants:
            status.append(plant.health)

        return status

    def get_garden(self):
        """
        Returns all plants in garden as list\n
        If displaying as string please use str(garden) instead
        :return: list()
        """
        return self.plants

    def get_weather(self):
        """
        Gets the current weather conditions
        :return: str
        """
        return self.forecast[0].get_synopsis()

    def add_plant(self, name, species, growth_rate, watering_frequency, height, health, min_temp=None, max_temp=None, id_val=None):
        """
        Add a new plant into the garden
        :param name: str
        :param species: str
        :param growth_rate: float
        :param watering_frequency: float
        :param height: float
        :param health: str
        :param min_temp: float
        :param max_temp: float
        :param id_val: int
        :return: None
        """
        self.plants.append(Plant(name, species, growth_rate, watering_frequency, height, health, min_temp, max_temp, id_val))
        print("Added new plant with the following properties")
        print(self.plants[len(self.plants) - 1])  # Print off the plant that was pushed to the end

        print(self.__str__())  # Print the garden out again as per the instructions

    def add_plant_by_csv(self, file_name):
        """
        Reads a csv file and converts it into new plants that are added to the garden
        :param file_name: str
        :return: None or -1
        """
        return self.read_in(file_name)  # Return is used because on error it returns -1

    def remove_plant(self, identifier: str or int):
        """
        Remove a plant by an id - Name or index
        :param identifier: str or int
        :return: None or -1
        """

        # Use a try except to parse the identifier to an int
        # If it succeeds then we know identifier is an ID and we send it to the remove by id function
        # If it fails then we know it was a name, and we send it to be removed by name
        try:
            identifier = int(identifier)
        except ValueError:
            "Do nothing since it's already a string"

        # Sending identifier to its proper function based on its type
        if type(identifier) is int:
            self.remove_plant_by_id(identifier)
            print(f"Plant(s) {identifier} removed")
            print(self.__str__())
            return
        elif type(identifier) is str:
            self.remove_plant_by_name(identifier)
            print(f"Plant(s) {identifier} removed")
            print(self.__str__())
            return

        print(f"Failed to remove plant: {identifier}")
        return -1

    def remove_plant_by_id(self, id_val: int):
        """
        Removes plant(s) by id value
        :param id_val: int
        :return: None
        """
        # Removes any plants with a matching id value
        indexes_to_remove = []

        for i, plant in enumerate(self.plants):
            if plant.id == id_val:
                indexes_to_remove.append(i)  # Have to do it this way since when we pop something it will then skip the next value due to how the for loop works

        # This will now adjust which index to remove by -1 each time it pops something
        # This is officially sanctioned by the Cavemen Programmers Sector also known as CPS... wait a minute!
        for i, index in enumerate(indexes_to_remove):
            self.history.append(self.plants.pop(index-i))

    def remove_plant_by_name(self, name: str):
        """
        Removes plant(s) by name
        :param name: str
        :return: None
        """
        indexes_to_remove = []

        for i, plant in enumerate(self.plants):
            if plant.name == name:
                indexes_to_remove.append(i)  # Have to do it this way since when we pop something it will then skip the next value due to how the for loop works

        # This will now adjust which index to remove by -1 each time it pops something
        # This is officially sanctioned by the Cavemen Programmers Sector also known as CPS... wait a minute!
        for i, index in enumerate(indexes_to_remove):
            self.history.append(self.plants.pop(index-i))

    @staticmethod
    def __check_nan(item):
        """
        Checks whether an item is not a number\n
        Used to determine if a pandas.get() function couldn't find its value since it returns a float(nan)
        :param item: any
        :return: bool
        """
        return str(item) == "nan"

    def read_in(self, file_name):
        """
        Reads a file and adds its plants to the garden
        :param file_name: str
        :return: None or -1
        """
        data = pds.read_csv(file_name)

        # Default values for items in case it can't find them
        default_vals = ("PlantX", "SpeciesX", 3, 3, 3, "Healthy", None, None)

        for i in range(len(data)):
            # Grab the plant from the csv file
            # Error checking is not necessary
            # The pandas.get() function returns a default value when it can't find an element
            id = data.get("ID")[i]
            name = data.get("Name")[i]
            species = data.get("Species")[i]
            growth_rate = data.get("GrowthRate")[i]
            watering_frequency = data.get("WateringFrequency")[i]
            height = data.get("Height")[i]
            health = data.get("HealthStatus")[i]

            # Ternary Expression courtesy of
            # https://stackoverflow.com/questions/2802726/putting-a-simple-if-then-else-statement-on-one-line
            # Use ternary to check if the values are nan, meaning they are absent,
            # and assigning a default value if they are
            id = id if not self.__check_nan(id) else None
            name = name if not self.__check_nan(name) else default_vals[0]
            species = species if not self.__check_nan(species) else default_vals[1]
            growth_rate = growth_rate if not self.__check_nan(growth_rate) else default_vals[2]
            watering_frequency = watering_frequency if not self.__check_nan(watering_frequency) else default_vals[3]
            height = height if not self.__check_nan(height) else default_vals[4]
            health = health if not self.__check_nan(health) else default_vals[5]

            try:
                min_temp = data.get("minTemp")[i]
                max_temp = data.get("maxTemp")[i]
            except TypeError:
                min_temp = default_vals[6]
                max_temp = default_vals[7]

            # Create a new plant with the given attributes
            self.plants.append(Plant(name, species, growth_rate, watering_frequency, height, health, min_temp, max_temp, id))

    def weather_read_in(self, file_name):
        data = pds.read_csv(file_name)

        dates = []
        types = []
        durations = []
        temps = []

        # Get the date, weather_type, duration, and temp of the entire file
        # Use ternary expression to check if the value exists in the file, if it doesn't default it to type(None)
        # The weather constructor handles None types by assigning default values on its own
        item_exists = (True if not self.__check_nan(data.get("Date")) else False,
                       True if not self.__check_nan(data.get("WeatherType")) else False,
                       True if not self.__check_nan(data.get("Duration")) else False,
                       True if not self.__check_nan(data.get("Temperature")) else False)

        if item_exists[0]:
            for item in data.get("Date"):
                dates.append(item)

        if item_exists[1]:
            for item in data.get("WeatherType"):
                types.append(item)

        if item_exists[2]:
            for item in data.get("Duration"):
                durations.append(item)
        if item_exists[3]:
            for item in data.get("Temperature"):
                temps.append(item)

        for i, item in enumerate(dates):
            self.forecast.append(Weather.Weather(dates[i], types[i], durations[i], temps[i]))

    def __start_ticking__(self):
        """
        Initializes a thread responsible for game ticks\n
        Called automatically by constructor
        :return: None
        """
        thread = threading.Thread(target=self.__tick__)
        thread.daemon = True  # If main ends then this thread will as well
        thread.start()

    def recover(self):
        """
        Recovers the last plant removes
        :return: None
        """
        if len(self.history) > 0:  # Checks if there is a previous action to revert
            self.plants.append(self.history.pop())

    def recover_all(self):
        """
        Recovers all items in history
        :return: None
        """
        for item in self.history:
            self.plants.append(item)

        self.history = []

    def save(self):
        # https://www.tutorialspoint.com/python/python_files_io.htm
        with open("plants.txt", 'w') as file:
            file.write("ID,Name,Species,GrowthRate,WateringFrequency,Height,HealthStatus,minTemp,maxTemp\n")
            for plant in self.plants:
                file.write(str(plant.id) + "," + plant.name + "," + plant.species + "," + str(plant.growth_rate) + ","
                           + str(plant.watering_frequency) + "," + str(plant.height) + "," + plant.health + "," + str(plant.ideal_conditions['min_temp'])
                           + "," + str(plant.ideal_conditions['max_temp']) + "\n"
                           )
            file.close()


class Plant(object):
    """
    Single plant node within a garden
    """
    def __init__(self, name, species, growth_rate, watering_frequency, height, health, min_temp=None, max_temp=None, id=None):
        """
        Creates a new instance of a plant
        :param name: str
        :param species: str
        :param growth_rate: float
        :param watering_frequency: float
        :param height: float
        :param health: str
        :param min_temp: float
        :param max_temp: float
        :param id: int
        """

        if (min_temp and not max_temp) or (max_temp and not min_temp):
            print("You must input both a minimum temperature"
                  " and a maximum temperature if adding manual temperature conditions")
            print("Default temperature gradient will be used instead")

        self.water = 0  # Water depletes as the plant grows, plants without water will not grow
        self.name = name
        self.id = id
        self.species = species
        self.growth_rate = growth_rate
        self.watering_frequency = watering_frequency
        self.height = height
        self.health = health
        self.growth_modifier = 1.00  # Plants grow faster in their ideal conditions

        if not min_temp or not max_temp:  # If there wasn't a min/max temp passed then get a temp condition
            # Temperatures used are not indicative of real life temperatures.
            # I don't want to research a dozen groups of plants to figure out their ideal conditions
            # These are just estimates of the conditions as I understand them
            if species == "Succulent":
                min_temp = 70
                max_temp = 130
            elif species == "Flower":
                min_temp = 60
                max_temp = 100
            elif species == "Gourd":
                min_temp = 40
                max_temp = 80
            elif species == "Bonsai":  # Bonsai trees are particularly picky plants
                min_temp = 60
                max_temp = 70
            else:  # Random temps if not recognized
                min_temp = random.randint(40, 60)
                max_temp = random.randint(60, 90)

        self.ideal_conditions = {"min_temp": min_temp, "max_temp": max_temp}

    def get_synopsis(self, show_labels=True):
        """
        Returns a brief synopsis of the current plant's properties
        :param show_labels: bool
        :return: list[any] or list[str, any]
        """

        if show_labels:
            return [
                ["id", "Name", "Species", "Growth Rate", "Watering Frequency", "Height", "Health", "Temperature Range"],
                [self.id, self.name, self.species, self.growth_rate, self.watering_frequency, self.height, self.height, self.ideal_conditions]
            ]
        else:
            return [self.id, self.name, self.species, self.growth_rate, self.watering_frequency, self.height, self.height, self.ideal_conditions]

    def grow(self, temp):
        depletion = self.watering_frequency * (temp / 60)

        if depletion < 1:  # Always lose at least 1 water point
            depletion = 1

        self.water -= depletion

        # These conditions are too extreme and plants will not grow at all due to them prioritizing water and nutrient retention
        # If the weather is +-30 then growing ceases. Water depletion does not stop, but colder weather results in less
        # Water depletion because the water does not evaporate from the soil/plant cells as quickly
        # I am in fact, a biology nerd...
        if self.ideal_conditions["min_temp"] - 30 >= temp:
            self.health = "Cold"
            return
        elif self.ideal_conditions["max_temp"] + 30 <= temp:
            self.health = "Hot"
            return
        elif self.water <= 0:  # Plant can't grow without water
            self.health = "Thirsty"
        else:
            self.height += self.growth_rate * self.growth_modifier  # Plant is perfectly healthy and will grow
            self.health = "Healthy"

    def water_plant(self):
        """
        Sets the plant's water value to 100
        :return: None
        """
        self.water = 100
