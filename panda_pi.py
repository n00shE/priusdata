import csv
import sys
from panda import Panda
import datetime
import serial
import pynmea2
import socket
import subprocess
import time

drive_modes = {'14': 'B', '13': 'D', '10': 'P', '11': 'R', '12': 'N'}
data_types = ['Time', 'DriveMode', 'CruiseControl', 'GasTank%', 'BatterySOC%', 'SpeedMPH', 'BrakePedal', 'GasPedal', 'EMAmps', 'BatteryVolts', 'EngineRPM', 'CoolantTemp', 'SteeringAngle', 'CANFrameCount', 'Latitude', 'Longitude', 'GPSSpeed', 'SatNum']
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 17380
call_beg = 'festival -b \'(voice_cmu_us_slt_arctic_hts)\' \'(SayText "'
call_end = '")\''
time.sleep(10)


def init_panda() -> Panda:
  try:
    print("Trying to connect to Panda over USB...")
    p = Panda()

  except AssertionError:
    print("USB connection failed. Trying WiFi...")

    try:
      p = Panda("WIFI")
    except:
      print("WiFi connection timed out. Please make sure your Panda is connected and try again.")
      sys.exit(0)
  return p

def to_csv(data: dict) -> None:
  now = datetime.datetime.now()
  file = 'output' + now.strftime(r'%m-%d-%H-%M-%S') + '.csv'
  with open(file, 'w', encoding='utf8', newline='') as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(['Time', 'DriveMode', 'CruiseControl', 'GasTank%', 'BatterySOC%', 'SpeedMPH', 'BrakePedal', 'GasPedal', 'EMAmps', 'BatteryVolts', 'EngineRPM', 'CoolantTemp', 'SteeringAngle', 'CANFrameCount', 'Latitude', 'Longitude', 'GPSSpeed', 'SatNum'])
    for k in data:
      csvwriter.writerow(data[k])

def count_sv(msg) -> int:
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

def send_data(data: list):
  print('running')
  with socket.socket() as s:
    s.connect((HOST, PORT))
    while True:
      s_data = s.recv(1024).decode()
      if str(s_data) != '':
        print(s_data)
      if str(s_data) in data_types:
        i = data_types.index(str(s_data))
        print(data[i])
        #subprocess.call(['festival', '-b' ,'\'(voice_cmu_us_slt_arctic_hts)\'', '\'(SayText "The temperature is 22 degrees centigrade and there is a slight breeze from the west.")\''], close_fds=True, shell=True)
        subprocess.call(['festival -b \'(voice_cmu_us_slt_arctic_hts)\' \'(SayText "The temperature is 22 degrees centigrade and there is a slight breeze from the west.")\''], close_fds=True, shell=True)

def run(p: Panda) -> dict:
    data = []
    gps = True
    voice = True
    port = '/dev/serial/by-id/usb-u-blox_AG_-_www.u-blox.com_u-blox_7_-_GPS_GNSS_Receiver-if00'
    ser = 0
    soc = 0

    gas_int = 0
    batt_int = 0
    speed_int = 0
    drive_mode = 'P'
    brake_percent = 0
    gas_percent = 0
    em_amps = 0
    em_volts = 0
    em_power = 0
    battery_volts = 0
    charging = False
    can_bus_count = 0
    cruise = 'OFF'
    engine_rpm = 0
    coolant_temp = 0
    steering_data = 0
    frames_s = 0
    lat = 0
    lng = 0
    sat_num = 0
    gps_speed = 0
    
    now = datetime.datetime.now()
    file = '/home/pi/panda/output' + now.strftime(r'%m-%d-%H-%M-%S') + '.csv'
    f = open(file, 'w', encoding='utf8', newline='')
    csvwriter = csv.writer(f)
    csvwriter.writerow(['Time', 'DriveMode', 'CruiseControl', 'GasTank%', 'BatterySOC%', 'SpeedMPH', 'BrakePedal', 'GasPedal', 'EMAmps', 'BatteryVolts', 'EngineRPM', 'CoolantTemp', 'SteeringAngle', 'CANFrameCount', 'Latitude', 'Longitude', 'GPSSpeed', 'SatNum'])

    while True:
      #start = time.time()
      try:
        if voice and soc == 0:
          try:
            soc = socket.socket()
            soc.connect((HOST, PORT))
            print('connected to socket')
          except:
            pass
        if gps and ser == 0:
            try:
                ser = serial.Serial(port, 4800, timeout=0.001)
            except Exception:
                pass
        if gps and ser != 0:
            try:
                line = ser.readline()
                decoded_line = line.decode('ascii', errors='replace').strip()
                msg = pynmea2.parse(decoded_line)
                if msg == '': raise ValueError
                #print(repr(msg))
                if isinstance(msg, pynmea2.types.GGA):
                    if not hasattr(msg, 'latitude') or not hasattr(msg, 'longitude'):
                        print("no satellite signal...")
                        continue
                    lat = msg.latitude
                    lng = msg.longitude
                if isinstance(msg, pynmea2.types.GSA):
                    sat_num = count_sv(msg)
                if isinstance(msg, pynmea2.types.VTG):
                    sat_kph = msg.spd_over_grnd_kmph
                    gps_speed = round(sat_kph * 0.62137, 3)
            except ValueError:
                pass
        can = p.can_recv()
        for address, _, dat, src  in can:
          if str(hex(address)) == '0x5a4':
            gas_int = (int(str(dat.hex())[-2:], 16) / 40) * 100
          if str(hex(address)) == '0x3cb':
            batt_int = int(str(dat.hex())[-8:-6], 16) / 2
          if str(hex(address)) == '0xb4':
            kph = int(str(dat.hex())[-6:-2], 16) / 100
            speed_int = round(kph * 0.62137, 2)
          if str(hex(address)) == '0x120' and str(dat.hex())[-6:-4] in drive_modes:
            drive_mode = drive_modes[str(dat.hex())[-6:-4]]
          if str(hex(address)) == '0x30':
            brake_percent = round((int(str(dat.hex())[-8:-6], 16) / 127) * 100, 2)
          if str(hex(address)) == '0x244':
            gas_percent = round((int(str(dat.hex())[-4:-2], 16) / 200) * 100, 2)
          if str(hex(address)) == '0x3b':
            #charging = True if int(str(dat.hex())[:2], 16) > 0 else False
            amp_data = int(str(dat.hex())[0:4], 16)
            if amp_data >= 2048:
              amp_data = amp_data - 4096
            if amp_data < 0:
              charging = True
            else:
              charging = False
            em_amps = amp_data / 10
            #em_volts = int(str(dat.hex())[-6:-2], 16)
            #em_power = em_amps * em_volts
          if str(hex(address)) == '0x3cd':
            battery_volts = int(str(dat.hex())[-6:-2], 16)
          if str(hex(address)) == '0x5c8':
            cruise = 'ON' if str(dat.hex())[-2:] == '10' else 'OFF'
          if str(hex(address)) == '0x3c8':
            engine_rpm = int(str(dat.hex())[-6:-4], 16) * 32
          if str(hex(address)) == '0x52c':
            coolant_temp = round(((int(str(dat.hex())[-2:], 16) / 2) * 9/5) + 32, 2)
          if str(hex(address)) == '0x25':
            steering_data = int(str(dat.hex())[0:4], 16)
            if steering_data >= 2048:
              steering_data = steering_data - 4096
            steering_data = steering_data * 360/240
          if src == 0:
            can_bus_count += 1
          #print(can_bus_count)

        now = datetime.datetime.now()
        nowstr = now.strftime(r'%H:%M:%S.%f')
        csvwriter.writerow([nowstr, drive_mode, cruise, gas_int, batt_int, speed_int, brake_percent, gas_percent, em_amps, battery_volts, engine_rpm, coolant_temp, steering_data, can_bus_count, lat, lng, gps_speed, sat_num])
        data = [nowstr, drive_mode, cruise, gas_int, batt_int, speed_int, brake_percent, gas_percent, em_amps, battery_volts, engine_rpm, coolant_temp, steering_data, can_bus_count, lat, lng, gps_speed, sat_num]

        if voice and soc != 0:
          s_data = soc.recv(1024).decode()
          if s_data != '':
            print(s_data)
          if s_data in data_types:
            i = data_types.index(str(s_data))
            d = data[i]
            print(d)
            if s_data == 'SpeedMPH':
              call_mid = f'You are traveling at {str(d)} miles per hour'
            elif s_data == 'BatterySOC%':
              call_mid = f'The batter is {str(d)} percent charged'
            subprocess.call([call_beg + call_mid + call_end], close_fds=True, shell=True)
        #end = time.time()
        #print('Loop Time: ' + str(end - start))
      except KeyboardInterrupt:
        if gps:
          ser.close()
        f.close()
        print('closing...')
        

if __name__ == "__main__":
    #send_data([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
    p = init_panda()
    run(p)
    #to_csv(data)
