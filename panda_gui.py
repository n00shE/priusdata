import csv
from panda import Panda
import tkinter as tk
import tkinter.font as tkFont
import serial
import datetime
from cardata import CarData

def gui(p: Panda, gps=False):
    #wifi = p.get_serial()
    #print("SSID: " + wifi[0])
    #print("Password: " + wifi[1])
    port = 'COM3'
    ser = 0
    '''
    TODO:
    Add Doors
    '''
    window = tk.Tk()
    window.title("CAN Bussin")
    title_font = tkFont.Font(family="Times", size=24, weight=tkFont.BOLD)
    label_font = tkFont.Font(family="Times", size=20)
    title = tk.Label(text="2006 (Gen 2) Prius Monitor", font=title_font)
    #title.pack()
    title.grid(column=0)

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
    front_tire_var = tk.StringVar(value='0')
    #lfront_tire_var = tk.StringVar(value='0')
    #rrear_tire_var = tk.StringVar(value='0')
    rear_tire_var = tk.StringVar(value='0')
    minor_mismatch_var = tk.StringVar(value='0')
    major_mismatch_var = tk.StringVar(value='0')



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
    front_tire_label = tk.Label(window, font=label_font, textvariable=front_tire_var)
    rear_tire_label = tk.Label(window, font=label_font, textvariable=rear_tire_var)
    minor_mismatch_label = tk.Label(window, font=label_font, textvariable=minor_mismatch_var)
    major_mismatch_label = tk.Label(window, font=label_font, textvariable=major_mismatch_var)

    """ can_bus_label.pack()
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
    coolant_temp_label.pack() """

    #can_bus_label.grid(column=1, row=0)
    #frames_s_label.pack()
    drive_mode_label.grid(column=1, row=1)
    cruise_label.grid(column=1, row=2)
    gas_label.grid(column=1, row=3)
    battery_label.grid(column=1, row=4)
    steering_angle_label.grid(column=1, row=5)
    speed_label.grid(column=1, row=6)
    brake_percent_label.grid(column=1, row=7)
    gas_pedal_label.grid(column=1, row=8)
    em_amps_label.grid(column=1, row=9)
    batt_volts_label.grid(column=1, row=10)
    #em_volts_label.pack()
    #em_power_label.pack()
    engine_rpm_label.grid(column=1, row=11)
    coolant_temp_label.grid(column=1, row=12)
    if gps:
        gps_speed_label.grid(column=1, row=13)
        long_label.grid(column=1, row=14)
        lat_label.grid(column=1, row=15)
        sat_label.grid(column=1, row=16)
    front_tire_label.grid(column=0, row=3)
    rear_tire_label.grid(column=0, row=4)
    minor_mismatch_label.grid(column=0, row=5)
    major_mismatch_label.grid(column=0, row=6)

    

    data = CarData(gps=gps)

    if gps:
        ser = serial.Serial(port, 4800, timeout=0.001)
    
    if p != "test":
        now = datetime.datetime.now()
        file = 'output' + now.strftime(r'%m-%d-%H-%M-%S') + '.csv'
        f = open(file, 'w', encoding='utf8', newline='')
        csvwriter = csv.writer(f)
        while True:
            try:
                if gps:
                    data.get_gps_data(ser)
                can = p.can_recv()
                data.process_data(can)
                data.write_row(csvwriter)

                drive_mode_var.set('Drive Mode: ' + data.drive_mode)
                cruise_var.set('Cruise Control: ' + data.cruise)
                gas_var.set('Gas (%): ' + str(round(data.gas_p)) + '%') # Gas is out of 40
                battery_var.set('Battery (%): ' + str(round(data.batt_p, 1)) + '%') # may be 0.5% increment
                speed_var.set('Speed (mph): ' + str(data.speed_int))
                brake_var.set('Brake Pedal (%) : ' + str(data.brake_pedal))
                gas_pedal_var.set('Gas Pedal (%) : ' + str(data.gas_pedal))
                if data.charging:
                    em_amps_label.config(fg='green')
                else:
                    em_amps_label.config(fg='red')
                em_amps_var.set('Electric Motor Current (A) : ' + str(abs(data.em_amps)))
                batt_volts_var.set('Battery Voltage (V) : ' + str(data.battery_volts))
                #em_power_var.set('Electric Motor Power (W) : ' + str(em_power))
                can_bus_var.set('CAN Frames Count : ' + str(data.can_bus_count))
                engine_rpm_var.set('Engine Revs (RPM) : ' + str(data.engine_rpm))
                coolant_temp_var.set('Coolant Temp (F) : ' + str(data.coolant_temp))
                steering_angle_var.set('Steering Angle (Deg) : ' + str(data.steering_data))
                #frames_s_var.set('Frames Per Second: ' + str(round(can_bus_count / (end - start), 2)))
                front_tire_var.set(str(data.lfront_tire) + ' :LF-RF: ' + str(data.rfront_tire))
                rear_tire_var.set(str(data.lrear_tire) + ' :LR-RR: ' + str(data.rrear_tire))
                minor_mismatch_var.set(f"Minor wheel speed mismatch violations: {data.minor_mismatch}")
                major_mismatch_var.set(f"MAJOR wheel speed mismatch violations: {data.major_mismatch}")
                if gps:
                    lat_var.set('Latitude : ' + str(data.lat))
                    long_var.set('Longitude : ' + str(data.lng))
                    sat_var.set('Sats in Use : ' + str(data.sat_num))
                    gps_speed_var.set('GPS Speed (MPH) : ' + str(data.gps_speed))
                
                window.update()
        
            except KeyboardInterrupt:
                print('Exiting...')
                window.destroy()
                ser.close()
                return data
    else:
        while True:
            window.mainloop()

if __name__ == "__main__":
    p = Panda()
    #p = "test"
    gps = False
    data = gui(p, gps=gps) # Ongoing dev of GUI
