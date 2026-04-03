import serial

ser = serial.serial_for_url('socket://127.0.0.1:4000')
ser.write(b"")
print(ser.readline().decode())
