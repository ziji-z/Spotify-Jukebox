'''
import webbrowser, os, sys

url = 'https://open.spotify.com/'

chrome_path = '/usr/lib/chromium-browser/chromium-browser'
webbrowser.get(chrome_path).open(url)
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import time
from signal import pause


def go():
    '''
    f = open(r'/home/piplayer/scripts/lcd_output.txt', 'r')    # pass an appropriate path of the required file
    lines = f.readlines()
    #print(lines)
    f.close()   # close the file and reopen in write mode to enable writing to file; you can also open in append mode and use "seek", but you will have some unwanted old data if the new data is shorter in length.
        
    f = open(r'/home/piplayer/scripts/lcd_output.txt', 'w')
    lines[1] = "booting... \n"
    #print(lines[0]+lines[1])
    lines[3] = 25
    f.write(lines[0]+lines[1]+lines[2]+lines[3])
    # do the remaining operations on the file
    f.close()
    '''
    time.sleep(10)
    
    # Set the path to the Chromium browser
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium-browser"

    # Specify the path to the Chromium user data directory
    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=/home/piplayer/.config/chromium") #e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
    options.add_argument("--autoplay-policy=no-user-gesture-required") #apparently this allows for autplay wihtout gesture
    options.add_experimental_option("detach", True)
    options.add_argument(r'--profile-directory=Profile2') #e.g. Profile 3

    #logger.debug('chrome options initilized')
    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(options=options)
    #logger.debug('chrome webdriver activated too')
    # Go to the specified URL
    driver.get("https://open.spotify.com/")

    # Wait for the page to load
    time.sleep(10)

    # Find the element you want to click on
    # You may need to update the selector to match the element you want to click
    #element = driver.find_element(By.XPATH, "/html/body/div[4]/div/div[2]/div[3]/footer/div/div[2]/div/div[1]/button")
    
    element = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Play"]') #let's see if using the aria label works


    # Create an ActionChain to perform the click
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()

go()