import serial
import pynmea2
import sys
import datetime



def logfilename():
    now = datetime.datetime.now()
    return 'NMEA_%0.4d-%0.2d-%0.2d_%0.2d-%0.2d-%0.2d.nmea' % \
                (now.year, now.month, now.day,
                 now.hour, now.minute, now.second)

def log(port: str):
    try:
        # try to read a line of data from the serial port and parse
        with serial.Serial(port, 4800, timeout=1) as ser:
            # log data
            outfname = logfilename()
            sys.stderr.write('Logging data on %s to %s\n' % (port, outfname))
            with open(outfname, 'wb') as f:
                # loop will exit with Ctrl-C, which raises a
                # KeyboardInterrupt
                while True:
                    line = ser.readline()
                    decoded_line = line.decode('ascii', errors='replace').strip()
                    print(line)
                    print(decoded_line)
                    print(repr(pynmea2.parse(decoded_line)))
                    f.write(line)
        
    except Exception as e:
        sys.stderr.write('Error reading serial port %s: %s\n' % (type(e).__name__, e))
    except KeyboardInterrupt as e:
        sys.stderr.write('Ctrl-C pressed, exiting log of %s to %s\n' % (port, outfname))

#https://github.com/Perseus-II/GPS/blob/master/gps.py
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


def get_info(port: str):
    try:
        #with serial.Serial(port, 4800, timeout=1) as ser:
        ser = serial.Serial(port, 4800, timeout=1)
        while True:
            line = ser.readline()
            decoded_line = line.decode('ascii', errors='replace').strip()
            msg = pynmea2.parse(decoded_line)
            #print(repr(msg))
            if isinstance(msg, pynmea2.types.GGA):
                if not hasattr(msg, 'latitude') or not hasattr(msg, 'longitude'):
                    print("no satellite signal...")
                    continue
                lat = msg.latitude
                lng = msg.longitude
                print(f'Lat: {lat} Long: {lng}')
            if isinstance(msg, pynmea2.types.GSA):
                num_sv_in_use = count_sv(msg)
                print(f'Sats in use: {num_sv_in_use}')
            if isinstance(msg, pynmea2.types.VTG):
                sat_kph = msg.spd_over_grnd_kmph
                print(f'MPH: {round(sat_kph * 0.62137, 3)}')

    except Exception as e:
        sys.stderr.write('Error reading serial port %s: %s\n' % (type(e).__name__, e))
    except KeyboardInterrupt as e:
        sys.stderr.write('Ctrl-C pressed, exiting %s\n' % (port))
        ser.close()



if __name__ == "__main__":
    get_info('COM3')
