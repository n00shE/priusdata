import csv

readfile = "output12-21-15-39-32.csv"
writefile = "output12-21-15-39-32-filtered.csv"

if __name__ == "__main__":
    total = 0
    counter = 0
    written = 0
    with open(readfile) as csvread:
        with open(writefile, 'w', newline='') as csvwrite:
            reader = csv.reader(csvread)
            writer = csv.writer(csvwrite)
            writer.writerow(['Time','DriveMode','CruiseControl','GasTank%','BatterySOC%','SpeedMPH','BrakePedal','GasPedal','EMAmps','BatteryVolts','EngineRPM','CoolantTemp','SteeringAngle','CANFrameCount','Latitude','Longitude','GPSSpeed','SatNum'])
            for row in reader:
                total += 1
                #print(row)
                #print(row[17])
                if row[17] != 0:
                    if counter == 70:
                        counter = 0
                        writer.writerow(row)
                        written += 1
                    else:
                        counter += 1
                if total % 10000 == 0:
                    print(f'Reached line {total}')
                    print(f'Saved {written} lines')
