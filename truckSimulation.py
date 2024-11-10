import simpy
import random

# Simulation parameters
RED_LIGHT_DURATION = 5  # Time for red traffic light (in minutes)
GREEN_LIGHT_DURATION = 3  # Time for green traffic light (in minutes)
NUM_TRUCKS = 10000  # Amount of trucks
SIMULATION_TIME = 480  # Simulationtime (in minutes)
LOADUNLOAD_TIME_RANGE = [30,41]  # Time range to load and unload a truck (in minutes)
DRIVE_TIME_A_TO_LIGHT = 20  # Time it takes to drive from A to the traffic light and vice versa(in minutes)
DRIVE_TIME_B_TO_LIGHT = 10  # Times it takes to drive from B to the traffic light and vice versa (in minutes)
ROUND_TRIPS = 3  # Amount of round trips a truck should do


class TrafficLight:
    def __init__(self, env):
        self.env = env
        self.state = "green"
        self.action = env.process(self.run())
        self.nextGreen = 0
    
    def run(self):
        while True:
            # Simulates the green light
            self.state = "green"
            yield self.env.timeout(GREEN_LIGHT_DURATION)
            
            # Simulates the red light
            self.state = "red"
            self.nextGreen = self.env.now + RED_LIGHT_DURATION
            yield self.env.timeout(RED_LIGHT_DURATION)


def truck(env, name, traffic_light, data):
    start_time = env.now
    print(f'{name} starts at {start_time} minutes.')

    stop_at_red_light = 0
    total_red_light_time = 0

    
    for i in range(ROUND_TRIPS):
        LOADING_UNLOADING_TIME = random.randint(LOADUNLOAD_TIME_RANGE[0],LOADUNLOAD_TIME_RANGE[1])

        print(f'{name} gets loaded.')
        yield env.timeout(LOADING_UNLOADING_TIME)
        print(f'{name} drives to storage B.')
        yield env.timeout(DRIVE_TIME_A_TO_LIGHT)
        
        while True:
            if traffic_light.state == "green":
                print(f'{name} continues at green traffic light.')
                break
            else:
                stop_at_red_light += 1
                wait_time = traffic_light.nextGreen - env.now
                print(f'{name} wwaits at red light for {wait_time} minutes.')
                total_red_light_time += wait_time
                yield env.timeout(wait_time)
        
        yield env.timeout(DRIVE_TIME_B_TO_LIGHT)
        print(f'{name} arrived at storage B and gets unloaded')
        yield env.timeout(LOADING_UNLOADING_TIME)


        print(f'{name} drives back to storage A.')
        yield env.timeout(DRIVE_TIME_B_TO_LIGHT)

        while True:
            if traffic_light.state == "green":
                print(f'{name} continues at green traffic light.')
                break
            else:
                stop_at_red_light += 1
                wait_time = traffic_light.nextGreen - env.now
                print(f'{name} wwaits at red light for {wait_time} minutes.')
                total_red_light_time += wait_time
                yield env.timeout(wait_time)

        yield env.timeout(DRIVE_TIME_A_TO_LIGHT)
        print(f'{name} arrived at storage A')

    # Data collection
    total_time = env.now - start_time
    data[name] = {
        'total_time': total_time,
        'stop_at_red_light': stop_at_red_light,
        'total_red_light_time': total_red_light_time
    }
    print(f'{name} ended his transports in {total_time} minutes.')


def run_simulation():
    
    
    for distance in range(5,30):
        env = simpy.Environment()
        traffic_light = TrafficLight(env)
        data = {}

        for i in range(NUM_TRUCKS):
            env.process(truck(env, f'LKW-{i+1}', traffic_light, data))

        global DRIVE_TIME_A_TO_LIGHT
        DRIVE_TIME_A_TO_LIGHT = distance
        env.run(until=SIMULATION_TIME)

        MIN = 999999
        AVG = 0
        MAX = 0
        for truck_name, truck_data in data.items():
            if truck_data["total_time"] < MIN:
                MIN = truck_data["total_time"]
            if truck_data["total_time"] > MAX:
                MAX = truck_data["total_time"]
            AVG += truck_data["total_time"]
            print(f'{truck_name}: Total time: {truck_data["total_time"]} minutes, '
            f'Amount of stops at red lights: {truck_data["stop_at_red_light"]}, '
            f'Total time waited at red lights: {truck_data["total_red_light_time"]} Minuten')
        AVG /= len(data.items())
        print(f"Abstand: {distance}, MIN: {MIN}, MAX: {MAX}, AVG: {AVG}")
        
        if len(data.items()) == NUM_TRUCKS:
            print("All trucks delivered successfully.")
        else:
            print("Not all trucks delivered successfully.")

if __name__ == "__main__":
    run_simulation()
