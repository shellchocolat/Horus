from picamera import PiCamera
import sys

try:
    camera = PiCamera()
    print("[+] Camera is working")
except Exception as e:
    print(str(e))
    print("[-] Camera is not working")
    sys.exit(1)
