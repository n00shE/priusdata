import csv
from cardata import CarData
import datetime
import serial
from panda import Panda

def run(p: Panda) -> dict:
    gps = True
    port = '/dev/serial/by-id/usb-u-blox_AG_-_www.u-blox.com_u-blox_7_-_GPS_GNSS_Receiver-if00'
    ser = 0

    data = CarData(gps=gps)
    
    now = datetime.datetime.now()
    file = '/home/pi/panda/output' + now.strftime(r'%m-%d-%H-%M-%S') + '.csv'
    f = open(file, 'w', encoding='utf8', newline='')
    csvwriter = csv.writer(f)
    csvwriter.writerow(['Time', 'DriveMode', 'CruiseControl', 'GasTank%', 'BatterySOC%', 'SpeedMPH', 'BrakePedal', 'GasPedal', 'EMAmps', 'BatteryVolts', 'EngineRPM', 'CoolantTemp', 'SteeringAngle', 'CANFrameCount', 'Latitude', 'Longitude', 'GPSSpeed', 'SatNum'])

    while True:
        #start = time.time()
        try:
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
        except:
            pass
if __name__ == "__main__":
    p = Panda()
    run(p)