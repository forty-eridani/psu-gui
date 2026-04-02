import serial 

ser = serial.serial_for_url("rfc2217://127.0.0.1:4000", timeout=2)
