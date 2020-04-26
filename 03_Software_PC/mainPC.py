#!/usr/bin/python
#Alexander Wiltz, 2019

#<#code#>
#<#turns=999#> Anz WdH
#<#dir=ltr#><#dir=rtl#> Startrichtung
#<#inv=True#> Dreht Buchstaben
#<#speed=1#> Geschwindigkeit max=1 und min=0.01 (Pausenzeit)
#<#default#> Setzt alle Parameter auf Standard zurueck
#<#time#> Zeigt die aktuelle Uhrzeit an
'''
static_text(msg, invert=False, font=None)
Zeigt Text ohne Bewegung an (maximale Zeichenzahl = Anzahl Displays).
Dreht den Text um, wenn invert = True. Die Variable msg beinhaltet den anzuzeigenden Text. Für font ist ein alternativer Zeichensatz geplant, der allerdings noch nicht umgesetzt ist.

scroll_text(msg, direction=False, invert=False, speed=0.25, turns=1, font=None)
Lässt einen in msg angegebenen Text über das Display laufen. Veränderliche Parameter, wie direction, drehen die Startrichtung, invert dreht die Buchstaben, speed gibt die Scrollgeschwindigkeit an. Durch turns wird die Anzahl der Scrollwiederholungen festgelgt.
Font ist noch nicht umgesetzt.
'''

import bluetooth
import time

def nearby():
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    print("Gefundene Geräte %d" % len(nearby_devices))
    for addr, name in nearby_devices:
        print("  %s - %s" % (addr, name))

def findDevice(target_adress):
    target_name = "Added Device"
    #target_adress = "B8:27:EB:51:6E:53" #MAC-Adresse Raspberry
    nearby_devices = bluetooth.discover_devices()
    for bdaddr in nearby_devices:
        if target_name == bluetooth.lookup_name( bdaddr ):
            target_address = bdaddr
            break
    if target_address is not None:
        print("Gerät mit der Adresse", target_address, "gefunden.")
    else:
        print("Kein Gerät mit angegebener MAC-Adresse in Reichweite gefunden.")
    
def startBTClient(target_adress, msg):
    #target_adress = "B8:27:EB:51:6E:53" #MAC-Adresse Raspberry
    #msg = "Hallo Raspberry" #Message an Pi
    port = 1
    sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    sock.connect((target_adress,port))
    sock.send(msg)
    sock.close()

##################################################################################
msg = ""
oldMSG =""
#target_adress = "B8:27:EB:51:6E:53"

print("#############################################"),time.sleep(0.15)
print("Welcome to BT-Console for RaspberryPi-Project"),time.sleep(0.15)
print("#############################################"),time.sleep(0.15)

try:
    target_adress = str(input("\nMAC-Adresse des BT-Adapters eingeben: "))
except:
    none

while True:
    msg = str(input("Nachricht: "))
    if msg != oldMSG:
        startBTClient(target_adress, msg)
        oldMSG = msg
    else:
        continue

