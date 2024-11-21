import random


class Weather:
    def __init__(self, date=None, weather=None, duration=None, temp=None):
        # Set up the date, temp, weather_type, duration using given values or default values if type(None) is passed
        # Or no value is passed
        self.date = date if date else "0000-00-00"
        self.temp = temp if temp else random.randint(40, 120)
        self.weather = weather if weather else "Sunny"
        self.duration = duration if duration else 5

    def tick(self):
        """
        Ticks the weather duration down by 1
        :return: None
        """

        # -700 is a never ending weather event :: Does not decrement
        if self.duration == -700:
            return

        self.duration -= 1

    def get_synopsis(self):
        """
        Gets a synopsis of the current weather
        :return: str
        """
        return "Date, Weather, Temperature, Duration\n" + self.date + ", " + self.weather + ", " + str(self.temp) + ", " + str(self.duration)

    def set_temp(self, temp):
        """
        Sets the current temperature
        :param temp: float or int
        :return: None
        """
        if self.temp is float or self.temp is int:
            self.temp = temp

    def set_weather(self, weather):
        """
        Sets the current weather
        :param weather: str
        :return:
        """
        self.weather = weather
