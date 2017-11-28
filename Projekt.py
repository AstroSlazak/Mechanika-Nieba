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
    data = ' '.join(data)
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
m = Basemap(projection='kav7',
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

# Konwersja szerokości i długości geograficznej na parametry możliwe do wyświetlenia na mapie
h_lon, h_lat = m(lon, lat)

# Styl przedstawienia miejsca obserwacji na mapie
m.plot(h_lon, h_lat,
        marker = '.',
        color = '#32caf6',
        markersize =6)

# Deklaracja list dla szerokości i długości geograficznej satelity
x_lon = []
y_lat = []

# Wypisanie położenia miejsca obserwacji
print('\n')
print('-' * 110)
print('\tMiejsce obserwacji: %s | longitude: %5.2f deg | latitude: %5.2f deg | elevation %5.2f m ' % (place, lon, lat, elev))
print('-' * 110)
print('\n')

# Pętla która oblicza położenie satelity w czasie rzeczywistym
while True:
    # Deklaracja czasu UTC
    home.date = datetime.utcnow()
    # Obliczenia parametrów satelity
    sat.compute(home)
    # Wypisanie danych
    print(data1 +" | altitude: %5.2f deg | azimuth %5.2f deg | longitude: %5.2f deg | latitude: %5.2f deg" % (math.degrees(sat.alt), math.degrees(sat.az), math.degrees(sat.sublong), math.degrees(sat.sublat)))
    # Konwersja szerokości i długości geograficznej na parametry możliwe do wyświetlenia na mapie
    x, y = m(math.degrees(sat.sublong), math.degrees(sat.sublat))
    # Dodanie parametrów satelity do listy
    x_lon.append(x)
    y_lat.append(y)
    # Styl przedstawienia satelity na mapie
    m.plot(x_lon, y_lat, marker='_', markersize=2, color='r', linestyle='None', label=data1)
    # Tytuł wykresu
    title = plt.title(data1 +' | longitude: %5.2f deg | latitude: %5.2f deg \nObserwator: %s | longitude: %5.2f deg | latitude: %5.2f deg ' % (math.degrees(sat.sublong), math.degrees(sat.sublat), place, lon, lat))
    # Pozycja tytułu
    title.set_y(1.01)
    plt.ion()
    plt.draw()
    plt.show(block=False)
    # Czasy przerw pomiędzy kolejnymi krokami pętli
    plt.pause(0.5)
    time.sleep(1.0)
