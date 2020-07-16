from selenium import webdriver
import statistics
from browsermobproxy import Server
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import json
import numpy as np
import matplotlib.pyplot as plt

# file di input dei siti
f_in = '/home/sara/Scrivania/docs/siti_giornali'
# file di output delle misure dei dati
f_out = '/home/sara/Scrivania/docs/outputs_dati'
f_err = '/home/sara/Scrivania/docs/failures'


# Finds the button to clear cache and pushes it
# noinspection PyShadowingNames
def get_clear_browsing_button(driver):
    """Find the "CLEAR BROWSING BUTTON" on the Chrome settings page."""
    return driver.find_element_by_css_selector(
        '* /deep/ #clearBrowsingDataConfirm')


# Used to clear the cache any time graph is cleared
# noinspection PyUnusedLocal,PyShadowingNames
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
    elenco_ridotto = riduci_array(elenco)
    # fare la media dei rimanenti
    media = statistics.mean(elenco_ridotto)
    return media


def riduci_array(elenco):
    copia = list()
    for num in elenco:
        if num >= 0:  # non tengo conto di quelli andati male
            copia.append(num)
    print(len(copia))
    if len(copia) == 9:
        copia.pop(0)
    elif len(copia) == 10:
        copia.pop(0)
        copia.pop(len(copia) - 1)
    return copia


# noinspection PyShadowingNames
def calcola_dimensione(har):
    download = 0
    if "entries" in har["log"]:
        for value in har["log"]["entries"]:
            if "response" in value and "request" in value:
                download += int(value["response"]["bodySize"])

    return round(download/1000000, 2)  # ritorna i MB


# noinspection PyShadowingNames
def set_chrome(profilo):
    if profilo not in range(1, 4):
        pass
    else:
        # imposto il driver
        chromedriver = "/usr/local/bin/chromedriver"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
        chrome_options.add_argument('user-data-dir=/home/sara/.config/google-chrome/Profile '+str(profilo))
        driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrome_options)
        driver.set_page_load_timeout(90)
        return driver


# noinspection PyShadowingNames,PyShadowingNames,PyShadowingNames,PyShadowingNames
def visita(profilo, driver, statistiche, errori):
    if profilo not in range(1, 4):
        pass
    else:
        # devo iterare su tutti i siti della lista e per ognuno fare la prova 10 volte
        id_sito = 0
        for sito in lista:
            id_sito += 1
            # prendo solo il nome del sito per metterlo come nome del nuovo har
            split = sito.split(".")
            nome_sito = split[1]
            # creo una lista dove andrò a metterci tutti i valori di un sito
            valori = list()
            # creo un nuovo file nella scrivania dove salverò i dati di questo sito e lo apro in scrittura
            f_sito = "/home/sara/Scrivania/output_singoli/" + nome_sito
            if profilo == 1:
                doc = open(f_sito, "w")
            else:
                doc = open(f_sito, "a")
            # pulisco la cache di chrome
            # clear_cache(driver)
            for i in range(10):  # qui faccio tutte le get per un singolo sito ripetute
                try:
                    clear_cache(driver)
                except TimeoutException:
                    print("errore nella clear cache")
                    clear_cache(driver)  # riprovo
                try:
                    # creo un nuovo har
                    proxy.new_har(nome_sito + str(i))
                    # carico la pagina
                    driver.get(sito)
                    # cerco le entries
                    har = proxy.har  # returns a HAR JSON blob
                    # calcolo la dimensione dei dati scaricati in MB
                    dati = calcola_dimensione(har)
                except TimeoutException:
                    # segno la failure --> su che sito e il numero
                    errori[id_sito-1] += 1  # incremento gli errori del relativo sito
                    # assegno a questo caricamento un valore negativo
                    dati = -1.0
                    print("trovato errore")
                    clear_cache(driver)

                # scrivo i la qta di dati in byte
                valori.append(dati)
                doc.write(repr(dati))
                if i < 9:
                    doc.write("\n")
                    # out.write("{0} ".format(repr(tempo)))
            else:
                # chiudo il file del sito
                doc.close()
                # finito il ciclo calcolo la media
                media = calcola_media(valori)
                # aggiungo le medie alle varie liste
                if profilo == 1:
                    pulito.append(media)
                    statistiche[id_sito-1]["p"] = media
                elif profilo == 2:
                    adblock.append(media)
                    statistiche[id_sito-1]["a"] = media
                elif profilo == 3:
                    ublock.append(media)
                    statistiche[id_sito-1]["u"] = media
        else:
            driver.close()


def plot(data):
    ind = np.arange(10)  # the x locations for the groups
    width = 0.27  # the width of the bars

    fig = plt.figure()
    ax = fig.add_subplot(111)

    yvals, zvals, kvals = list(), list(), list()

    for diz in data:
        yvals.append(diz["p"])
        zvals.append(diz["a"])
        kvals.append(diz["u"])

    rects1 = ax.bar(ind, yvals, width, color='r')
    rects2 = ax.bar(ind + width, zvals, width, color='g')
    rects3 = ax.bar(ind + width * 2, kvals, width, color='b')

    ax.set_ylabel('Dati in MB')
    ax.set_xticks(ind + width)
    ax.set_xticklabels(('sito_1', 'sito_2', 'sito_3', 'sito_4', 'sito_5', 'sito_6',
                        'sito_7', 'sito_8', 'sito_9', 'sito_10'))
    ax.legend((rects1[0], rects2[0], rects3[0]), ('pulito', 'adblock', 'ublock'))

    plt.show()


# leggo il file con i siti e li metto in un vettore
lista = []  # inizializzo la lista di siti
for l in open(f_in).readlines():
    lista.append(l)
for p in lista:  # verifico che ci siano tutti i siti che ho nel file
    print(p)

# imposto il server per browsermob
server = Server("/home/sara/browsermob-proxy-2.1.4/bin/browsermob-proxy")
server.start()
proxy = server.create_proxy()

statistiche = list()
errori = dict()
for j in range(10):  # inizializzo il dict con un id per ogni sito e una lista in cui metterò i valori delle medie
    value = {'p': 0, 'a': 0, 'u': 0}
    statistiche.append(value)
    errori[j] = 0

# apro il file degli aoutputs in modalità scrittura
out = open(f_out, "w")
err = open(f_err, "w")

pulito, adblock, ublock = list(), list(), list()  # setto le 3 liste vuote in cui metterò tutte le medie

for i in range(1, 4):
    # faccio tre tipologie di visita:
    # --> 1) browser pulito
    # --> 2) browser con adblock plus
    # --> 3) browser con request policy o compatibile
    driver = set_chrome(i)
    visita(i, driver, statistiche, errori)

server.stop()
# scrivo nel file la media del sito corrente
json_str = json.dumps(statistiche)
out.write(json_str)
out.close()
for e in errori:
    err.write(str(e)+" - "+str(errori[e]))
err.close()
# plotto il risultato
plot(statistiche)
# plot_cdf(f_out)

for l in open(f_out).readlines():
    print(l)
