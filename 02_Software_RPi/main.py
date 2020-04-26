#!/usr/bin/env python
# --------------------------------------------------------------
# Technikerarbeit Elektrotechnik
# Alexander Wiltz, EW16
# --------------------------------------------------------------
# Thema:
# RaspberryPi mit DOT-Matrix-Anzeigen betrieben mittels MAX7219
# ueber SPI-Bus
# --------------------------------------------------------------

#Import der noetigen Bibliotheken
import max7219.led
from max7219.font import DEFAULT_FONT, LCD_FONT, UKR_FONT, TINY_FONT 
import time
import spidev

import bluetooth
import time

import datetime

#Zeitfunktionen
def getActualTime():
    #Zeit nehmen und splitten
    isTime = datetime.datetime.now()
    stunden = isTime.hour
    minuten = isTime.minute
    sekunden = isTime.second

    #Führende Nullen für die Uhrzeit und wandeln in String
    if stunden < 10:
        stunden = "0" + str(stunden)
    if minuten < 10:
        minuten = "0" + str(minuten)
    if sekunden < 10:
        sekunden = "0" + str(sekunden)

    return str(stunden), str(minuten), str(sekunden)

#Funktionen fuer die Bluetooth-Server
def startBTserverOnce():
    server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    port = 1
    server_sock.bind(("",port))
    server_sock.listen(1)
    client_sock,address = server_sock.accept()
    print("Akzeptiere Verbindung zu ",address[0])
    
    data = client_sock.recv(1024)
    print("empfange [%s]" % data)

    client_sock.close()
    server_sock.close()

def startBTServer():
    server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    port = 1
    server_sock.bind(("",port))
    server_sock.listen(1)
    client_sock,address = server_sock.accept()
    print("Akzeptiere Verbindung zu ",address[0])
    data = client_sock.recv(1024)
    return data
    time.sleep(0.02)

def nearby():
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    print("Gefundene Geräte %d" % len(nearby_devices))
    for addr, name in nearby_devices:
        print("  %s - %s" % (addr, name))

def findDevice(target_adress):
    target_name = "Added Device"
    nearby_devices = bluetooth.discover_devices()
    for bdaddr in nearby_devices:
        if target_name == bluetooth.lookup_name( bdaddr ):
            target_address = bdaddr
            break
    if target_address is not None:
        print("Gerät mit der Adresse", target_address, "gefunden.")
    else:
        print("Kein Gerät mit angegebener MAC-Adresse in Reichweite gefunden.")

#Hilfsvariablen
oldData = ""

#Definition bzw Start des SPI-Bus
spi = spidev.SpiDev()

#Paramterdefinition
font=LCD_FONT
cascaded = 8
brightness = 1

def initDisplay(cascaded, brightness):
    #Funktion zum initialisieren (siehe Datenblatt MAX7219)
    #Standardfunktion aus max7219 Bibliothek Problembehaftet
    bus = 0
    device = 0
    #Verbindung aufbauen
    spi.open(bus, device)
    #Taktfrequenz Bus definieren und Modus festlegen
    spi.max_speed_hz = 100000
    spi.mode = 0
    #Initschritte
    spi.xfer2([0xB,7]*cascaded) #Benutze alle Digits
    spi.xfer2([0x9,0]*cascaded) #Decodemode aus
    spi.xfer2([0xF,0]*cascaded) #Displaytest aus
    spi.xfer2([0xC,1]*cascaded) #Shutdownmode aus
    spi.xfer2([0xA,brightness]*cascaded) #Intensitaet 0-15 (Standard =3)

def brightnessPulses(cascaded, turns=1, endless=False):
    #Pulsiert Anzeige in Abhaengigkeit von 'turns', oder dauerhaft wenn 'endless=True'
    assert cascaded > 1 or cascaded==None, "Anzahl der angegebenen Module ueberpruefen"
    
    a = 0
    while endless or a in range(turns):
        for i in range(0,16):
            spi.xfer2([0xA,i]*cascaded)
            time.sleep(0.05)
        for i in range(0,16):
            i = 15-i
            spi.xfer2([0xA,i]*cascaded)
            time.sleep(0.05)
        a += 1

def static_text(msg, invert=False, font=None):
    #Zeigt Text ohne Bewegung an
    #Invertiert Text bei 'invert = True'
    assert len(msg) > 0, "Es wurde kein Text angegeben"
    
    try:
        #Beschneide String bei Ueberlaenge, sonst Fehler (zu wenig Geraete!)
        if len(msg) > cascaded:
            msg = msg[:-(len(msg)-cascaded)]
    except:
        None
    for i,j in enumerate(msg):
        if len(msg) < cascaded:
            offset = len(msg) - cascaded + 1
        elif len(msg) == cascaded:
            offset = 1
        if invert == False:
            i = len(msg) - i - offset
        device.letter(i, ord(j), font)

def scroll_text(msg, direction=False, invert=False, speed=0.25, turns=1, font=None):
    #Scrollt einen Text durch die Displays
    #'direction = False', scrollt von rechts nach links
    #'direction = True', scrollt von links nach rechts
    #'invert = True', dreht den Text um
    #'speed' beeinflusst die Scrollgeschwindigkeit in Sekunden/Wechsel
    #'turns' bestimmt die Anzahl der Wiederholungen
    assert len(msg) > 0, "Es wurde kein Text zum Scrollen angegeben"
    tmp = list()
    x = 0
    z = 0
    
    while z in range(turns):
        for i in msg:
            tmp.append(i)
        if invert == False and direction == True:
            tmp.reverse()
        elif direction == False and invert == True:
            tmp = [" "]*(cascaded-1) + tmp
            tmp.reverse()
        elif direction == False and invert == False:
            tmp = tmp + [" "]*(cascaded-1)
        tmp = [" "]*(cascaded-1) + tmp
        while x in range(len(tmp)):
            if len(tmp) >= cascaded:
                maxRange = cascaded
            else:
                maxRange = len(tmp)
            if direction == True:
                for i in range(maxRange):
                    device.letter(i,ord(tmp[i]), font)
                    if maxRange <= (cascaded-1):
                        i = maxRange
                        device.clear(i)
            else:
                k = cascaded - 1            
                for i in range(maxRange):
                    device.letter(k-i,ord(tmp[i]), font)
                    if maxRange <= cascaded-1:
                        k = maxRange
                        device.clear(k)

            try:
                del(tmp[0])
            except:
                None
               
            time.sleep(speed)
        device.clear()
        z += 1
    
#Treiber initialisieren vor Beginn der Anzeigen
initDisplay(cascaded, brightness)
#Funktionen aus max7219.led Lib
device = max7219.led.matrix(cascaded) #Klassendefinition als device
device.brightness(brightness) #Helligkeit vordefinieren (ueberschreibt aus max7219.led lib)
device.clear() #Anzeige komplett leeren
device.orientation(90) #Orientierung auf Standard setzen

msgInit = "Technikerarbeit 2020"
scroll_text(msgInit, direction=False, invert=False, speed=0.05, turns=1, font=font)

#Standardwerte setzen
direction=False
invert=False
speed=0.15
turns=1

oldSekunden = ""
print("Start BT-Server...")
count = 0
    
while True:
    #Bluetooth-Server starten und auf neue Nachrichten warten
    data = startBTServer()
    
    if "<#" and "#>" in data.decode("utf-8"):
        codeStrLst = data.decode("utf-8").split("<#")
        codeStrLst = codeStrLst[1].split("#>")
        codeStr = codeStrLst[0]
        print("Parameter detected:", codeStr)
        if "turns" in codeStr:
            try:
                turns = int(codeStr.split("=")[1])
                if turns > 9:
                    turns = 9
                elif turns < 1:
                    turns = 1
            except:
                None
            msgInfo = "Set 'turns' to " + str(turns)
        elif "dir" in codeStr:
            dirCheck = codeStr.split("=")[1]
            if dirCheck == "ltr":
                direction = True
            elif dirCheck == "rtl":
                direction = False
            else:
                None
            msgInfo = "Set 'direction' to " + str(direction)
        elif "inv" in codeStr:
            invCheck = codeStr.split("=")[1]
            if invCheck == "True":
                invert = True
            elif dirCheck == "False":
                invert = False
            else:
                None
            msgInfo = str("Set 'invertation' to ", invert)
        elif "speed" in codeStr:
            try:
                speed = float(codeStr.split("=")[1])
                if speed > 1:
                    speed = 1
                elif speed < 0.05:
                    speed = 0.05
            except:
                None
            msgInfo = "Set 'speed' to " + str(speed)
        elif "default" in codeStr:
            direction=False
            invert=False
            speed=0.15
            turns=1
            msgInfo = "Set all to default"
        elif "time" in codeStr:
            #Wechsel in Uhrzeitanzeige
            stunden, minuten, sekunden = getActualTime()
            msgTime = stunden + ":" + minuten + ":" + sekunden
            static_text(msgTime, invert=False, font=None)      
            time.sleep(0.02)
        else:
            msgInfo = "Unknown command"
            
        if not "time" in codeStr:
            print("Feedback:", msgInfo)
            scroll_text(msgInfo, direction=False, invert=False, speed=0.05, turns=1, font=font)
            
    elif data != oldData:
        print("New message received...")
        msg = str(data.decode("utf-8"))
        scroll_text(msg, direction, invert, speed, turns, font=font)
        oldData = data