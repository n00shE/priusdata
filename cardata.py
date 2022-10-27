import datetime
import pynmea2
import csv

drive_modes = {'14': 'B', '13': 'D', '10': 'P', '11': 'R', '12': 'N'}

class CarData():
    def __init__(self, gps=False):
        self.gps = gps
        self.gas_p = 0
        self.batt_p = 0
        self.kph = 0
        self.speed_int = 0
        self.drive_mode = 'P'
        self.brake_pedal = 0
        self.gas_pedal = 0
        self.em_amps = 0
        self.em_volts = 0
        self.em_power = 0
        self.battery_volts = 0
        self.charging = False
        self.can_bus_count = 0
        self.cruise = 'OFF'
        self.engine_rpm = 0
        self.coolant_temp = 0
        self.steering_data = 0
        self.data = {}
        self.lat = 0
        self.lng = 0
        self.gps_speed = 0
        self.sat_num = 0
        self.driver_door = False
        self.passenger_door = False
        self.rear_doors = False
        self.rfront_tire = 0
        self.lfront_tire = 0
        self.rrear_tire = 0
        self.lrear_tire = 0
        self.minor_mismatch = 0
        self.major_mismatch = 0

    @staticmethod
    def wheel_speed_mismatch(speeds: list, threshold: int) -> bool: 
        for s1 in speeds:
            for s2 in speeds:
                if (abs(s1-s2) > threshold):
                    return True

    def __getitem__(self, arg):
        #data_types = ['Time', 'DriveMode', 'CruiseControl', 'GasTank%', 'BatterySOC%', \
        #    'SpeedMPH', 'BrakePedal', 'GasPedal', 'EMAmps', 'BatteryVolts', 'EngineRPM', \
        #    'CoolantTemp', 'SteeringAngle', 'CANFrameCount', 'Latitude', 'Longitude', 'GPSSpeed', 'SatNum', 'DriverDoor', 'PassengerDoor', 'RearDoors']
        if arg == 'DriveMode':
            return self.drive_mode
        elif arg == 'CruiseControl':
            return self.cruise
        elif arg == 'GasTank%':
            return self.gas_p
        elif arg == 'BatterySOC%':
            return self.batt_p
        elif arg == 'SpeedMPH':
            return self.speed_int
        elif arg == 'BrakePedal':
            return self.brake_pedal
        elif arg == 'GasPedal':
            return self.gas_pedal
        elif arg == 'EMAmps':
            return self.em_amps
        elif arg == 'BatteryVolts':
            return self.battery_volts
        elif arg == 'EngineRPM':
            return self.engine_rpm
        elif arg == 'CoolantTemp':
            return self.coolant_temp
        elif arg == 'SteeringAngle':
            return self.steering_data
        elif arg == 'CANFrameCount':
            return self.can_bus_count
        elif arg == 'Latitude':
            return self.lat
        elif arg == 'Longitude':
            return self.lng
        elif arg == 'GPSSpeed':
            return self.gps_speed
        elif arg == 'SatNum':
            return self.sat_num
        elif arg == 'DriverDoor':
            return self.driver_door
        elif arg == 'PassengerDoor':
            return self.passenger_door
        elif arg == 'RearDoors':
            return self.rear_doors
        elif arg == 'RightFront':
            return self.rfront_tire
        elif arg == 'LeftFront':
            return self.lfront_tire
        elif arg == 'RightRear':
            return self.rrear_tire
        elif arg == 'LeftRear':
            return self.lrear_tire
        else:
            raise ValueError

    def process_data(self, data):
        for address, _, dat, src  in data:
          if str(hex(address)) == '0x5a4':
            self.gas_p = (int(str(dat.hex())[-2:], 16) / 40) * 100
          if str(hex(address)) == '0x3cb':
            self.batt_p = int(str(dat.hex())[-8:-6], 16) / 2
          if str(hex(address)) == '0xb4':
            self.kph = int(str(dat.hex())[-6:-2], 16) / 100
            self.speed_int = round(self.kph * 0.62137, 2)
            #print('KPH (test reverse): ' + str(kph))
          if str(hex(address)) == '0x120' and str(dat.hex())[-6:-4] in drive_modes:
            self.drive_mode = drive_modes[str(dat.hex())[-6:-4]]
          if str(hex(address)) == '0x30':
            self.brake_pedal = round((int(str(dat.hex())[-8:-6], 16) / 127) * 100, 2)
          if str(hex(address)) == '0x244':
            self.gas_pedal = round((int(str(dat.hex())[-4:-2], 16) / 200) * 100, 2)
          if str(hex(address)) == '0x3b':
            #charging = True if int(str(dat.hex())[:2], 16) > 0 else False
            amp_data = int(str(dat.hex())[0:4], 16)
            if amp_data >= 2048:
              amp_data = amp_data - 4096
            if amp_data < 0:
              self.charging = True
            else:
              self.charging = False
            self.em_amps = amp_data / 10
            #em_volts = int(str(dat.hex())[-6:-2], 16)
            #em_power = em_amps * em_volts
          if str(hex(address)) == '0x3cd':
            self.battery_volts = int(str(dat.hex())[-6:-2], 16)
          if str(hex(address)) == '0x5c8':
            self.cruise = 'ON' if str(dat.hex())[-2:] == '10' else 'OFF'
          if str(hex(address)) == '0x3c8':
            self.engine_rpm = int(str(dat.hex())[-6:-4], 16) * 32
          if str(hex(address)) == '0x52c':
            self.coolant_temp = round(((int(str(dat.hex())[-2:], 16) / 2) * 9/5) + 32, 2)
          if str(hex(address)) == '0x25':
            self.steering_data = int(str(dat.hex())[0:4], 16)
            if self.steering_data >= 2048:
              self.steering_data = self.steering_data - 4096
            self.steering_data = self.steering_data * 360/240
          #if str(hex(address)) == '0x57f': # HEADLIGHTS
            #print(dat.hex())
          #if str(hex(address)) == '0x520':
            #print(str(dat.hex()))
            #print((speed_int * 1100) / int(str(dat.hex())[2:], 16)) # Fuel Injector???
          #if str(hex(address)) == '0x39':
            #print(int(str(dat.hex())[:2], 16) * 9/5 + 32) # Engine temp C???
          if str(hex(address)) == '0x5b6': # DOORS
              self.driver_door = str(dat.hex())[-2:] == '80'  
              self.passenger_door = str(dat.hex())[-2:] == '40'
              self.rear_doors = str(dat.hex())[-2:] == '04'
              # 40 is pass, 80 is driver, 04 is rear
          if str(hex(address)) == '0xb1': # front wheel speed
              self.rfront_tire = int(str(dat.hex())[:4], 16) / 100
              self.lfront_tire = int(str(dat.hex())[4:8], 16) / 100
          if str(hex(address)) == '0xb3':
              self.lrear_tire = int(str(dat.hex())[:4], 16) / 100
              self.rrear_tire = int(str(dat.hex())[4:8], 16) / 100
          if src == 0:
            self.can_bus_count += 1
          if self.wheel_speed_mismatch([self.rfront_tire, self.lfront_tire, self.rfront_tire, self.lrear_tire], 2):
              self.minor_mismatch += 1
          if self.wheel_speed_mismatch([self.rfront_tire, self.lfront_tire, self.rfront_tire, self.lrear_tire], 5):
              self.major_mismatch += 1
        #if engine_rpm != 0:
          #print('MPG? : ' + str((kph * 10000) / (engine_rpm / 32)))

    def add_to_dict(self):
        now = datetime.datetime.now()
        nowstr = now.strftime(r'%H:%M:%S.%f')
        if self.gps:
            self.data[nowstr] = [nowstr, self.drive_mode, self.cruise, self.gas_p, self.batt_p, self.speed_int, self.brake_pedal, self.gas_pedal, self.em_amps, self.battery_volts, self.engine_rpm, self.coolant_temp, self.steering_data, self.can_bus_count, self.lat, self.lng, self.gps_speed, self.sat_arg]
        else:
            self.data[nowstr] = [nowstr, self.drive_mode, self.cruise, self.gas_p, self.batt_p, self.speed_int, self.brake_pedal, self.gas_pedal, self.em_amps, self.battery_volts, self.engine_rpm, self.coolant_temp, self.steering_data, self.can_bus_count]

    @staticmethod
    def count_sats(msg) -> int:
        count = 0
        for i in range(1,13):
            attr = "sv_id"
            if i < 10:
                attr = attr+"0"+str(i)
            else:
                attr = attr+str(i)
            try:
                int(getattr(msg,attr))
                count += 1
            except ValueError:
                pass
        return count

    def get_gps_data(self, open_gps):
        try:
            line = open_gps.readline()
            decoded_line = line.decode('ascii', errors='replace').strip()
            msg = pynmea2.parse(decoded_line)
            if msg == '': raise ValueError
            #print(repr(msg))
            if isinstance(msg, pynmea2.types.GGA):
                #if not hasattr(msg, 'latitude') or not hasattr(msg, 'longitude'):
                #    print("no satellite signal...")
                #    continue
                self.lat = msg.latitude
                self.lng = msg.longitude
            if isinstance(msg, pynmea2.types.GSA):
                self.sat_num = self.count_sats(msg)
            if isinstance(msg, pynmea2.types.VTG):
                sat_kph = msg.spd_over_grnd_kmph
                self.gps_speed = round(sat_kph * 0.62137, 2)
        except:
            pass

    def write_row(self, writer):
        now = datetime.datetime.now()
        nowstr = now.strftime(r'%H:%M:%S.%f')
        if self.gps:
            writer.writerow([nowstr, self.drive_mode, self.cruise, self.gas_p, self.batt_p, self.speed_int, self.brake_pedal, self.gas_pedal, self.em_amps, self.battery_volts, self.engine_rpm, self.coolant_temp, self.steering_data, self.can_bus_count, self.rfront_tire, self.lfront_tire, self.rrear_tire, self.lrear_tire, self.driver_door, self.passenger_door, self.rear_doors, self.lat, self.lng, self.gps_speed, self.sat_num])
        else:
            writer.writerow([nowstr, self.drive_mode, self.cruise, self.gas_p, self.batt_p, self.speed_int, self.brake_pedal, self.gas_pedal, self.em_amps, self.battery_volts, self.engine_rpm, self.coolant_temp, self.steering_data, self.can_bus_count, self.rfront_tire, self.lfront_tire, self.rrear_tire, self.lrear_tire, self.driver_door, self.passenger_door, self.rear_doors])

    def write_entire_dict(self):
        now = datetime.datetime.now()
        file = 'output' + now.strftime(r'%m-%d-%H-%M-%S') + '.csv'
        with open(file, 'w', encoding='utf8', newline='') as f:
            csvwriter = csv.writer(f)
            if self.gps:
                csvwriter.writerow(['Time', 'DriveMode', 'CruiseControl', 'GasTank%', 'BatterySOC%', 'SpeedMPH', 'BrakePedal', 'GasPedal', 'EMAmps', 'BatteryVolts', 'EngineRPM', 'CoolantTemp', 'SteeringAngle', 'CANFrameCount', 'RightFTire', 'LeftFTire', 'RightRTire', 'LeftRTire', 'DriverDoor', 'PassengerDoor', 'RearDoor', 'Latitude', 'Longitude', 'GPSSpeed', 'SatNum'])
            else:
                csvwriter.writerow(['Time', 'DriveMode', 'CruiseControl', 'GasTank%', 'BatterySOC%', 'SpeedMPH', 'BrakePedal', 'GasPedal', 'EMAmps', 'BatteryVolts', 'EngineRPM', 'CoolantTemp', 'SteeringAngle', 'CANFrameCount', 'RightFTire', 'LeftFTire', 'RightRTire', 'LeftRTire', 'DriverDoor', 'PassengerDoor', 'RearDoor'])
            for k in self.data:
                csvwriter.writerow(self.data[k])
    
    def create_str(self, arg):
        if arg == 'DriveMode':
            return self.drive_mode
        elif arg == 'CruiseControl':
            return self.cruise
        elif arg == 'GasTank%':
            return f'The gas tank is {str(self.gas_p)} percent full'
        elif arg == 'BatterySOC%':
            return f'The battery is {str(self.batt_p)} percent charged'
        elif arg == 'SpeedMPH':
            return f'You are traveling at {str(self.speed_int)} miles per hour'
        elif arg == 'BrakePedal':
            return self.brake_pedal
        elif arg == 'GasPedal':
            return self.gas_pedal
        elif arg == 'EMAmps':
            return self.em_amps
        elif arg == 'BatteryVolts':
            return self.battery_volts
        elif arg == 'EngineRPM':
            return self.engine_rpm
        elif arg == 'CoolantTemp':
            return self.coolant_temp
        elif arg == 'SteeringAngle':
            return self.steering_data
        elif arg == 'CANFrameCount':
            return self.can_bus_count
        elif arg == 'Latitude':
            return self.lat
        elif arg == 'Longitude':
            return self.lng
        elif arg == 'GPSSpeed':
            return self.gps_speed
        elif arg == 'SatNum':
            return self.sat_num
        else:
            raise ValueError


    

