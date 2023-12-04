import serial
import time
import argparse
from serial.serialutil import SerialException


parser = argparse.ArgumentParser()
parser.add_argument('-p', metavar='port', type=str,
                    help='Serial port', default='/dev/ttyACM1')
parser.add_argument('-b', metavar='baud', type=int,
                    help='Serial baudrate', default=38400)
parser.add_argument('-t', metavar='timeout', type=int,
                    help='Serial timeout', default=0.25)
parser.add_argument('-v', metavar='version', type=str,
                    help='Firmware vesion', default='0.1.5-1')
parser.add_argument('-hv', metavar='HW version', type=str,
                    help='Hardware vesion', default='0.1')
parser.add_argument('-w', metavar='password', type=str,
                    help='password', default='N00BIO')
parser.add_argument('-nw', metavar='new password', type=str,
                    help='new password', default='new-N00BIO')
parser.add_argument('-dm', metavar='device make', type=str,
                    help='device make', default='UL')
parser.add_argument('-m', metavar='device model', type=str,
                    help='device model', default='0001')
parser.add_argument('-a', '--all', action='store_true',
                    help='Test all fields', default=False)
parser.add_argument('--prod', action='store_true',
                    help='Speeds up tests for prod builds', default=False)

args = parser.parse_args()

port = args.p
baud = args.b
timeout = args.t

print(port, baud, timeout)
print()

OK = b'OK'
ERROR = b'ERROR'
UNKNOWN = b'UNKNOWN'


def send(cmdFull, resp=OK):
    type = b''
    if b'?' in cmdFull:
        type = b'?'
    elif b'=' in cmdFull:
        type = b'='

    cmd = cmdFull
    if type != b'':
        cmd = cmdFull[:cmdFull.index(type)]
    print('CMD: ', cmdFull)

    while ser.in_waiting:
        ser.readline()
        #  print(ser.readline())

    ser.write(b'AT+')
    ser.write(cmdFull)
    ser.write(b'\n')

    line = None
    while not line or line[0] == b'\0' or line[0] == b'['[0]:
        line = ser.readline()
        print(line)

    assert(line != b'')

    ans = line[:line.index(b'\n')]
    if resp != UNKNOWN and type == b'?':
        assert(ans.index(b'+') == 0)
        assert(ans.index(b':') == len(cmd) + 1)
        assert(ans[1:ans.index(b':')] == cmd)
        ans = ans[ans.index(b':') + 1:]
    print('ANS: ', ans)
    return ans


def check(cmdFull, resp=OK):
    ans = send(cmdFull, resp)

    if isinstance(resp, list) and isinstance(resp[0], bytes):
        assert(ans in resp)
    if isinstance(resp, list) and isinstance(resp[0], int):
        assert(len(ans) >= resp[0] and len(ans) <= resp[1])
    elif isinstance(resp, int):
        assert(len(ans) == resp)
    elif isinstance(resp, str):
        assert(ans == bytes(resp, 'utf-8'))
    elif isinstance(resp, bytes):
        assert(ans == resp)

    if args.prod:
        time.sleep(0.02)
    else:
        time.sleep(0.08)

def checkListNum(cmdFull, resp1=0, resp2=1):
    ans = send(cmdFull, OK)

    ans_int = int(ans)
    if ans_int < resp1 or ans_int > resp2:
        assert(ans_int >= resp1 and ans_int <= resp2)

    if args.prod:
        time.sleep(0.02)
    else:
        time.sleep(0.08)


def version():
    check(b'FWVERSION?', args.v)
    check(b'FWVERSION=1', UNKNOWN)
    check(b'FWVERSION=', UNKNOWN)
    check(b'FWVERSION', UNKNOWN)

def uniqueID():
    check(b'UNIQUEID?', 24)
    check(b'UNIQUEID=1', UNKNOWN)
    check(b'UNIQUEID=', UNKNOWN)
    check(b'UNIQUEID', UNKNOWN)

def deviceMake():
    check(b'DEVICEMAKE?', args.dm)
    check(b'DEVICEMAKE=1', UNKNOWN)
    check(b'DEVICEMAKE=', UNKNOWN)
    check(b'DEVICEMAKE', UNKNOWN)

def deviceModel():
    check(b'DEVICEMODEL?', args.m)
    check(b'DEVICEMODEL=1', UNKNOWN)
    check(b'DEVICEMODEL=', UNKNOWN)
    check(b'DEVICEMODEL', UNKNOWN)

def deviceHWVersion():
    check(b'HWVERSION?', args.hv)
    check(b'HWVERSION=1', UNKNOWN)
    check(b'HWVERSION=', UNKNOWN)
    check(b'HWVERSION', UNKNOWN)

def clearSettStd():
    check(b'CLEARSETTINGSSTD', OK)
    if args.prod:
        time.sleep(0.25)
    else:
        time.sleep(0.7)

def clearSettRbx():
    check(b'CLEARSETTINGSRBX', OK)
    if args.prod:
        time.sleep(0.25)
    else:
        time.sleep(0.7)

def reset():
    check(b'SOFTRESET', OK)
    print('sleeping for 2\n')
    if args.prod:
        time.sleep(1.2)
    else:
        time.sleep(2)
    line = None

    # For USB serial, we need to re-open the serial port after a device reset
    ser.close()
    time.sleep(0.2)
    while True:
        try:
            ser.open()
        except SerialException:
            # try the port number above or below since the reset happens
            #  too fast for PCs to reassign the device to the same port
            serNum = int(ser.port[-1])
            if ser.port == port:
                serNum += 1
            else:
                serNum -= 1
            ser.port = ser.port[:-1]+str(serNum)
            continue
        break
    ser.readline()
    while ser.in_waiting or line != b'':
        line = ser.readline()
        #  print(line)

def loradetect():
    check(b'LORADETECT?', [b'0', b'1'])
    check(b'LORADETECT=', UNKNOWN)
    check(b'LORADETECT=0', UNKNOWN)
    check(b'LORADETECT', UNKNOWN)

def lrrkey():
    check(b'LRRKEY=00112233445566778899AABBCCDDEEFF', OK)
    check(b'LRRKEY=00112233445566778899AABBCCDDEEF', ERROR)
    check(b'LRRKEY=00112233445566778899AABBCCDDEEFFF', ERROR)
    check(b'LRRKEY=', ERROR)
    check(b'LRRKEY?', UNKNOWN)
    check(b'LRRKEY=0301021604050F07E6095A0B0C12630F', OK)

def lrraddr():
    check(b'LRRADDRUNQ?', 8)
    check(b'LRRADDRUNQ=01234567', UNKNOWN)

def loraLoad():
    # check(b'LORALOAD=1+1+23.45', OK)
    check(b'LORALOAD', UNKNOWN)
    check(b'LORALOAD=', ERROR)
    check(b'LORALOAD=1', ERROR)
    check(b'LORALOAD=A,8', ERROR)

def loraClearBuffer():
    check(b'LORACLEARBUFFER', OK)
    check(b'LORACLEARBUFFER=', UNKNOWN)
    check(b'LORACLEARBUFFER?', UNKNOWN)
    check(b'LORACLEARBUFFER=1', UNKNOWN)

def loraBuffer():
    checkListNum(b'LORABUFFER?', 0, 2048)
    check(b'LORABUFFER=', UNKNOWN)
    check(b'LORABUFFER=1', UNKNOWN)

def loraReady():
    check(b'LORAREADY?', b'0')
    check(b'LORAREADY=', UNKNOWN)
    check(b'LORAREADY?=', UNKNOWN)
    check(b'LORAREADY=1', UNKNOWN)

def loraPush():
    check(b'LORAPUSH', OK)
    check(b'LORAPUSH=', UNKNOWN)
    check(b'LORAPUSH?=', UNKNOWN)
    check(b'LORAPUSH=1', UNKNOWN)


def appSettingsTest():
    # clear buffer
    check(b'LORACLEARBUFFER', OK)

    # set data
    check(b'LORALOAD=1+1+23.45', OK)    # temp
    check(b'LORALOAD=2+2+87.16', OK)    # humi
    check(b'LORALOAD=3+3+12', OK)    # lux
    check(b'LORALOAD=4+4+1', OK)        # movement
    check(b'LORALOAD=5+5+1234', OK)    # Pulses/counter
    check(b'LORALOAD=6+6+0', OK)        # Digital
    check(b'LORALOAD=7+7+5.71', OK)      # 0-10V
    check(b'LORALOAD=8+8+15.21', OK)    # 4-20mA
    check(b'LORALOAD=10+10+135790', OK) # Ohm
    check(b'LORALOAD=11+11+350', OK)  # CO2
    check(b'LORALOAD=12+12+5.2', OK)   # Battery Voltage
    check(b'LORALOAD=13+13+1145', OK)   # Push Freqency
    check(b'LORALOAD=30+30+123', OK)    # uint8
    check(b'LORALOAD=31+31+-34', OK)    # int8
    check(b'LORALOAD=32+32+3456', OK)   # uint16
    check(b'LORALOAD=33+33+-7531', OK)  # int16
    check(b'LORALOAD=34+34+98765432', OK)   # uint32
    check(b'LORALOAD=35+35+-555444', OK)    # int32
    check(b'LORALOAD=38+38+1', OK)      # bool
    check(b'LORALOAD=39+39+a', OK)      # char
    check(b'LORALOAD=40+40+278.91', OK) # float

    check(b'LORAREADY?', b'0')

    check(b'LORAPUSH', OK)

    # while True:
    #     line = ser.readline()
    #     print(line)


class bcolors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def test(func):
    print(f'->{bcolors.BOLD} {func.__name__}{bcolors.ENDC}')
    func()
    print(f'{bcolors.GREEN}  PASSED{bcolors.ENDC}')


with serial.Serial(port, baud, timeout=timeout) as ser:
    ser.readline()
    while ser.in_waiting:
        ser.readline()

    start_time = time.time()
    if args.all:
        test(uniqueID)
        test(version)
        test(deviceMake)
        test(deviceModel)
        test(deviceHWVersion)

        test(loradetect)
        test(lrrkey)
        test(lrraddr)

        test(loraLoad)
        test(loraBuffer)
        test(loraClearBuffer)
        test(loraReady)
        test(loraPush)
        time.sleep(1)


    test(appSettingsTest)

    time.sleep(1)
    line = ser.readline()
    print(line)

print(f'{bcolors.BOLD}{bcolors.GREEN}PASSED{bcolors.ENDC}')
print(f'Tests completed in: {round(time.time()-start_time, 2)}s')
