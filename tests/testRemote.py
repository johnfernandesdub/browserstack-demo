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
USERNAME = BSTACK_USERNAME
ACCESS_KEY = config['accessKey']
INVITE_URL = config['invite_url']
BROWSER_STACK_URL = config['brower_stack_url']
URL = f"https://{USERNAME}:{ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"

options = ChromeOptions()
options.accept_insecure_certs=True
#options.set_capability('sessionName', 'BStack Testo')

try:
    logger.info("Logging into BrowserStack Web Site...")
    driver = webdriver.Remote(
        command_executor=URL,
        options=options)

    driver.get(BROWSER_STACK_URL)
    driver.maximize_window()    
    
    logger.info("Navigate to the Sign In Page...")
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.XPATH,"//*[contains(text(),'Sign in')]"))
    ).click()
     
    #Find the username, password and click elements
    logger.info("Enter the Credentials...")
    login=driver.find_element(By.ID, "user_email_login");
    password=driver.find_element(By.ID, "user_password");
        
    login.send_keys(BSTACK_USERNAME)
    password.send_keys(BSTACK_PASSWORD)
    driver.execute_script("document.querySelector('#user_submit').click();")
    
    logger.info("Locate the Invite Team Link...")
    invite=WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "invite-link"))
    )
    
    logger.info("Perform Assertion as per the brief...")
    assert invite is not None, f"The Invite Team link was not found on BrowserStack web site"
    
    inviteUrl=invite.get_property("href")
    
    assert len(inviteUrl) != 0, f"The Invite Team link was not found"
    assert INVITE_URL.lower() == inviteUrl.lower(), f"The Teams URL obtained from BrowserStack web site matches the internal one"
    
    logger.info("The URL extracted matched...")
    
    #Log out of BrowserStack
    logger.info("Sign out of BrowserStack web site...")
    driver.execute_script("document.querySelector('#account-menu-toggle').click();")
    signout=WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "sign_out_link"))
    )
    signout.click()
    
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