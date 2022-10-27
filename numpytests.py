import numpy as np 
import matplotlib.pyplot as plt

file = "output03-22-14-15-22.csv"
unfiltered = "output12-21-15-39-32fixedtime.csv"

#data = np.genfromtxt(unfiltered, delimiter=',')
#x = np.arange(0, un.shape[0], 1)

day = "2021-03-22T"

stringdata = np.genfromtxt(file, dtype='str', delimiter=',')
for row in stringdata:
    row[0] = day + row[0]
dates = np.array(stringdata[60:, 0], dtype='datetime64')
data = np.array(stringdata[60:, 3:], dtype=float)

print(dates[0])
print(data.shape[0])


brake_pedal = data[:, 3]
gas_pedal = data[:, 4]
em_amps = data[:, 5]
batt_volts = data[:, 6]
rpm = data[:, 7]
coolant_temp = data[:, 8]
steering_angle = data[:, 9]
gps_speed = data[:, 13]
car_speed = data[:, 2]

plt.style.use('dark_background')


def gasPedalandRPM():
    plt.figure(figsize=(12,8), dpi= 100)
    plt.plot(dates, gas_pedal, c='green', label='Gas Pedal %', alpha=0.6)
    plt.plot(dates, rpm / 100, c='orange', label='RMP (hundreds)', alpha=0.6)
    plt.plot(dates, (em_amps*batt_volts) / 1000, c='yellow', label='Power (kW)', alpha=0.6)
    plt.legend()
    plt.show()    


def pedalsAndPower():
    plt.figure(figsize=(12,8), dpi= 100)
    plt.plot(dates, gas_pedal, c='green', label='Gas Pedal %', alpha=0.6)
    plt.plot(dates, brake_pedal, c='red', label='Brake Pedal %', alpha=0.6)
    #plt.plot(dates, batt_volts - 201, c='orange', label='Battery Voltage Offset', alpha=0.6) # Normalizes voltage
    #plt.plot(dates, em_amps, c='yellow', label='EM Amps', alpha=0.6)
    plt.plot(dates, (em_amps*batt_volts) / 1000, c='yellow', label='Power (kW)', alpha=0.6)
    plt.plot(dates, rpm / 100, c='orange', label='RMP (hundreds)', alpha=0.6)
    plt.legend()
    plt.show()

def pedalsVoltOffset():
    plt.figure(figsize=(12,8), dpi= 100)
    plt.plot(dates, gas_pedal, c='green', label='Gas Pedal %', alpha=0.6)
    plt.plot(dates, brake_pedal, c='red', label='Brake Pedal %', alpha=0.6)
    plt.plot(dates, batt_volts - 201, c='orange', label='Battery Voltage Offset', alpha=0.6) # Normalizes voltage
    plt.legend()
    plt.show()


def pedalsAmp():
    plt.figure(figsize=(12,8), dpi= 100)
    plt.plot(dates, gas_pedal, c='green', label='Gas Pedal %', alpha=0.6)
    plt.plot(dates, brake_pedal, c='red', label='Brake Pedal %', alpha=0.6)
    plt.plot(dates, em_amps, c='yellow', label='EM Amps', alpha=0.6)
    #plt.ylabel('Speed (MPH)')
    plt.legend()
    plt.show()


def speedCompare():
    plt.scatter(dates, car_speed, c='green', label='Car Speed', alpha=0.6)
    plt.scatter(dates, gps_speed, c='red', label='GPS Speed', alpha=0.6)
    plt.ylabel('Speed (MPH)')
    plt.legend()
    plt.show()
    
def gasPedalandSpeed():
    plt.plot(dates, gas_pedal, c='green', label='Gas Pedal %', alpha=0.6)
    plt.plot(dates, car_speed, c='red', label='Car Speed (MPH)', alpha=0.6)
    plt.ylabel('Speed (MPH)')
    plt.legend()
    plt.show()

def pedalsPowerAndSpeed():
    plt.figure(figsize=(12,8), dpi= 100)
    plt.plot(dates, gas_pedal, c='green', label='Gas Pedal %', alpha=0.6)
    plt.plot(dates, brake_pedal, c='red', label='Brake Pedal %', alpha=0.6)
    plt.plot(dates, car_speed, c='blue', label='Car Speed (MPH)', alpha=0.6)
    plt.plot(dates, (em_amps*batt_volts) / 1000, c='yellow', label='Power (kW)', alpha=0.6)
    plt.plot(dates, rpm / 100, c='orange', label='RMP (hundreds)', alpha=0.6)
    plt.legend()
    plt.show()

#gasPedalandRPM()
#pedalsAndPower()
#pedalsVoltOffset()
#pedalsAmp()
#speedCompare()
pedalsPowerAndSpeed()

# The second generation Toyota Prius makes use of a 201.6-volt NiMH battery composed of 28 modules, where each module is made of six individual 1.2-volt, 6.5 Ah Prismatic NiMH cells