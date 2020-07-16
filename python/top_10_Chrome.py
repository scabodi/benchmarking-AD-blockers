from selenium import webdriver
import statistics
from browsermobproxy import Server
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import json
import numpy as np
import matplotlib.pyplot as plt
import time

# unisco insieme sia le statistiche sui dati che quelle sui tempi

# file di input dei siti --> uguale per entrambi
f_in = '/home/sara/Scrivania/docs/siti_giornali'
# file di output delle misure dei dati
f_out_dati = '/home/sara/Scrivania/docs/outputs_dati_chrome'
# file di output delle misure dei tempi
f_out_tempi = '/home/sara/Scrivania/docs/outputs_tempi_chrome'
# file degli errori
f_err = '/home/sara/Scrivania/docs/failures_chrome'


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
    minimo = elenco_ridotto[0]
    massimo = elenco_ridotto[len(elenco_ridotto) - 1]
    # fare la media dei rimanenti
    media = statistics.mean(elenco_ridotto)
    up = massimo - media
    down = media - minimo
    return media, up, down


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
    dati = download/1000
    return dati  # ritorna i KB


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
        chrome_options.add_argument('--disable-application-cache')  # stessa cosa di clear cache??
        driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chrome_options)
        driver.set_page_load_timeout(120)
        return driver


# noinspection PyShadowingNames,PyShadowingNames,PyShadowingNames,PyShadowingNames
def visita(profilo, driver, sito, nome_sito, id_sito):
    if profilo not in range(1, 4):
        pass
    else:
        # creo due liste dove andrò a metterci tutti i valori di un sito (una per i dati una per i tempi)
        valori_dati = list()
        valori_tempi = list()
        # creo un nuovo file nella scrivania dove salverò i dati di questo sito e lo apro in scrittura
        f_sito = "/home/sara/Scrivania/output_singoli/" + nome_sito + "_chrome"
        if profilo == 1:
            doc = open(f_sito, "w")
        else:
            doc = open(f_sito, "a")
        doc.write("Profilo "+repr(profilo)+" :\n")
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
                # definisco il momento d'inizio
                start = time.time()
                # carico la pagina
                driver.get(sito)
                # calcolo il momento finale
                finish = time.time()
                # calcolo il tempo e poi vado a scrivere nel file
                tempo = finish - start
                # round(tempo, 2)
                # cerco le entries
                har = proxy.har  # returns a HAR JSON blob
                # calcolo la dimensione dei dati scaricati in MB
                dati = calcola_dimensione(har)
            except TimeoutException:
                # segno la failure --> su che sito e il numero
                errori[id_sito] += 1  # incremento gli errori del relativo sito
                # assegno a questo caricamento un valore negativo
                dati = -1.0
                tempo = -1.0
                print("trovato errore")
                try:
                    # driver.get('about:preferences')
                    clear_cache(driver)
                except TimeoutException:
                    print("errore nella clear cache")
                    clear_cache(driver)  # riprovo

            # scrivo i la qta di dati in byte
            valori_dati.append(dati)
            valori_tempi.append(tempo)
            doc.write("Tempo = " + repr(tempo) + "---- Dati = " + repr(dati) + "\n")
            # out.write("{0} ".format(repr(tempo)))
        else:
            # chiudo il file del sito
            doc.close()
            # finito il ciclo calcolo la media
            media_dati, up_dati, down_dati = calcola_media(valori_dati)
            media_tempi, up_tempi, down_tempi = calcola_media(valori_tempi)
            # aggiungo le medie alle varie liste
            if profilo == 1:
                # per i Dati
                statistiche_dati[id_sito]["p"][0] = media_dati
                statistiche_dati[id_sito]["p"][1] = down_dati, up_dati
                err_puliti_dati[0].append(down_dati)
                err_puliti_dati[1].append(down_dati)
                # per i Tempi
                statistiche_tempi[id_sito]["p"][0] = media_tempi
                statistiche_tempi[id_sito]["p"][1] = down_tempi, up_tempi
                err_puliti_tempi[0].append(down_tempi)
                err_puliti_tempi[1].append(down_tempi)
            elif profilo == 2:
                # per i dati
                statistiche_dati[id_sito]["a"][0] = media_dati
                statistiche_dati[id_sito]["a"][1] = down_dati, up_dati
                err_adblock_dati[0].append(down_dati)
                err_adblock_dati[1].append(down_dati)
                # per i tempi
                statistiche_tempi[id_sito]["a"][0] = media_tempi
                statistiche_tempi[id_sito]["a"][1] = down_tempi, up_tempi
                err_adblock_tempi[0].append(down_tempi)
                err_adblock_tempi[1].append(down_tempi)
            elif profilo == 3:
                # per i dati
                statistiche_dati[id_sito]["u"][0] = media_dati
                statistiche_dati[id_sito]["u"][1] = down_dati, up_dati
                err_ublock_dati[0].append(down_dati)
                err_ublock_dati[1].append(down_dati)
                # per i tempi
                statistiche_tempi[id_sito]["u"][0] = media_tempi
                statistiche_tempi[id_sito]["u"][1] = down_tempi, up_tempi
                err_puliti_tempi[0].append(down_tempi)
                err_puliti_tempi[1].append(down_tempi)
            # chiudo il driver
            driver.close()
            print(statistiche_dati)
            print(statistiche_tempi)


# noinspection PyShadowingNames
def plot_multiplo(data, tempi, errori):
    # imposto le dimensioni della figure
    fig = plt.figure(figsize=(10, 8))
    fig.suptitle("Test 10 siti - CHROME", size=20)

    font = {'family': 'sans-serif',
            'color': 'black',
            'weight': 'normal',
            'size': 10,
            }

    ind = np.arange(10)
    width = 0.27
    # plotto il primo grafico dei DATI
    ax1 = plt.subplot(311)

    yvals, zvals, kvals = list(), list(), list()
    yyerr, zyerr, kyerr = err_puliti_dati, err_adblock_dati, err_ublock_dati
    # saranno liste con ognuna una lista di due valori all'interno
    # il primo è il valore della media e il secondo di yerr per l'error bar

    for diz in data:
        yvals.append(diz["p"][0])  # è una lista con una lista di due valori per ogni valore
        # yyerr.append(diz["p"][1])
        zvals.append(diz["a"][0])
        # zyerr.append(diz["a"][1])
        kvals.append(diz["u"][0])
        # kyerr.append(diz["u"][1])

    rects1 = ax1.bar(ind, yvals, width, color='r', yerr=yyerr)
    rects2 = ax1.bar(ind + width, zvals, width, color='g', yerr=zyerr)
    rects3 = ax1.bar(ind + width * 2, kvals, width, color='b', yerr=kyerr)

    ax1.set_ylabel('Dati in KB', fontdict=font)
    ax1.set_xticks(ind + width)
    ax1.set_xticklabels([])

    # ax1.legend((rects1[0], rects2[0], rects3[0]), ('pulito', 'adblock', 'ublock'))
    fig.legend((rects1[0], rects2[0], rects3[0]), ('pulito', 'adblock plus', 'ublock'), 'upper right')

    plt.setp(ax1.get_xticklabels(), visible=False)

    # plotto il secondo grafico dei TEMPI
    # share x only
    ax2 = plt.subplot(312, sharex=ax1)

    yvals, zvals, kvals = list(), list(), list()
    yyerr, zyerr, kyerr = err_puliti_tempi, err_adblock_tempi, err_ublock_tempi

    for diz in tempi:
        yvals.append(diz["p"][0])  # è una lista con una lista di due valori per ogni valore
        # yyerr.append(diz["p"][1])
        zvals.append(diz["a"][0])
        # zyerr.append(diz["a"][1])
        kvals.append(diz["u"][0])
        # kyerr.append(diz["u"][1])

    ax2.bar(ind, yvals, width, color='r', yerr=yyerr)
    ax2.bar(ind + width, zvals, width, color='g', yerr=zyerr)
    ax2.bar(ind + width * 2, kvals, width, color='b', yerr=kyerr)

    ax2.set_ylabel('Tempi in secondi', fontdict=font)
    ax2.set_xticks(ind + width)
    ax2.set_xticklabels([])
    # ax2.legend((rects1[0], rects2[0], rects3[0]), ('pulito', 'adblock', 'ublock'))

    # make these tick labels invisible
    plt.setp(ax2.get_xticklabels(), visible=False)

    # share x and y
    ax3 = plt.subplot(313, sharex=ax1, sharey=ax1)  # 313

    ax3.bar(ind + width, errori.values(), width, color='r')

    ax3.set_ylabel('Errori', fontdict=font)
    ax3.set_xticks(ind + width)
    ax3.set_xticklabels(('repubblica', 'gazzetta', 'ansa', 'sole24ore', 'corriere', 'stampa',
                         'messaggero', 'giornale', 'quotidiano', 'libero'), fontdict=font)

    fig.subplots_adjust(hspace=0.1)
    plt.savefig("/home/sara/Scrivania/docs/plots/tris_chrome.png")
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

statistiche_dati = []
statistiche_tempi = []
errori = dict()
# creo le liste di margini di errore per le 3 bar per i dati e per i tempi
err1_dati, err2_dati, err3_dati = [0, 0], [0, 0], [0, 0]
err1_tempi, err2_tempi, err3_tempi = [0, 0], [0, 0], [0, 0]
# creo 3 liste totali
err_puliti_dati, err_adblock_dati, err_ublock_dati = [list(), list()], [list(), list()], [list(), list()]
err_puliti_tempi, err_adblock_tempi, err_ublock_tempi = [list(), list()], [list(), list()], [list(), list()]
# err_puliti = (down_puliti, up_puliti) dove dwn e up sono due liste di 10 valori ciascuna
# --> un valore per ogni sito con pulito

for j in range(10):  # inizializzo il dict con un id per ogni sito e una lista in cui metterò i valori delle medie
    value = {'p': [0, err1_dati], 'a': [0, err2_dati], 'u': [0, err3_dati]}  # per ogni chiave metto 2 valori :
    # il primo è la media e il secondo e yerr che mi servirà per la error bar
    value1 = {'p': [0, err1_tempi], 'a': [0, err2_tempi], 'u': [0, err3_tempi]}
    statistiche_dati.insert(j, value)
    statistiche_tempi.insert(j, value1)
    errori[j] = 0

id_sito = 0
for sito in lista:  # per ogni sito faccio 10 prove per ogni profilo
    # prendo solo il nome del sito per metterlo come nome del nuovo har
    split = sito.split(".")
    nome_sito = split[1]
    for i in range(1, 4):
        # faccio tre tipologie di visita con 3 profili diversi
        driver = set_chrome(i)
        print("ID sito = "+repr(id_sito))
        visita(i, driver, sito, nome_sito, id_sito)
    id_sito += 1

server.stop()
# apro il file degli aoutputs in modalità scrittura
out_dati = open(f_out_dati, "w")
# scrivo nel file la media del sito corrente
json_str = json.dumps(statistiche_dati)
print(json_str)
out_dati.write(json_str)
out_dati.close()
# faccio lo stesso per i tempi
out_tempi = open(f_out_tempi, "w")
json_str1 = json.dumps(statistiche_tempi)
print(json_str1)
out_tempi.write(json_str1)
out_tempi.close()
# e per gli errori
err = open(f_err, "w")
json_str2 = json.dumps(errori)
err.write(json_str2)
err.close()
'''for e in errori:
    err.write(str(e)+" - "+str(errori[e])+"\n")
err.close()'''

# plotto il risultato
# plot_dati(statistiche_dati)
# plot_tempi(statistiche_tempi)
# plot_errori(errori)
plot_multiplo(statistiche_dati, statistiche_tempi, errori)
