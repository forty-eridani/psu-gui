import serial 

ser = serial.serial_for_url("socket://127.0.0.1:4000", timeout=2)
ser.write(b"Grrrr this is a command")
