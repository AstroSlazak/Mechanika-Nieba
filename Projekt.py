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

def sat_position():
    #sprawdzenie czy dane zostały już ściągnięte
    if os.path.exists('TLE_SATELLITE.txt'):
        data = open('TLE_SATELLITE.txt', 'r').readlines()
    else:
        # Deklaracja strony do pobierania danych
        tle_url = 'http://www.celestrak.com/NORAD/elements/stations.txt'
        # Zwrócenie danych ze strony
        satellite_data = requests.get(tle_url).text
        # zapis danych do pliku txt
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

    number = input('Podaj numer satelity dla którego ma zostać wyznaczone położenie: ')
    sat_number = int(number) * 3 - 3
    return data[sat_number:sat_number+3]

def my_position():
    gmaps = googlemaps.Client(key='XXXXXXXXX')
    x = input('Określić twoje aktualne położenie jako miejsce obserwacji ? [t/n] ')

    if x.lower() == 't':
        g = geocoder.ip('me')
    else:
        y = str(input('Dla jakiego miejsca ma zostać wyznaczone położenie ? '))
        g = geocoder.google(y)

    lat = list(g.latlng)[0]
    lon = list(g.latlng)[1]
    e = gmaps.elevation(tuple(g.latlng))
    elev = e[0].get('elevation')
    place = g.city
    return lat, lon, elev, place

data = sat_position()
data1 = " ".join(data[0].split())
data2 = data[1]
data3 = data[2]

lat, lon, elev, place = my_position()
home = ephem.Observer()
home.lat = lat
home.lon = lon
home.elevation = elev
sat = ephem.readtle(data1, data2, data3)

matplotlib.rc('figure', figsize = (12, 6))
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
h_lon, h_lat = m(lon, lat)
m.plot(h_lon, h_lat,
        marker = '.',
        color = '#32caf6',
        markersize =6)

x_lon = []
y_lat = []

print('\n')
print('-' * 96)
print('Miejsce obserwacji: %s | longitude: %5.2f deg | latitude: %5.2f deg | elevation %5.2f m ' % (place, lon, lat, elev))
print('-' * 96)
print('\n')

while True:
    home.date = datetime.utcnow()
    sat.compute(home)
    print(data1 +" | altitude: %5.2f deg | azimuth %5.2f deg | longitude: %5.2f deg | latitude: %5.2f deg" % (math.degrees(sat.alt), math.degrees(sat.az), math.degrees(sat.sublong), math.degrees(sat.sublat)))

    x, y = m(math.degrees(sat.sublong),math.degrees(sat.sublat))
    x_lon.append(x)
    y_lat.append(y)
    m.plot(x_lon, y_lat, marker='_', markersize=2, color='r', linestyle='None', label=data1)
    title = plt.title(data1 +' | longitude: %5.2f deg | latitude: %5.2f deg \nObserwator: %s | longitude: %5.2f deg | latitude: %5.2f deg ' % (math.degrees(sat.sublong), math.degrees(sat.sublat), place, lon, lat))
    plt.ion()
    plt.draw()
    title.set_y(1.01)
    plt.show(block=False)
    plt.pause(0.5)
    time.sleep(1.0)
