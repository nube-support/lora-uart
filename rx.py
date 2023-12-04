import serial
import time

# Configure the serial connection
ser = serial.Serial(
    port='/dev/ttyACM0',  # Replace with your serial port
    #port='/dev/ttyUSB0',  # Replace with your serial port
    # baudrate=38400,
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

try:
    while True:
        # Read a line from the serial port
        line = ser.readline().decode('utf-8').rstrip()
        if line:
            print(line)
        time.sleep(0.1)  # Add a short delay to limit reading speed
except KeyboardInterrupt:
    pass
finally:
    ser.close()  # Always close the serial port