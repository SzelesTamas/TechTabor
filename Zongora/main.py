#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import Motor
from pybricks.parameters import (Port, Stop, Direction)
from time import sleep
import threading
import queue

emelo = Motor(Port.A, Direction.COUNTERCLOCKWISE)
forgato = Motor(Port.C)
elore = Motor(Port.B, Direction.COUNTERCLOCKWISE)
mozgato = Motor(Port.D)

forgato_mozdulat = 120 # egy egységnyi forgatás fokban
elore_ido = 600 # kitolás/visszahúzás ideje ms-ben
emelo_mozdulat = 115 # felemeléshez/lenyomáshoz szükséges szög fokban
mozgato_mozdulat = 47 # egy billentyű mozgatásához szükséges szög fokban

billentyu_ido = 200 # egy billenytűt mozgás ms-ben
forgas_ido = 50 # egy egységnyi forgatás ideje ms-ben
lenyomas_ido = 120 # egy lenyomás ideje ms-ben


elore_hely = 0 # vissza van húzva 
forgato_irany = 2 # középen áll
hely_akt = 0 # kezdőhelyen áll
emelo_hely = 1 # fel van emelve
akkordok = {}

# minden akkord 3 paraméterrel rendelkezik
# 1. tavolsag a zongora vegetol
# 2. irany (balra, kozep, jobbra) (1, 2, 3)
# 3. nev

# a helynél a kezdőbillentyű a 0 

th = set()
kesz = False

def alaphelyzetbe():
    beallitElore(0)
    beallitHely(0)
    #beallitEmelo(1)

def beallitHely(cel):
    global hely_akt, mozgato, mozgato_mozdulat, th
    th.add('h')
    mozgato.run_angle(1000, (cel - hely_akt) * mozgato_mozdulat)
    hely_akt = cel
    th.discard('h')
    if(len(th) == 0):
        nyom()

def beallitElore(elo):
    global elore, elore_ido, elore_hely, th
    th.add('e')
    if(elo == 1):
        elore.run_time(1000, elore_ido)
    else:
        elore.run_time(-1000, elore_ido)
    elore_hely = elo
    th.discard('e')
    if(len(th) == 0):
        nyom()

def beallitForgato(irany):
    global forgato, forgato_irany, forgato_mozdulat, th
    th.add('f')
    forgato.run_angle(1000, (irany - forgato_irany) * forgato_mozdulat)
    forgato_irany = irany
    th.discard('f')
    if(len(th) == 0):
        nyom()

def beallitEmelo(fel):
    global emelo, emelo_mozdulat, emelo_hely
    emelo.run_angle(10000, (fel - emelo_hely) * emelo_mozdulat, Stop.HOLD )
    emelo_hely = fel
    
def nyom():
    global emelo_hely, kesz

    if(emelo_hely == 0):
        beallitEmelo(1)
    beallitEmelo(0)
    beallitEmelo(1)
    kesz = True
    print("kesz")

def eloreIdo(elore1, elore2):
    global elore_ido
    return abs(elore1-elore2)*elore_ido

def iranyIdo(irany1, irany2):
    global forgas_ido
    
    return abs(irany1 - irany2) * forgas_ido

def koztesIdo(akk1, akk2):
    global billentyu_ido
    mozgas_ido = abs(akkordok[akk1].hely - akkordok[akk2].hely) * billentyu_ido
    irany_ido = iranyIdo(akkordok[akk1].irany, akkordok[akk2].irany)
    elore_ido = eloreIdo(akkordok[akk1].elo, akkordok[akk2].elo)

    return max(max(elore_ido, irany_ido), mozgas_ido) + lenyomas_ido / 2

class Akkord:
    def __init__(self, nev, irany, hely, elo):
        self.nev = nev
        self.hely = hely
        self.irany = irany
        self.elo = elo
        
        global akkordok
        akkordok[nev] = self

    def lenyom(self):
        x = threading.Thread(target=beallitHely, args=(self.hely,))
        x.start()
        x = threading.Thread(target=beallitElore, args=(self.elo,))
        x.start()
        x = threading.Thread(target=beallitForgato, args=(self.irany,))
        x.start() 


def sipol(ido):
    brick.sound.beep(1000, 100, 100)
    sleep(ido - 0.1)    
    sipol(ido)

class Dal:
    def __init__(self, ut, utemek):
        self.ut = ut
        self.utemek = utemek

    def lejatszas(self, tempo):
        # a tempo megadja egy utem hany mp
        global akkordok, kesz

        aktAkkord = "C"
        utemHatar = threading.Thread(target=sipol, args=(tempo,))
        utemHatar.start()
        for utem in self.utemek:
            for akkord in range(utem[0]+1, len(utem)):
                akkordok[utem[akkord]].lenyom()
                ido = (tempo / self.ut) * utem[akkord-utem[0]] # az adott és a következő akkord lenyomása közötti idő
                ido -= koztesIdo(aktAkkord, utem[akkord]) / 1000 # 1
                ido -= lenyomas_ido / 2000 # 3
                
                sleep(ido)
                kesz = False
                aktAkkord = utem[akkord]
        
        brick.sound.beep(1000, 1000, 100)
        sleep(5)
        alaphelyzetbe()





c = Akkord("C", 2, 0, 0) 
dm = Akkord("Dm", 2, 1, 0)
d = Akkord("D", 3, 1, 1)
f = Akkord("F", 2, 3, 0)
fm = Akkord("Fm", 1, 3, 1)
g = Akkord("G", 2, 4, 0)
        
white_christmas = Dal(4, [[1, 4, "C"], [1, 4, "C"], [1, 4, "Dm"], [1, 4, "G"], \
    [1, 4, "F"], [2, 2, 2, "F", "G"], [1, 4, "C"], [1, 4, "C"], \
    [1, 4, "C"], [1, 4, "C"], [1, 4, "F"], [1, 4, "Fm"], \
    [1, 4, "C"], [2, 2, 2, "C", "D"], [1, 4, "Dm"], [1, 4, "G"], \
    [1, 4, "C"], [1, 4, "C"], [1, 4, "D"], [1, 4, "G"], \
    [1, 4, "F"], [2, 2, 2, "F", "G"], [1, 4, "C"], [1, 4, "C"], \
    [1, 4, "C"], [1, 4, "C"], [1, 4, "F"], [1, 4, "Fm"], \
    [1, 4, "C"], [1, 4, "G"], [1, 4, "C"], [1, 4, "C"]])


white_christmas.lejatszas(5)

