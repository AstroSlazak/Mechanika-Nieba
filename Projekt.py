import requests
import os
import geocoder
import googlemaps
import time
import ephem
import math
from datetime import datetime
from mpl_toolkits.basemap import Basemap
import matplotlib
import matplotlib.pyplot as plt
from orbital import KeplerianElements as KE , earth
from orbital.utilities import Position, Velocity
from astropy.time import Time
import warnings

# Funkcja pozbycia się ostrzeźeń
def warn():
    warnings.warn("deprecated", DeprecationWarning)

# Funkcja do pobierania, zapisywania, i przetwarzania danych TLE satelitów
def sat_position():
    # Sprawdzenie czy dane zostały już ściągnięte
    if os.path.exists('TLE_SATELLITE.txt'):
        data = open('TLE_SATELLITE.txt', 'r').readlines()
    else:
        # Deklaracja strony do pobierania danych
        tle_url = 'http://www.celestrak.com/NORAD/elements/stations.txt'
        # Zwrócenie danych ze strony
        satellite_data = requests.get(tle_url).text
        # Zapis danych do pliku txt
        sat_data = open('TLE_SATELLITE.txt','w')
        sat_data.write(satellite_data)
        sat_data.close()
        data = open('TLE_SATELLITE.txt', 'r').readlines()

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
    number = input('Podaj numer satelity dla którego ma zostać wyznaczone położenie: ')
    sat_number = int(number) * 3 - 3
    return data[sat_number:sat_number+3]

# Określenie pozycji obserwacji
def my_position():
    # Klucz do googlemaps elevation API
    key = open('key.txt', 'r').readlines()
    gmaps = googlemaps.Client(key = key[0])
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
    return lat, lon, elev, place

# Funkcja do zamiany współrzędnych topocentrycznych na geocentryczne
def top_to_geo(lat, lon, elev=0):
    # Promień ziemi
    R = ephem.earth_radius
    # Współczynnik spłaszczenia ziemi
    f = 1/298.257223563
    # Współczynniki do obliczeń
    F = (1-f)**2
    C = 1/(math.sqrt(math.cos(lat)**2 + F * math.sin(lat)**2))
    S = C*F
    # Obliczenie współrzędnych kartezjańwszystkich
    x = (R * C + elev)*math.cos(lat) * math.cos(lon)
    y = (R * C + elev)*math.cos(lat) * math.sin(lon)
    z = (R * S + elev)*math.sin(lat)
    return x, y, z

# Pozbycie się ostrzeżeń
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    warn()
    # Wywołanie funkcji pozycji satelity i podział danych
    data = sat_position()
    data1 = " ".join(data[0].split())
    data2 = data[1]
    data3 = data[2]

    # Wywołanie funcki własnej pozycji
    lat, lon, elev, place = my_position()

    # Określenie zmiennych dla obserwatora
    home = ephem.Observer()
    home.lat = lat
    home.lon = lon
    home.elevation = elev

    # Wprowadzenie danych orbity satelity
    sat = ephem.readtle(data1, data2, data3)

    # Określenie wielkości mapy
    matplotlib.rc('figure', figsize = (12, 6))

    # Określenie parametrów mapy
    m = Basemap(projection='robin',
                lon_0 = 0,
                llcrnrlat = -90,
                llcrnrlon = -180,
                urcrnrlat = 90,
                urcrnrlon = 180,
                resolution = 'l')
    m.drawcoastlines(linewidth=0)
    m.drawcountries(color = 'white',
                    linewidth = 0.25,
                    linestyle = 'solid',
                    zorder = 30)
    m.fillcontinents(color = '#1e1e1d',
                    lake_color = 'white')
    # Mapa a'la Google
    # m.bluemarble()

    # Konwersja szerokości i długości geograficznej na parametry możliwe do wyświetlenia na mapie
    h_lon, h_lat = m(lon, lat)

    # Styl przedstawienia miejsca obserwacji na mapie
    m.plot(h_lon, h_lat,
            marker = '.',
            color = '#32caf6',
            markersize =6)

    # Geocentryczne dane orbity satelity
    sat_orbit = KE.from_tle(data2,data3,earth)
    period = sat_orbit.T
    mins, secs = divmod(period, 60)
    hours, mins = divmod(mins, 60)
    print('*'*100)
    print('\n')
    print('Orbital parameters')
    print('Semimajor axis                    = {} [km]' .format(round(sat_orbit.a/1000,3)))
    print('Eccentricity:                     = {} [-]'  .format(round(sat_orbit.e,6)))
    print('Inclination:                      = {} [deg]'.format(round((sat_orbit.i*180)/math.pi,1)))
    print('Right ascension of ascending node = {} [deg]'.format(round((sat_orbit.raan*180)/math.pi,1)))
    print('Argument of perigee               = {} [deg]'.format(round((sat_orbit.arg_pe*180)/math.pi,1)))
    print('Mean anomaly                      = {} [deg]'.format(round((sat_orbit.M*180)/math.pi,1)))
    print('Eccentricity anomaly              = {} [deg]'.format(round((sat_orbit.E*180)/math.pi,1)))
    print('Period                            = {:02d}:{:02d}:{:02d} [H]'.format(int(hours), int(mins), int(secs)))

    # Deklaracja list dla szerokości i długości geograficznej satelity
    x_lon = []
    y_lat = []

    plt.ion()
    # Pętla która oblicza położenie satelity w czasie rzeczywistym

    while True:
        # Deklaracja czasu UTC
        home.date = datetime.utcnow()
        # Obliczenia parametrów satelity
        sat.compute(home)
        # Konwersja szerokości i długości geograficznej na parametry możliwe do wyświetlenia na mapie
        x, y = m(math.degrees(sat.sublong), math.degrees(sat.sublat))
        # Dodanie parametrów satelity do listy
        x_lon.append(x)
        y_lat.append(y)
        # Styl przedstawienia satelity na mapie
        m.plot(x_lon, y_lat, marker='_', markersize=1, color='r', linestyle='None', label=data1)
        # Tytuł wykresu
        title = plt.title( 'Observer: {} | Lon: {} deg | Lat: {} deg | Ele: {} m \n{}: Alt: {} deg | Azi: {} deg  | Lon: {} deg | Lat: {} deg'
                            .format(place, round(lon,2), round(lat,2), round(elev,2), data1, round(math.degrees(sat.alt),2), round(math.degrees(sat.az),2), round(math.degrees(sat.sublong),2), round(math.degrees(sat.sublat),2)), fontsize = 14)
        # Pozycja tytułu
        title.set_y(1.01)
        # Czasy przerw pomiędzy kolejnymi krokami pętli
        plt.tight_layout()
        plt.draw()
        plt.pause(0.25)
        time.sleep(1.0)
