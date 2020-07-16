from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import time
import statistics
import matplotlib.pyplot as plt

# file di input dei siti
f_in = '/home/sara/Scrivania/docs/siti_10'
# file di output delle misure dei dati
f_out = '/home/sara/Scrivania/docs/outputs_tempi'


# Finds the button to clear cache and pushes it
def get_clear_browsing_button(driver):
    """Find the "CLEAR BROWSING BUTTON" on the Chrome settings page."""
    return driver.find_element_by_css_selector(
        '* /deep/ #clearBrowsingDataConfirm')


# Used to clear the cache any time graph is cleared
# noinspection PyUnusedLocal
def clear_cache(driver, timeout=60):
    """Clear the cookies and cache for the ChromeDriver instance."""
    # navigate to the settings page
    driver.get('chrome://settings/clearBrowserData')

    # wait for the button to appear
    wait = WebDriverWait(driver, timeout)
    wait.until(get_clear_browsing_button)

    # click the button to clear the cache
    get_clear_browsing_button(driver).click()

    # wait for the button to be gone before returning
    wait.until_not(get_clear_browsing_button)


def calcola_media(array):  # cercare i due max e i due min e toglierli e fare la media dei restanti
    elenco = list(array)
    elenco.sort()
    # se possibile cercare un metodo più veloce per togliere i primi due e gli ultimi due
    elenco.pop(0)
    elenco.pop(0)
    elenco.pop(len(elenco)-1)
    elenco.pop(len(elenco)-1)
    # fare la media dei rimanenti
    media = statistics.mean(elenco)
    return media


def plot_cdf(file):

    if file != f_out:
        pass
    else:
        data = list()
        for l in open(file).readlines():
            l.rstrip()
            num = round(float(l), 2)
            data.append(num)

        print(data)
        print(len(data))

        data.sort()
        max_data = data[len(data) - 1]
        # normalizzo tutti i tempi rispetto al max
        for i in range(len(data)):
            data[i] /= max_data
        print(data)
        # plotto i dati
        plt.plot(data)
        plt.show()


# leggo il file con i siti e li metto in un vettore
lista = []  # inizializzo la lista di siti
for l in open(f_in).readlines():
    lista.append(l)
for p in lista:  # verifico che ci siano tutti i siti che ho nel file
    print(p)
# scelgo chrome come driver
driver = webdriver.Chrome()

# apro il file degli aoutputs in modalità scrittura
out = open(f_out, "w")
# devo iterare su tutti i siti della lista e per ognuno fare la prova 10 volte
for sito in lista:
    valori = list()
    # pulisco la cache di chrome
    clear_cache(driver)
    for i in range(10):  # qui faccio tutte le get per un singolo sito ripetute
        # definisco il momento d'inizio
        start = time.time()
        # carico la pagina
        driver.get(sito)
        # calcolo il momento finale
        finish = time.time()
        # calcolo il tempo e poi vado a scrivere nel file
        tempo = round(finish-start, 5)
        valori.append(tempo)

        # out.write("{0} ".format(repr(tempo)))
    else:
        # finito il ciclo calcolo la media
        media = calcola_media(valori)
        # scrivo nel file la media del sito corrente
        out.write(repr(media))
        # finito il ciclo vado a stampare nel file un a capo
        if sito != "http://www.libero.it":
            out.write("\n")

else:
    driver.close()
    # chiudo il file e il browser
    out.close()
    # plotto il risultato
    plot_cdf(f_out)


for l in open(f_out).readlines():
    print(l)
