#python3 test_email_ad_evade.py

import sys
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium
import time
import signal

#Global Variable
inbox_url = 'https://10minutemail.net'
chromedriver_path = '/usr/lib/chromium-browser/chromedriver' #Local path on pi

#Quits faucet if stalled
class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

#Connects pi to ProtonVPN of given server name, returns true if successful
def connect_protonvpn(server):
    server = '-f'
    c_cmd = ['sudo','protonvpn','c',server]
    connected = False
    while connected == False:
        subprocess.run(c_cmd)
        response = subprocess.check_output(c_cmd)
        if "Connected!" in response.decode("utf-8"):
            connected = True
        else:
            subprocess.run(['sudo','protonvpn','refresh'])

#Disconnects pi from ProtonVPN, returns true if successful
def disconnect_protonvpn():
    d_cmd = ['sudo','protonvpn','d']
    connected = True
    while connected:
        subprocess.run(d_cmd)
        response = subprocess.check_output(d_cmd)
        if "Disconnected" in response.decode("utf-8"):
            connected = False
        else:
            subprocess.run(['sudo','protonvpn','refresh'])

#Initialize and return webdriver for raspberry pi configuration
def init_webdriver(headless):

    if headless == True: #optionally headless
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chromedriver_path,chrome_options=options)
    else:
        driver = webdriver.Chrome(chromedriver_path)

    driver.set_window_size(1400, 600)
    driver.implicitly_wait(10)

    return driver

#Evades the inevitable 10minuteemail.net popup by shifting window frame size
def evade_email_popup(driver):
    driver.set_window_size(100, 400)
    time.sleep(3)
    driver.set_window_size(1400, 600)

    return driver


def main():
    
    checkpoint = time.time() #CHECKPOINT
    connect_protonvpn('f')
    print("VPN Connected:",time.time()-checkpoint) #CHECKPOINT

    checkpoint = time.time() #CHECKPOINT
    driver = init_webdriver(False)
    print("Driver initialized:",time.time()-checkpoint) #CHECKPOINT

    checkpoint = time.time() #CHECKPOINT
    driver.get(inbox_url)
    print("Init Page Loaded:",time.time()-checkpoint) #CHECKPOINT
    
    checkpoint = time.time() #CHECKPOINT
    message = driver.find_element_by_xpath("/html/body/div[1]/div[4]/div/table/tbody/tr[2]")
    message.click()
    print("Clicked element",time.time()-checkpoint) #CHECKPOINT
    
    checkpoint = time.time() #CHECKPOINT
    time.sleep(4)
    driver = evade_email_popup(driver)
    print("Ad evaded",time.time()-checkpoint) #CHECKPOINT

    disconnect_protonvpn()

if __name__ == "__main__":
	main()
