import os
import subprocess
import time
import PyChromeDevTools
import signal

FNULL = open(os.devnull, 'w')
SHORT_TIMEOUT = 2
PORT = 9222

N_PROFILI, N_SITI = 4, 30
f_in = '/home/sara/Desktop/docs/classi_siti'

lista = [l.split('\n')[0] for l in open(f_in).readlines()]
lista = lista[10:]

for profilo in range(N_PROFILI):

    PROFILE_DIR = '/home/sara/.config/google-chrome/profilo'+str(profilo+1)
    # faccio partire il profilo desiderato
    CHROME_CMD = "google-chrome --remote-debugging-port=" + str(PORT) + \
                 " --user-data-dir=" + PROFILE_DIR
    proc = subprocess.Popen(CHROME_CMD, shell=True, stdin=None, stdout=FNULL,
                            stderr=subprocess.STDOUT, close_fds=True, preexec_fn=os.setsid)
    time.sleep(SHORT_TIMEOUT)
    chrome = PyChromeDevTools.ChromeInterface()
    chrome.Network.enable()
    chrome.Page.enable()
    chrome.Network.setCacheDisabled()

    # for id_sito in range(N_SITI):
    chrome.Page.navigate(url='http://www.conrad.it')
    event1, messages1 = chrome.wait_event("Page.DOMContentEventFired", timeout=60)
    event2, messages2 = chrome.wait_event("Page.loadEventFired", timeout=60)
    # time.sleep(3)

    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    proc.kill()
