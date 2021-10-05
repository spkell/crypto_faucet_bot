
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

#Password generator
import random
import string

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
    c_cmd = ['sudo','protonvpn','c',server]
    connected = False
    while connected == False:
        subprocess.run(c_cmd)
        response = subprocess.check_output(c_cmd)
        if "Connected!" in response.decode("utf-8"):
            return True
        else:
            subprocess.run(['sudo','protonvpn','refresh'])

#Disconnects pi from ProtonVPN, returns true if successful
def disconnect_protonvpn():
    d_cmd = ['sudo','protonvpn','d']
    connected = True
    while connected:
        subprocess.run(d_cmd)
        response = subprocess.check_output(d_cmd)
        if "Disconnected." in response.decode("utf-8"):
            return False
        else:
            subprocess.run(['sudo','protonvpn','d','refresh'])

#List of all faucet URLs to create accounts for
def get_ref_links():

    short_ref_links = [
    'https://free-doge.com/?ref=52484',
    'https://freeusdcoin.com/?ref=114441',
    'https://freebinancecoin.com/?ref=128599',
    'https://freedash.io/?ref=104856',
    'https://freechainlink.io/?ref=64749',
    'https://free-ltc.com/?ref=91188',
    'https://free-tron.com/?ref=180105',
    'https://freetether.com/?ref=161367',
    'https://freeethereum.com/?ref=174149',
    'https://freesteam.io/?ref=106608',
    ]

    return short_ref_links

#Names of faucets in confirmation emails
def get_faucet_names():

    faucet_names = [
        'FreeDoge',
        'FreeUSDCoin',
        'FreeBinanceCoin',
        'FreeDash',
        'FreeChainLink',
        'FreeLiteCoin',
        'FreeTron',
        'FreeTether',
        'FreeEthereum',
        'FreeSteam'
        ]
    
    return faucet_names

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

    return driver

#returns 0 if element with text is present, 1 otherwise
def query_text(driver,text):

    #if failed, mark as failed website for user so it can be skipped when the user tries it later
    time.sleep(2)
    try:
        text_path = "//*[contains(text(),'"+text+"')]"
        driver.find_element_by_xpath(text_path)
        return True
    except:
        return False

#Evades the inevitable 10minuteemail.net popup by shifting window frame size
def evade_email_popup(driver):

    time.sleep(2)
    driver.set_window_size(100, 400)
    time.sleep(2)
    driver.set_window_size(1400, 600)

    return driver
    
#Creates new email address
#Returns open driver for the email account, username, and password
def initialize_email():
    
    driver = init_webdriver(False)
    driver.get(inbox_url)
    driver.implicitly_wait(10)
    driver = evade_email_popup(driver)

    email_address_xpath = "/html/body/div[1]/div[3]/div[5]/div[1]/input"
    email_addr = driver.find_element_by_xpath(email_address_xpath)

    n_pword = 20
    username = email_addr.get_attribute('value')
    password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=n_pword))

    return driver, username, password

#Deletes ads that may be blocking registration form on faucet websites
def delete_faucet_ads(driver):

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
                    deleted_ad = True
                    break
            except:
                pass

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
                pass

    return driver

#Go to faucet for given user and register
def visit_faucet(driver, faucet_url, username, password):
    
    checkpoint = time.time() #CHECKPOINT
    #Open and Initialize Faucet Website
    if driver == None: #Reuse driver for same user
        driver = init_webdriver(False)
    driver.get(faucet_url)
    print("     faucet loading time:",time.time()-checkpoint) #CHECKPOINT

    driver = delete_faucet_ads(driver)

    #Register on faucet website

    #Select Register option
    reg_opt_xpath = "//*[@id='navbarSupportedContent']/ul/li[4]/a"
    reg_opt = driver.find_element_by_xpath(reg_opt_xpath)
    reg_opt.click()

    #Email Address Input
    user_xpath = '/html/body/main/section/section[1]/div/div/div[2]/div/div[2]/div[1]/input'
    user_input = driver.find_element_by_xpath(user_xpath)
    user_input.send_keys(username)

    #Password inputs
    pword_xpath = '/html/body/main/section/section[1]/div/div/div[2]/div/div[2]/div[2]/input'
    pword_input = driver.find_element_by_xpath(pword_xpath)
    pword_input.send_keys(password)

    pword_xpath = '/html/body/main/section/section[1]/div/div/div[2]/div/div[2]/div[3]/input'
    pword_input = driver.find_element_by_xpath(pword_xpath)
    pword_input.send_keys(password)

    reg_button_xpath = '/html/body/main/section/section[1]/div/div/div[2]/div/div[2]/button'
    reg_button = driver.find_element_by_xpath(reg_button_xpath)
    reg_button.click()

    return driver

#Switch back to email primary driver and return confirmation link from email
def confirm_email(driver, faucet_name):

    driver.get(inbox_url)
    driver.implicitly_wait(10)

    #Wait for message from faucet, then copy link
    while True:
        driver = evade_email_popup(driver)
        sender_xpath = '/html/body/div[1]/div[4]/div/table/tbody/tr[2]/td[1]/a'
        sender = driver.find_element_by_xpath(sender_xpath)
        if faucet_name in sender.text:
            message_xpath = '/html/body/div[1]/div[4]/div/table/tbody/tr[2]'
            message = driver.find_element_by_xpath(message_xpath)
            message.click()
            driver = evade_email_popup(driver)
            conf_link = driver.find_element_by_link_text('Email Confirmation').text

            driver.refresh() #back to main inbox screen
            break
        else:
            time.sleep(2)

    return driver, conf_link

def main():

    short_ref_links = get_ref_links()
    faucet_names = get_faucet_names()
    faucet_accounts = {}

    start_time = time.time()
    one_hr = 60*60
    
    #Make and register new users 
    while time.time()-start_time < one_hr: #Perpetual loop to register referral accounts for jackrset1

        checkpoint = time.time() #CHECKPOINT
        driver = None #Fresh User
        connect_protonvpn('-f')
        print("VPN Connected:",time.time()-checkpoint) #CHECKPOINT
        
        checkpoint = time.time() #CHECKPOINT
        primary_driver, username, password = initialize_email()
        faucet_accounts[username] = password
        faucet_registeries = [] #Indexed to faucet list, 0=no account, 1=made account
        print("Email Created:",time.time()-checkpoint) #CHECKPOINT

        #Loop through every faucet and register this new user
        for i_ref_link in range(len(short_ref_links)):
            
            checkpoint = time.time() #CHECKPOINT
            #Open, Initialize, and Register on Faucet Website
            driver = visit_faucet(driver, short_ref_links[i_ref_link], username, password)
            print("Faucet Registered:",time.time()-checkpoint) #CHECKPOINT
            
            checkpoint = time.time() #CHECKPOINT
            #Check if account is already registered, escape the rest of the mailing process
            try:
                if query_text(driver,'You cannot create more than one account'):
                    faucet_registeries.append(0)
                    continue 
            except:
                faucet_registeries.append(0)
                continue

            faucet_registeries.append(1)
            print("Prior Acct at ip check:",time.time()-checkpoint) #CHECKPOINT

            checkpoint = time.time() #CHECKPOINT
            #Confirm registration on 10minutemail.net
            primary_driver, conf_link = confirm_email(primary_driver,faucet_names[i_ref_link])
            print("Conf Link Retreived:",time.time()-checkpoint) #CHECKPOINT
            
            faucet_accounts[username] = password #Store account information

            #Open confirmation link in driver that was on faucet page
            driver.get(conf_link)
            time.sleep(5) #Wait for confirmation to register

        #User iterated all faucet registeries
        primary_driver.quit()
        driver.quit()
        disconnect_protonvpn() #This person is finished

        #copy and paste user info from terminal into dictionary of main script
        print("'"+username+"': '"+password+"',")
        print(faucet_registeries)
        
    print(faucet_accounts) #formatted output
    

if __name__ == "__main__":
	main()
