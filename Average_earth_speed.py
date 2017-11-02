import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from astropy import constants as const
import pandas as pd

while True:
    punkt = input("Dla ilu punktów liczona ma byś średnia prędkość: ")
    # sprawdza czy podana wartość jest liczbą całkowitą dodatnią
    if punkt.isdigit():
        R = const.R_earth.to('km')
        T = 24
        # funkcja która tworzy losowe współrzędnę punktów x,y,z (ndim = 3), dla których wektor będzie równy 1 http://mathworld.wolfram.com/SpherePointPicking.html (16)
        def losowe_punkty(npoints, ndim=3):
        # np.random.randn() tworzy tablicę rozkładu normalego Gaussa o 3 rzędach dla ndim = 3
            vec = np.random.randn(ndim, npoints)
         # np.linalg.norm() jest to funkcja która dla danej tablicy wykonuje obliczenie sqrt(x**2 + y**2 + z**2) a wtym przypadku "/=" dzieli tablicę vec/sqrt(x**2 + y**2 + z**2)
         # axis = 0 oznacza że obliczenie wykonuje dla danego rzędu
            vec /= np.linalg.norm(vec, axis=0)
            return vec
        # funkcja zwarcająca prędkość
        def v_punktu(k):
        # Prędkości dla danego punktu
            v = (2*np.pi*np.array(k))/T
        # Prędkość bezwzględna
            v_abs = np.sqrt(np.array(v)**2)
            return v_abs

        xi, yi, zi = losowe_punkty(int(punkt))
        # Jako że wektor promienia jest równy 1 należy go przemnożyć przez promień ziemi
        xi = np.array(xi) * R
        yi = np.array(yi) * R
        zi = np.array(zi) * R
        # prędkości bezwzględne punktów
        v_abs = v_punktu(xi)
        # prędkośc średnia
        v_sre = np.average(v_abs)
        # Tworzy plik excel i zapisuje w nim dane
        d = {'x[km]':np.array(xi),'y[km]':np.array(yi),'z[km]':np.array(zi),'V[km/h]':np.array(v_abs)}
        df = pd.DataFrame(d,index = np.arange(1,len(xi)+1))
        df.to_excel('Prędkość_i_współrzędne_dla_{}_punktów.xlsx'.format(punkt), sheet_name="Współrzędne i Prędkość")

        print("-"*75)
        print("\tPrędkość średnia dla {} punktów wynosi: {} km/h".format(punkt,round(v_sre,2)))
        print("-"*75)

        # Wykres pokazujący położenie punktów
        # Kąt phi niech ma 50 punktów od zera do PI
        phi = np.linspace(0, np.pi, 25)
        # Kąt theta jest w przedziale od zera do 2*PI i też niech ma 50
        theta = np.linspace(0, 2*np.pi, 25)
        """
            Obliczenia punktów na sferze
            x = r*sin(theta)*cos(phi)
            y = r*sin(theta)*sin(phi)
            z = r*cos(theta)

            r w tym przypadku to promień ziemi czyli R
        """
        x = R * np.outer(np.sin(theta), np.cos(phi))
        y = R * np.outer(np.sin(theta), np.sin(phi))
        z = R * np.outer(np.cos(theta), np.ones_like(phi))
        """
            funkcja outer() mnoży dwa wektory, a funkcja ones_like() tworzy
            wektor złożony z jedynek w tym przypadku wektor phi
        """

        #Wykres
        fig, ax = plt.subplots(1, 1, subplot_kw={'projection':'3d', 'aspect':'equal'})
        fig.suptitle('Rozmieszczenie punktów na powierzchni', fontsize=14, fontweight='bold')
        # Wykres siatki "Ziemi"
        ax.plot_wireframe(x, y, z, color='k', rstride=1, cstride=1)
        # Wykres rozmieszczenia Punktów
        ax.scatter(xi, yi, zi, s=100, c='g', zorder=10)
        # Osie
        plt.xlabel('X')
        plt.ylabel('Y')

        plt.show()
    else:
        print("Podana wartość nie jest liczbą całkowitą !")
    print("Chcesz sprawdzić dla innej liczby punktów ?")
    pyt = input("Jeśli TAK wciśnij T lub Y, jeśli NIE wciśnij cokolwiek ")
    if pyt.lower() == 't' or pyt.lower() == 'y' :
        pass
    else:
        print("Bye")
        break
