from cardata import CarData
import subprocess
import socket
import serial
import datetime
import time
import csv
from panda import Panda

# https://pimylifeup.com/raspberry-pi-spotify/

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 17380
call_beg = 'festival -b \'(voice_cmu_us_slt_arctic_hts)\' \'(SayText "'
call_end = '")\''
time.sleep(10)


def run(p: Panda) -> dict:
    gps = True
    voice = True
    port = '/dev/serial/by-id/usb-u-blox_AG_-_www.u-blox.com_u-blox_7_-_GPS_GNSS_Receiver-if00'
    ser = 0
    soc = socket.socket()
    soc_status = False

    data = CarData(gps=gps)
    
    now = datetime.datetime.now()
    file = '/home/pi/panda/output' + now.strftime(r'%m-%d-%H-%M-%S') + '.csv'
    f = open(file, 'w', encoding='utf8', newline='')
    csvwriter = csv.writer(f)
    csvwriter.writerow(['Time', 'DriveMode', 'CruiseControl', 'GasTank%', 'BatterySOC%', 'SpeedMPH', 'BrakePedal', 'GasPedal', 'EMAmps', 'BatteryVolts', 'EngineRPM', 'CoolantTemp', 'SteeringAngle', 'CANFrameCount', 'Latitude', 'Longitude', 'GPSSpeed', 'SatNum'])

    while True:
      #start = time.time()
      try:
        if voice and not soc:
          try:
            soc.connect((HOST, PORT))
            print('connected to socket')
            soc.settimeout(0.01)
            soc_status = True
          except:
            pass
        if gps and ser == 0:
            try:
                ser = serial.Serial(port, 4800, timeout=0.001)
            except Exception:
                pass
        if gps and ser != 0:
            data.get_gps_data(ser)
        can = p.can_recv()
        data.process_data(can)
        data.write_row(csvwriter)
    
        if voice:
          try:
            s_data = soc.recv(1024).decode()
            if s_data != '':
              try:
                print(s_data)
                print(data[s_data])
                call_mid = data.create_str(s_data)
                subprocess.call([call_beg + call_mid + call_end], close_fds=True, shell=True)
              except ValueError:
                  pass
          except OSError:
            soc_status = False
            print('not connected')
        #end = time.time()
        #print('Loop Time: ' + str(end - start))
      except KeyboardInterrupt:
        if gps:
          ser.close()
        f.close()
        print('closing...')


if __name__ == "__main__":
    p = Panda()
    run(p)