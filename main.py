import pandas as pds
import Garden


if __name__ == "__main__":
    """
    If reading into a file please use a csv formatted file, can be a .txt extension, and format it similar to plants_test.csv
    If passing temperature preferences with a plant please use the keys "minTemp" & "maxTemp"
    You can also manually add a weather file
    """

    garden = Garden.Garden(read_in_file="plants.txt", weather_file="default_weather.csv")

    # Interactive interface is on main thread while the plant updates and ticking is on a side thread for the game loop
    while True:
        cmd = input("Type a command(help for cmd list): ")

        if cmd == "help":
            print("""
help: Displays command list
water: Water all plants
check health: Checks the health of all plants
show garden: Display's garden in a stringified list
show history: Display's the garden's history
add plant: Adds a new plant to the garden
plant help: Get info on adding plants
remove plant: Remove a plant(s) based on their id or name
recover plant: Undo the last plant removed
recover all: Undoes all previous removals in history
clear history: Clears the garden history
save: Saves your current history to plants.txt file
show weather: Shows the date and weather
""")
        elif cmd == "water":
            garden.water_all()
        elif cmd == "check health":
            print(str(garden.get_health_all()))
        elif cmd == "show garden":
            print(str(garden))
        elif cmd == "add plant":
            id_var = input("ID: ")
            name = input("Plant name: ")
            species = input("Species name: ")
            growth_rate = input("Growth rate: ")
            watering_frequency = input("Watering frequency: ")
            height = input("Starting height: ")
            health = input("Health status(1 = Healthy; 2 = Dry): ")
            min_temp = input("Plant's minimum preferred temperature: ")
            max_temp = input("Plant's maximum preferred temperature: ")

            # Try parsing the values and excepting any ValueErrors by telling the user their formatting was incorrect
            try:
                id_var = int(id_var)  # id is a built-in so use this name
                min_temp = float(min_temp)
                max_temp = float(max_temp)
                height = float(height)
                watering_frequency = float(watering_frequency)
                growth_rate = float(growth_rate)

                # If it's invalid number then throw ValueError and let except block handle it
                if watering_frequency <= 0:
                    raise ValueError
                elif height < 0:
                    raise ValueError
                elif min_temp > max_temp:
                    raise ValueError
                elif growth_rate <= 0:
                    raise ValueError
                elif id_var < 0:
                    raise ValueError

                if int(health) == 1:
                    health = "Healthy"
                else:
                    health = "Dry"
            except ValueError:
                print("There was an error reading your values, please retry with the proper formatting (use \"plant help\" to get info on how to add a plant)")

            garden.add_plant(name, species, growth_rate, watering_frequency, height, health, min_temp, max_temp, id_var)
            garden.save()

        elif cmd == "plant help":
            print("To add a plant use the command \"add plant\" then fill out the fields with the following format")
            print("ID: NUMBER >= 0 :: This is used for removing groups of plants by their id number")
            print("Name: TEXT")
            print("Species: TEXT")
            print("Growth Rate: NUMBER > 0")
            print("Watering Frequency: NUMBER > 0")
            print("Starting Height: NUMBER > 0")
            print("Health Status: NUMBER(1 or 2)")
            print("Minimum Temp: NUMBER < Maximum Temp")
            print("Maximum Temp: NUMBER > Minimum Temp")
        elif cmd == "remove plant":
            identifier = input("Enter the name or ID of the plant(s) to be removed: ")
            garden.remove_plant(identifier)  # remove_plant() handles routing the identifier to its proper destination of remove_plant_by_id() or remove_plant_by_name()
            garden.save()
        elif cmd == "recover plant":
            garden.recover()
            garden.save()
            print("Last plant removed has been recovered")
        elif cmd == "recover all":
            garden.recover_all()
            garden.save()
            print("All items recovered from history")
        elif cmd == "show history":
            print(str(garden.history))
        elif cmd == "clear history":
            garden.history = []
            print("History Cleared")
        elif cmd == "save":
            garden.save()
            print("Progress saved")
        elif cmd == "show weather":
            print(garden.get_weather())
