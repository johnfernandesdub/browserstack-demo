import json
import logging
from datetime import datetime 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

#Start Timer
start_time = datetime.now() 
logger = logging.getLogger(__name__)

# Load the configuration file
with open('browserstack_config.json') as config_file:
    config = json.load(config_file)

# BrowserStack credentials and URL
BSTACK_USERNAME = config['browserstack_user']
BSTACK_PASSWORD = config['browserstack_password']
USERNAME = config['username']
ACCESS_KEY = config['accessKey']
OLYMPIC_URL = config['olympic_url']
BROWSER_URL = config['irish_times_url']
#URL = f"https://{USERNAME}:{ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"
URL = f"https://{USERNAME}:{ACCESS_KEY}@hub.browserstack.com/wd/hub"

options = ChromeOptions()
options.set_capability('sessionName', 'BStack Testo')
options.set_capability('local', 'True')

try:
    logger.info("Logging into BrowserStack Test Site...")
    logger.info(URL)
    logger.info(BROWSER_URL)
    driver = webdriver.Remote(
        command_executor=URL,
        options=options)

    logger.info("Obtained a driver...")
    driver.get(BROWSER_URL)
    driver.maximize_window()    
    
    logger.info("Navigate to the Web Site and extract link ...")
    elementOlympic=WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH,"//*[@id='main-nav']/div[1]/nav/span[2]/a"))
    )
           
    logger.info("Perform Assertion on the link...")
    assert elementOlympic is not None, f"The Paris Olympic element was on not found on the web site"
    
    olympicUrl=elementOlympic.get_property("href")
    
    assert len(olympicUrl) != 0, f"The Olympic Url link was not found"
    assert OLYMPIC_URL.lower() == olympicUrl.lower(), f"The Paris Olympic from the web site does not match the internal one"
    
    logger.info("The Test is completed...")
    
except NoSuchElementException as err:
    message = 'Exception: ' + str(err.__class__) + str(err.msg)
    driver.execute_script(
        'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": ' + json.dumps(message) + '}}')
except Exception as err:
    message = 'Exception: ' + str(err.__class__) + str(err.msg)
    driver.execute_script(
        'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": ' + json.dumps(message) + '}}')
finally:
    # Stop the driver
    driver.quit()
    
#End time
end_time = datetime.now()
time_difference = (end_time - start_time).total_seconds() 
logger.info("Execution of the test is: " + str(time_difference) + "secs")   