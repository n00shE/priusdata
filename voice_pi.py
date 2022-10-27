import speech_recognition as sr
#from subprocess import call
import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 17380

for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
    if microphone_name == 'USB PnP Sound Device: Audio (hw:1,0)':
        mic = sr.Microphone(device_index=i)

r = sr.Recognizer()

print("A moment of silence, please...")
with mic as source: r.adjust_for_ambient_noise(source)
print("Set minimum energy threshold to {}".format(r.energy_threshold))

with socket.socket() as s:
    s.bind((HOST, PORT))
    print('Waiting for a connection...')
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            with mic as source:
                print('listening...')
                audio = r.listen(source)
            try:
                # recognize speech using Google Speech Recognition
                value = r.recognize_google(audio)
                print("You said {}".format(value))
                if 'speed' in value:
                    conn.sendall('SpeedMPH'.encode('utf-8'))
                elif 'battery' in value and 'percent' in value:
                    conn.sendall('BatterySOC%'.encode('utf-8'))
                elif 'gas' in value:
                    conn.sendall('GasTank%'.encode('utf-8'))
                elif 'amps' in value:
                    conn.sendall('EMAmps'.encode('utf-8'))
                elif 'volts' in value:
                    conn.sendall('BatteryVolts'.encode('utf-8'))
            except sr.UnknownValueError:
                print("Oops! Didn't catch that")
                continue
            except sr.RequestError as e:
                print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
                continue
            

