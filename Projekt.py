import requests
import os
import geocoder
import googlemaps
import time
import ephem
import math
from datetime import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib as mpl
from orbital import KeplerianElements as KE, earth
import warnings
import random
import numpy as np

# Usuwanie ostrzeżeń
def warn():
    warnings.warn("deprecated", DeprecationWarning)

# Typy satelitów
norad = {'Stacje kosmiczne':"http://www.celestrak.com/NORAD/elements/stations.txt",
        'Satelity wystrzelone w ostatnich 30 dniach':'http://www.celestrak.com/NORAD/elements/tle-new.txt',
        'Satelity nawigacyjne - GPS':'http://www.celestrak.com/NORAD/elements/gps-ops.txt',
        'Satelity nawigacyjne - GLONASS':'http://www.celestrak.com/NORAD/elements/glo-ops.txt',
        'Satelity nawigacyjne - GALILEO':'http://www.celestrak.com/NORAD/elements/galileo.txt',
        'Satelity nawigacyjne - BEIDOU':'http://www.celestrak.com/NORAD/elements/beidou.txt',
        'Satelity systemu wspomagającego - WAAS/EGNOS/MSAS':'http://www.celestrak.com/NORAD/elements/sbas.txt',
        'Satelity nawigacyjne - NAVY(NNSS)':'http://www.celestrak.com/NORAD/elements/nnss.txt',
        'Satelity nawigacyjne Rosyjskie na LEO':'http://www.celestrak.com/NORAD/elements/musson.txt',
        'Satelity pogodowe':'http://www.celestrak.com/NORAD/elements/weather.txt',
        'Satelity geostacjonarne':'http://www.celestrak.com/NORAD/elements/geo.txt',
        'Satelity naukowe':'http://www.celestrak.com/NORAD/elements/science.txt',
        'Satelity geodezyjne':'http://www.celestrak.com/NORAD/elements/geodetic.txt',
        'Satelity inżynierskie':'http://www.celestrak.com/NORAD/elements/engineering.txt',
        'Satelity edukacyjne':'http://www.celestrak.com/NORAD/elements/education.txt',
        'Satelity amatorskie':'http://www.celestrak.com/NORAD/elements/amateur.txt',
        'Satelity eksperymentalne':'http://www.celestrak.com/NORAD/elements/x-comm.txt',
        'Satelity militarne':'http://www.celestrak.com/NORAD/elements/military.txt',
        'Satelity typu cubesat':'http://www.celestrak.com/NORAD/elements/cubesat.txt',
        'Satelity Molniya':'http://www.celestrak.com/NORAD/elements/molniya.txt'}

# Wybór typu satelitów i zwrócenie adresu URL
def sat_typ():
    print("\n")
    # Wypisanie typów satelitów
    for i,(key, value)  in enumerate(norad.items(),1):
        print(i, key)
    print("\n")
    # Wybór satelitów
    type_sat = input("Wybierz typ satelitów: ")
    while True:
        # Sprawdzenie czy numery zostały
        if type_sat.isdigit() and int(type_sat) > 0 and int(type_sat) <= len(norad.keys()):
            break
        else:
            print("Numer {} jest nieprawidłowy \nWprowadź numery jeszcze raz".format(type_sat))
            type_sat = input('Podaj jeszcze raz numer: ')
            continue
    # Stworzenie listy kluczy
    x = list(norad.keys())
    print("Zostały wybrane:")
    print("\n")
    print("     ----- {} -----".format(x[int(type_sat)-1]))
    print("\n")
    # Przypisanie wybranego typu satelity i adresu URL do zmiennych
    key = x[int(type_sat)-1]
    url = norad.get(x[int(type_sat)-1])
    return key, url

# Operacje na plku TLE
def sat_position(key,url):
    # Zwrócenie danych ze strony
    data = requests.get(url).text
    # Zapis danych do pliku txt
    sat_data = open('{}.txt'.format(key),'w')
    sat_data.write(data)
    sat_data.close()
    data = open('{}.txt'.format(key), 'r').readlines()
    # Usunięcie znaków nowej lini
    data = [a for a in data if a != '\n']
    data = ''.join(data)
    data = data.split('\n')
    # wybranie nazw satelitów
    names = data[0::3]
    # Wypisanie nazw wszystkich satelitów
    for line, value in enumerate(names[:-1], 1):
        x = str(line).strip()
        print(x, value)
    # Wprowadzenie numeru satelity, i zwrócenie jej danych TLE
    print("\n")
    number = input('Podaj numery satelitów po przecinku dla którego ma zostać wyznaczone położenie: ')
    # Sprawdzenie czy wprowadzone numery są poprawne
    while True:
        # Wyodrębnienie poszczególnych numerów
        num = number.split(",")
        # Sprawdzenie czy numery zostały
        for i in num:
            if i.isdigit() and int(i) > 0 and int(i) <= len(names[:-1]):
                continue
            else:
                print("Numer {} jest nieprawidłowy !\nWprowadź numery jeszcze raz".format(i))
                number = input('Podaj jeszcze raz numery: ')
                break
        else:
            break
    print("Zostały wybrane:")
    print("-"*25)
    # Stworzenie listy danych dla wybranych satelitów
    n_data = []
    for i in num:
        sat_number = int(i) * 3 - 3
        print("     {}".format(names[int(i)-1]))
        n_data += data[sat_number:sat_number+3]
    # Stworzenie listy list satelitów [[sat1],[sat2]...[satn]]
    data = [n_data[i:i + 3] for i in range(0, len(n_data), 3)]
    return data

# Określenie pozycji obserwacji
def my_position():
    # Klucz do googlemaps elevation API
    key = open('key.txt', 'r').readlines()
    gmaps = googlemaps.Client(key = key[0])
    print("-"*25)
    x = input('Określić twoje aktualne położenie jako miejsce obserwacji ? [t/n] ')
    # Jeżeli lokalizacja ma zostać wyznaczona dla aktualnej pozycji wyznacz się ją na podstawie IP
    if x.lower() == 't':
        g = geocoder.ip('me')
    else:
        # Jeżeli dla dowolnego miejsca na podstwaie google
        y = str(input('Dla jakiego miejsca ma zostać wyznaczone położenie ? '))
        g = geocoder.google(y)
    # Wyznaczenie długości, szerokości, przewyższenie
    lat = list(g.latlng)[0]
    lon = list(g.latlng)[1]
    e = gmaps.elevation(tuple(g.latlng))
    elev = e[0].get('elevation')
    place = g.city
    print("Miejsce obserwacji: ")
    print("-"*25)
    print("     {}".format(place))
    print("-"*25)
    print("\n")
    return lat, lon, elev, place

# Pozbycie się ostrzeżeń
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    warn()
    key, url = sat_typ()
    # Wywołanie funkcji pozycji satelity i podział danych
    data = sat_position(key, url)

    # Wywołanie funcki własnej pozycji
    lat, lon, elev, place = my_position()

    # Geocentryczne dane orbity satelity
    for i in range(len(data)):
        # Wczytanie danych
        sat_orbit = KE.from_tle(data[i][1],data[i][2],earth)
        # Wyznaczenie prędkości
        v = math.sqrt(list(sat_orbit.v)[0]**2+list(sat_orbit.v)[1]**2+list(sat_orbit.v)[2]**2)
        # Pobranie okresu satelity
        period = sat_orbit.T
        # Przeliczenie okresu na H:m:s
        mins, secs = divmod(period, 60)
        hours, mins = divmod(mins, 60)
        # Wypisanie parametrów
        print("    ----- {} -----".format(" ".join(data[i][0].split())))
        print("\n")
        print('Parametry orbity:')
        print('Półoś wielka               = {} [km]' .format(round(sat_orbit.a/1000,3)))
        print('Mimośród:                  = {} [-]'  .format(round(sat_orbit.e,6)))
        print('Inklinacja:                = {} [deg]'.format(round((sat_orbit.i*180)/math.pi,1)))
        print('Długość węzła wstępującego = {} [deg]'.format(round((sat_orbit.raan*180)/math.pi,1)))
        print('Długość pericentrum        = {} [deg]'.format(round((sat_orbit.arg_pe*180)/math.pi,1)))
        print('Anomalia średnia           = {} [deg]'.format(round((sat_orbit.M*180)/math.pi,1)))
        print('Anomalia mimośrodowa       = {} [deg]'.format(round((sat_orbit.E*180)/math.pi,1)))
        print('Okres                      = {:02d}:{:02d}:{:02d} [H]'.format(int(hours), int(mins), int(secs)))
        print('Prędkość średnia           = {} [km/s]'.format(round(v/1000,4)))
        print('\n')

    # Określenie wielkości mapy
    mpl.rc('figure', figsize = (17, 7.5))
    # Określenie parametrów mapy
    # Wybór typu mapy, wyświetlanie, rozdzielczość mapy
    m = Basemap(projection='kav7', lon_0 = 0,
                llcrnrlat = -90, llcrnrlon = -180,
                urcrnrlat = 90, urcrnrlon = 180,
                resolution = 'l')
    # Linia konturu kontynentów
    m.drawcoastlines(linewidth=0)
    # Oś szerokości geograficznej
    m.drawparallels(np.arange(-90,91,30),labels=[1,0,0,0],fontsize=12)
    # Oś długości geograficznej
    m.drawmeridians(np.arange(-180,181,60), labels=[0,0,0,1],fontsize=12)
    # Linia brzegowa krajów
    m.drawcountries(color = 'white', linewidth = 0.25, linestyle = 'solid', zorder = 30)
    # Wypełnienie kontynentów i wód
    m.fillcontinents(color = '#1e1e1d',lake_color = 'white')
    # Mapa a'la Google
    # m.bluemarble()

    # Konwersja szerokości i długości geograficznej na parametry możliwe do wyświetlenia na mapie
    h_lon, h_lat = m(lon, lat)

    # Styl przedstawienia miejsca obserwacji na mapie
    m.plot(h_lon, h_lat, marker = '.', color = '#32caf6', markersize =6)

    # Wyświetlenie adnotacji miejsca obserwacji
    plt.text(h_lon + 100000, h_lat + 100000,place,size = 11,color='#32caf6',fontweight='bold')

    # Stworzenie losowych kolorów
    colors = []
    for i in range(len(data)):
        col = '#{:06x}'.format(random.randint(0, 256**3))
        col = [''.join(col)]
        colors += col

    # Deklaracja list dla szerokości i długości geograficznej satelity
    for i in range(len(data)):
        x = ""
        x = "x_lon" + str(i) + " = []"
        y = ""
        y = "y_lon" + str(i) + " = []"
        exec(x), exec(y)

    plt.ion()
    # Określenie zmiennych dla obserwatora
    home = ephem.Observer()
    home.lat = lat
    home.lon = lon
    home.elevation = elev

    # Pętla która oblicza położenie satelitów
    while True:
        # Deklaracja czasu UTC
        home.date = datetime.utcnow()
        # Listy położenia adnotacji satelitów
        x_label = []
        y_label = []
        for i in range(len(data)):
            # Wprowadzenie danych orbity satelity
            sat = ephem.readtle(" ".join(data[i][0].split()), data[i][1], data[i][2])
            # Obliczenia parametrów satelity
            sat.compute(home)
            # Konwersja szerokości i długości geograficznej na parametry możliwe do wyświetlenia na mapie
            x, y = m(math.degrees(sat.sublong), math.degrees(sat.sublat))
            # Dodanie położenia adnotacji satelitów do listy
            x_label.insert(i, x)
            y_label.insert(i, x)
            # Pokazanie adnotacji na mapie
            globals()['sat_labels'+str(i)] = plt.text(x + 100000, y + 100000," ".join(data[i][0].split()),size = 11,color=colors[i],fontweight='bold')
            # Dodanie parametrów satelity do listy
            globals()['x_lon'+str(i)].append(x)
            globals()['y_lon'+str(i)].append(y)
            # Przedstawienie trajektori satelitów na mapie
            m.plot(globals()['x_lon'+str(i)],globals()['y_lon'+str(i)], marker='_', markersize=1, color=colors[i], linestyle='None', label=" ".join(data[i][0].split()))
            # Tytuł wykresu
            title = plt.title( 'Observer: {} | Longitude: {} deg | Latitude: {} deg | Elevation: {} m \nTime: {} UTC'
                                .format(place, round(lon,2), round(lat,2), round(elev,2), datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")), fontsize = 14)
            # Pozycja tytułu
            title.set_y(1.01)
            # Wypisanie położenia satelitów
            print('{}: Altitude: {} deg | Azimuth: {} deg  | Longitude: {} deg | Latitude: {} deg'
                        .format(" ".join(data[i][0].split()), round(math.degrees(sat.alt),2), round(math.degrees(sat.az),2), round(math.degrees(sat.sublong),2), round(math.degrees(sat.sublat),2)))
            # print("-"*115)
            plt.draw()
        # Czasy przerw pomiędzy kolejnymi krokami pętli
        plt.pause(2.0)
        # time.sleep(1.0)
        print("-"*115)
        # Usuniecię adnotacji satelitów
        for i in range(len(data)):
            globals()['sat_labels'+str(i)].remove()
