
#python3 test_vpn_connect.py

import sys
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import selenium
import time

import signal

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

#List of all free servers on ProtonVPN
def get_server_list():
    
    server_list = [
    "nl-free-01",
    "nl-free-02",
    "nl-free-03",
    "nl-free-04",
    "nl-free-05",
    "nl-free-06",
    "nl-free-07",
    "nl-free-08",
    "nl-free-09",
    "us-free-01",
    "us-free-02",
    "us-free-03",
    "us-free-04",
    "us-free-05",
    "jp-free-01",
    "jp-free-02",
    "jp-free-03"]

    return server_list

#Connects pi to ProtonVPN of given server name, returns true if successful
def connect_protonvpn(server):
    server = '-f'
    c_cmd = ['sudo','protonvpn','c',server]
    connected = False
    while connected == False:
        subprocess.run(c_cmd)
        response = subprocess.check_output(c_cmd)
        if "Connected!" in response.decode("utf-8"):
            return True
        else:
            subprocess.run('sudo','protonvpn','d','refresh')

#Disconnects pi from ProtonVPN, returns true if successful
def disconnect_protonvpn():
    d_cmd = ['sudo','protonvpn','d']
    connected = True
    while connected:
        subprocess.run(d_cmd)
        response = subprocess.check_output(d_cmd)
        if "Disconnected." in response.decode("utf-8"):
            return True
        else:
            subprocess.run('sudo','protonvpn','d','refresh')

#List of all faucet URLs that the user_list has accounts with
def free_faucet_list():

    faucet_list = ['https://freebitcoin.io/free',
    'https://free-doge.com/free',
    'https://coinfaucet.io/free',
    'https://freeusdcoin.com/free',
    'https://freebinancecoin.com',
    'https://freedash.io',
    'https://freechainlink.io',
    'https://freecardano.com',
    'https://free-ltc.com',
    'https://free-tron.com',
    'https://freetether.com',
    'https://freeethereum.com',
    'https://freesteam.io',
    'https://freenem.com']

    return faucet_list

#Dictionary of all user account email keys and password records
def get_user_list():
    
    user_list = {

        "user":"password",
        "user2":"password2"
    }

    return user_list

#Use to get both user and pword by iterating through dictionary
def get_key(dictionary, n):
    """This function takes a dictionary and an index n as input, and returns
    the n'th key of the dictionary by utilizing how dictionaries preserve the order
    of key entry during initialization."""

    i = 0
    for key in dictionary:
        if n == i:
            return key
        i = i + 1

#Returns usernames of each user in user_list()
def get_users():
    """Prevents need to treat dictionary as an iterable"""
    user_list = get_user_list()
    usernames = []
    for usr in user_list:
        usernames.append(usr)
    return usernames

#Starter function to visit every faucet for a given user
def visit_faucets(username, password):
    faucet_list = free_faucet_list()
    visits = 0
    for faucet_url in faucet_list:
        try:
            with timeout(seconds=90):
                if visit_single_faucet(username,password,faucet_url):
                    visits = visits + 1
        except:
            print("Error:",username,password,faucet_url)
            continue #Something with faucet/user failed
    return visits

#Selenium faucet interaction backend; visits faucet and rolls game
def visit_single_faucet(username,password,faucet_url):

    driver_path = '/usr/lib/chromium-browser/chromedriver' #Local path on pi

    #Initializes chromedriver, optionally headless
    headless = False
    if headless == True:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(driver_path,chrome_options=options)
    else:
        driver = webdriver.Chrome(driver_path)

    #Open and Initialize Faucet Website
    driver.get(faucet_url)
    driver.implicitly_wait(10)

    #Delete ad type 1 covering login button
    deleted_ad = True
    while deleted_ad == True:
        deleted_ad = False
        possible_ads = driver.find_elements_by_tag_name('div')
        for ad in possible_ads:
            try:
                if ad.get_attribute('onclick') == '$(this).parent().remove()':
                    ad.click()
                    driver.implicitly_wait(10)
                    break
            except:
                continue
    
    #Delete ad type 2
    deleted_ad = True
    while deleted_ad == True:
        deleted_ad = False
        possible_ads = driver.find_elements_by_tag_name('span')
        for ad in possible_ads:
            try:
                if ad.text == 'x':
                    ad.click()
                    driver.implicitly_wait(10)
                    deleted_ad = True
                    break
            except:
                continue
    
    #Login
    user_xpath = '/html/body/main/section/section[1]/div/div/div[2]/div/div[1]/div[1]/input'
    user_input = driver.find_element_by_xpath(user_xpath)
    user_input.send_keys(username)

    pword_xpath = '/html/body/main/section/section[1]/div/div/div[2]/div/div[1]/div[2]/input'
    pword_input = driver.find_element_by_xpath(pword_xpath)
    pword_input.send_keys(password)
            
    buttons = driver.find_elements_by_tag_name('button')
    for button in buttons:
        if button.text == 'LOGIN!':
            button.click()
            driver.implicitly_wait(10)

    #Click on roll button!
    roll_xpath = '/html/body/main/div/div/div/div/div/div[5]/button'
    rolled = False
    while rolled == False:
        try:
            roll_button = driver.find_element_by_xpath(roll_xpath)
            roll_button.click()
            rolled = True
        except:
            continue
        
    time.sleep(3.5) #Roll render
    print("rolled:",faucet_url)
    
    driver.quit() #Closes all selenium instances

    return True
    

def main():

    user_list = get_user_list()
    usernames = get_users()
    server_list = get_server_list()

    faucet_visits = 0
    
    while True:
        
        start_time = time.time()
        round_visits = 0

        #TODO: Is it okay to have the same accounts login from variable IPs?
        #Visits each faucet for each user at a relatively different IP address
        for i_usr in range(len(usernames)):

            i_server = i_usr % len(server_list) #Indexed servers have dynamic IPs when disconnected
            connect_protonvpn(server_list[i_server])
            usr_visits = visit_faucets(usernames[i_usr], user_list[usernames[i_usr]])
            disconnect_protonvpn()

            faucet_visits = faucet_visits + usr_visits
            round_visits = round_visits + round_visits
            print(usernames[i_usr],':',usr_visits,'  -  Round:',round_visits,'  -  Total:',faucet_visits)

        elapsed_time = time.time() - start_time
        if elapsed_time < 60*60: #Elapsed time < 1hr
            time.sleep(60*60 - elapsed_time + 300)

if __name__ == "__main__":
	main()
