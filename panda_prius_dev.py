import csv
import sys
from panda import Panda
import tkinter as tk
import tkinter.font as tkFont
#from time import sleep
import datetime
import time
import serial
import pynmea2

# GPS code from https://github.com/Perseus-II/GPS/blob/master/gps.py

'''
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
'''

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

def can_logger(p: Panda):

  try:
    outputfile = open('output.csv', 'w', encoding='utf8', newline='')
    csvwriter = csv.writer(outputfile)
    #Write Header
    csvwriter.writerow(['Bus', 'MessageID', 'Message', 'MessageLength'])
    print("Writing csv file output.csv. Press Ctrl-C to exit...\n")

    bus0_msg_cnt = 0
    bus1_msg_cnt = 0
    bus2_msg_cnt = 0

    while True:
      can_recv = p.can_recv()

      for address, _, dat, src  in can_recv:
        csvwriter.writerow([str(src), str(hex(address)), f"0x{dat.hex()}", len(dat)])

        if src == 0:
          bus0_msg_cnt += 1
        elif src == 1:
          bus1_msg_cnt += 1
        elif src == 2:
          bus2_msg_cnt += 1

        print(f"Message Counts... Bus 0: {bus0_msg_cnt} Bus 1: {bus1_msg_cnt} Bus 2: {bus2_msg_cnt}", end='\r')

  except KeyboardInterrupt:
    print(f"\nNow exiting. Final message Counts... Bus 0: {bus0_msg_cnt} Bus 1: {bus1_msg_cnt} Bus 2: {bus2_msg_cnt}")
    outputfile.close()

def enable_write(p: Panda):
  print('!!! DANGER DANGER DANGER !!!')
  print("Setting Panda to output mode... (BE CAREFUL)")
  p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)

def send_data(p: Panda):
  print('!!! DANGER DANGER DANGER !!!')
  print("Setting Panda to output mode... (BE CAREFUL)")
  p.set_safety_mode(Panda.SAFETY_ALLOUTPUT)
  print('Attempting to send...')
  try:
    #p.can_send(0x5c8, b'\xa4\x00\x10', 0) #CRUISE
    #p.can_send(0x540, b'\xa5\x20\x00\x00', 0) #SHIFTER
    p.can_send(0x57f, b'\x68\x30\x10\x00\x00\x00\x00', 0) # LIGHTS
  finally:
    print("Disabling output on Panda... (SAFETY ENGAGED)")
    p.set_safety_mode(Panda.SAFETY_SILENT)

def current(p: Panda):
  while True:
    can_recv = p.can_recv()
    for address, _, dat, src  in can_recv:
      '''
      if str(hex(address)) == '0x3b':
        hexstr = str(dat.hex())[-2:]
        print(f'Current: {int(hexstr, 16)}')
      '''
      if str(hex(address)) == '0xb4':
        print(f'Hex : {str(dat.hex())}')
        hexstr = str(dat.hex())[-6:-2]
        print(f'Speed : {(int(hexstr, 16) / 100) * 0.62137}')

def to_csv(data: dict):
  now = datetime.datetime.now()
  file = 'output' + now.strftime(r'%m-%d-%H-%M-%S') + '.csv'
  with open(file, 'w', encoding='utf8', newline='') as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(['Time', 'DriveMode', 'CruiseControl', 'GasTank%', 'BatterySOC%', 'SpeedMPH', 'BrakePedal', 'GasPedal', 'EMAmps', 'BatteryVolts', 'EngineRPM', 'CoolantTemp', 'SteeringAngle', 'CANFrameCount', 'Latitude', 'Longitude', 'GPSSpeed', 'SatNum'])
    for k in data:
      csvwriter.writerow(data[k])

def gps(ser: serial.Serial) -> dict:
  data = {}
  while True:
    try:
      line = ser.readline()
      decoded_line = line.decode('ascii', errors='replace').strip()
      msg = pynmea2.parse(decoded_line)
      #print(repr(msg))
      if isinstance(msg, pynmea2.types.GGA):
          if not hasattr(msg, 'latitude') or not hasattr(msg, 'longitude'):
              print("no satellite signal...")
              break
          lat = msg.latitude
          lng = msg.longitude
          print(f'Lat: {lat} Long: {lng}')
      if isinstance(msg, pynmea2.types.GSA):
          num_sv_in_use = count_sv(msg)
          print(f'Sats in use: {num_sv_in_use}')
      if isinstance(msg, pynmea2.types.VTG):
          sat_kph = msg.spd_over_grnd_kmph
          data['kph'] = sat_kph
          print(f'MPH: {round(sat_kph * 0.62137, 3)}')
    except Exception as e:
        sys.stderr.write('Error reading serial port %s: %s\n' % (type(e).__name__, e))
  
  return data

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

def gui(p: Panda, send_bool=False, gps=False):
    #wifi = p.get_serial()
    #print("SSID: " + wifi[0])
    #print("Password: " + wifi[1])
    data = {}
    port = 'COM3'
    ser = 0
    '''
    TODO:
    Add Doors
    '''
    drive_modes = {'14': 'B', '13': 'D', '10': 'P', '11': 'R', '12': 'N'}
    window = tk.Tk()
    title_font = tkFont.Font(family="Times", size=24, weight=tkFont.BOLD)
    label_font = tkFont.Font(family="Times", size=20)
    title = tk.Label(text="2006 (Gen 2) Prius Monitor", font=title_font)
    title.pack()

    gas_var = tk.StringVar(value='0')
    battery_var = tk.StringVar(value='0')
    speed_var = tk.StringVar(value='0')
    drive_mode_var = tk.StringVar(value='P')
    brake_var = tk.StringVar(value='0')
    gas_pedal_var = tk.StringVar(value='0')
    cruise_var = tk.StringVar(value='OFF')
    em_amps_var = tk.StringVar(value='0')
    em_volts_var = tk.StringVar(value='0')
    can_bus_var = tk.StringVar(value='0')
    em_power_var = tk.StringVar(value='0')
    batt_volts_var = tk.StringVar(value='0')
    engine_rpm_var = tk.StringVar(value='0')
    coolant_temp_var = tk.StringVar(value='0')
    steering_angle_var = tk.StringVar(value='0')
    frames_s_var = tk.StringVar(value='0')
    long_var = tk.StringVar(value='0')
    lat_var = tk.StringVar(value='0')
    gps_speed_var = tk.StringVar(value='0')
    sat_var = tk.StringVar(value='0')


    gas_label = tk.Label(window, font=label_font, textvariable=gas_var)
    battery_label = tk.Label(window, font=label_font, textvariable=battery_var)
    speed_label = tk.Label(window, font=label_font, textvariable=speed_var)
    drive_mode_label = tk.Label(window, font=label_font, textvariable=drive_mode_var)
    brake_percent_label = tk.Label(window, font=label_font, textvariable=brake_var)
    gas_pedal_label = tk.Label(window, font=label_font, textvariable=gas_pedal_var)
    em_amps_label = tk.Label(window, font=label_font, textvariable=em_amps_var)
    em_volts_label = tk.Label(window, font=label_font, textvariable=em_volts_var)
    em_power_label = tk.Label(window, font=label_font, textvariable=em_power_var)
    batt_volts_label = tk.Label(window, font=label_font, textvariable=batt_volts_var)
    can_bus_label = tk.Label(window, font=label_font, textvariable=can_bus_var)
    cruise_label = tk.Label(window, font=label_font, textvariable=cruise_var)
    engine_rpm_label = tk.Label(window, font=label_font, textvariable=engine_rpm_var)
    coolant_temp_label = tk.Label(window, font=label_font, textvariable=coolant_temp_var)
    steering_angle_label = tk.Label(window, font=label_font, textvariable=steering_angle_var)
    frames_s_label = tk.Label(window, font=label_font, textvariable=frames_s_var)
    long_label = tk.Label(window, font=label_font, textvariable=long_var)
    lat_label = tk.Label(window, font=label_font, textvariable=lat_var)
    gps_speed_label = tk.Label(window, font=label_font, textvariable=gps_speed_var)
    sat_label = tk.Label(window, font=label_font, textvariable=sat_var)

    can_bus_label.pack()
    if gps:
      long_label.pack()
      lat_label.pack()
      sat_label.pack()
    #frames_s_label.pack()
    drive_mode_label.pack()
    cruise_label.pack()
    gas_label.pack()
    battery_label.pack()
    steering_angle_label.pack()
    speed_label.pack()
    if gps:
      gps_speed_label.pack()
    brake_percent_label.pack()
    gas_pedal_label.pack()
    em_amps_label.pack()
    batt_volts_label.pack()
    #em_volts_label.pack()
    #em_power_label.pack()
    engine_rpm_label.pack()
    coolant_temp_label.pack()
    

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

    #start = time.time()
    if send_bool:
      enable_write(p)
    if gps:
      ser = serial.Serial(port, 4800, timeout=0.001) #
    while True:
      #start = time.time()
      try:
        if send_bool:
          p.can_send(0x57f, b'\xe8\x30\x10\x00\x00\x00\x00', 0)
        if gps:
          try:
            line = ser.readline()
            decoded_line = line.decode('ascii', errors='replace').strip()
            msg = pynmea2.parse(decoded_line)
            if msg == '': raise ValueError
            #print(repr(msg))
            if isinstance(msg, pynmea2.types.GGA):
                #if not hasattr(msg, 'latitude') or not hasattr(msg, 'longitude'):
                #    print("no satellite signal...")
                #    continue
                lat = msg.latitude
                lng = msg.longitude
            if isinstance(msg, pynmea2.types.GSA):
                sat_num = count_sv(msg)
            if isinstance(msg, pynmea2.types.VTG):
                sat_kph = msg.spd_over_grnd_kmph
                gps_speed = round(sat_kph * 0.62137, 2)
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
            #print('KPH (test reverse): ' + str(kph))
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
          #if str(hex(address)) == '0x57f': # HEADLIGHTS
            #print(dat.hex())
          #if str(hex(address)) == '0x520':
            #print(str(dat.hex()))
            #print((speed_int * 1100) / int(str(dat.hex())[2:], 16)) # Fuel Injector???
          #if str(hex(address)) == '0x39':
            #print(int(str(dat.hex())[:2], 16) * 9/5 + 32) # Engine temp C???
          
          if src == 0:
            can_bus_count += 1
        #if engine_rpm != 0:
          #print('MPG? : ' + str((kph * 10000) / (engine_rpm / 32)))
        
        
        now = datetime.datetime.now()
        nowstr = now.strftime(r'%H:%M:%S.%f')
        data[nowstr] = [nowstr, drive_mode, cruise, gas_int, batt_int, speed_int, brake_percent, gas_percent, em_amps, battery_volts, engine_rpm, coolant_temp, steering_data, can_bus_count, lat, lng, gps_speed, sat_num]
        #end = time.time()
        #print('Loop Time: ' + str(end - start))

        drive_mode_var.set('Drive Mode: ' + drive_mode)
        cruise_var.set('Cruise Control: ' + cruise)
        gas_var.set('Gas (%): ' + str(gas_int) + '%') # Gas is out of 40
        battery_var.set('Battery (%): ' + str(batt_int) + '%') # may be 0.5% increment
        speed_var.set('Speed (mph): ' + str(speed_int))
        brake_var.set('Brake Pedal (%) : ' + str(brake_percent))
        gas_pedal_var.set('Gas Pedal (%) : ' + str(gas_percent))
        if charging:
          em_amps_label.config(fg='green')
        else:
          em_amps_label.config(fg='red')
        em_amps_var.set('Electric Motor Current (A) : ' + str(abs(em_amps)))
        batt_volts_var.set('Battery Voltage (V) : ' + str(battery_volts))
        #em_power_var.set('Electric Motor Power (W) : ' + str(em_power))
        can_bus_var.set('CAN Frames Count : ' + str(can_bus_count))
        engine_rpm_var.set('Engine Revs (RPM) : ' + str(engine_rpm))
        coolant_temp_var.set('Coolant Temp (F) : ' + str(coolant_temp))
        steering_angle_var.set('Steering Angle (Deg) : ' + str(steering_data))
        #frames_s_var.set('Frames Per Second: ' + str(round(can_bus_count / (end - start), 2)))
        lat_var.set('Latitude : ' + str(lat))
        long_var.set('Longitude : ' + str(lng))
        sat_var.set('Sats in Use : ' + str(sat_num))
        gps_speed_var.set('GPS Speed (MPH) : ' + str(gps_speed))
        
        window.update()
      
      except KeyboardInterrupt:
        print('Exiting...')
        p.set_safety_mode(Panda.SAFETY_SILENT)
        window.destroy()
        ser.close()
        return data


if __name__ == "__main__":
  p = init_panda()
  gps = False
  #p = 0
  #can_recv = p.can_recv()
  #print(can_recv)
  #can_logger(p) # Log to csv
  #current(p) # test single address
  #send_data(p)
  data = gui(p, send_bool=False, gps=gps) # Ongoing dev of GUI
  to_csv(data)
  #plot(p) # moved to another file 'live-plot'.py