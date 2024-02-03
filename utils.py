import traceback

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import sys
import time
import re
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def get_firefox_browser_with_profile(profile_name='firefox_dir', headless=False):
    options = Options()
    custom_profile = os.path.join(os.path.dirname(sys.executable), profile_name)
    if headless:
        options.headless = True
    print(custom_profile)
    # options.set_preference('profile', custom_profile)
    driver = webdriver.Firefox(firefox_profile=custom_profile,options=options)
    driver.maximize_window()
    driver.get("https://www.facebook.com/marketplace/create/vehicle")
    driver.implicitly_wait(10)
    return driver


def get_google_driver(headless=False, path='chrome-dir'):
    try:
        options = webdriver.ChromeOptions()
        # options.add_argument('--incognito')
        BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        complete_path = rf"{BASE_DIR}/{path}"
        print(complete_path)
        options.add_argument(f"--user-data-dir={complete_path}")
        options.add_argument("--log-level=3")
        options.add_argument('--no-sandbox')
        if headless:
            options.add_argument('--headless')
        options.add_argument('--start-maximized')
        chrome_exe_path = ChromeDriverManager().install()
        driver = webdriver.Chrome(service=Service(executable_path=chrome_exe_path), options=options)
        time.sleep(2)
        driver.implicitly_wait(10)
        return driver
    except Exception as e:
        print(e)
        print('------------------- Generation the New Driver')
        get_google_driver(headless, path=path)

def login_facebook_account(driver, email='', password=''):
    driver.find_element(By.XPATH, "//input[@aria-label='Email or phone'] | //input[@id='email']").send_keys(email)
    driver.find_element(By.XPATH, "//input[@aria-label='Password'] | //input[@id='pass']").send_keys(password)

    try:
        login_button = driver.find_elements(By.XPATH, "//span[text()='Log In'] | //button[@id='loginbutton']")
        if login_button:
            login_button[0].click()
    except:
        driver.find_elements(By.XPATH, "//span[text()='Log in']")[0].click()
    time.sleep(5)

def btn_click(driver, xpath, timeout=20):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))

    element.click()

def btn_click_with_action_chains(driver, xpath, wait_time=20):
    element = WebDriverWait(driver, wait_time).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))

    action = ActionChains(driver)
    action.move_to_element(element).perform()
    action.click(element).perform()



def execute_script_based_click(driver, xpath, timeout=60):
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].click();", el)
    except Exception as e:
        print(e)
        traceback.print_exc()

def send_keys_with_action_chains(driver, xpath, text, wait_time=20, previouse_clear=False):
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))

        action = ActionChains(driver)
        action.move_to_element(element).perform()
        if previouse_clear:
            element.clear()

        action.click().send_keys(text).perform()
    except Exception as e:
        print(e)
        traceback.print_exc()

def insert_value(driver, xpath, text, wait_time=20,previouse_clear=False):
    element = WebDriverWait(driver, wait_time).until(
        EC.visibility_of_element_located((By.XPATH, xpath)))
    if previouse_clear:
        element.clear()

    element.send_keys(text)



def select_make_value(driver, make):
    try:
        btn_click_with_action_chains(driver, "//span[text()='Make']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']")
        btn_click(driver, f"//span[text()='{make}']")
    except:
        insert_value(driver, f"//span[text()='Make']/following-sibling::input", make)


def click_login_button(driver):
    try:
        btn_click_with_action_chains(driver, "(//span[text()='Log In'])[2] | //button[@id='loginbutton'] | //button[text()='Log In']", wait_time=5)
        time.sleep(3)
        return True
    except:
        try:
            login_buttons = driver.find_elements(By.XPATH, "//span[text()='Log In'] | //button[@id='loginbutton'] | //span[text()='Log in'] | //button[text()='Log In']")
            for login in login_buttons:
                driver.execute_script("arguments[0].click();", login)
                time.sleep(1)
            time.sleep(3)
            return True
        except:
            print("Login button not found")
            time.sleep(3)
            return False


body_style_dict = {'Sedan': 'Saloon'}
color_change = {'Tann': 'Tan', 'Gray': 'Grey'}
fuel_type_change = {'Gasoline': 'Petrol'}


def select_interior_colour(driver, int_color):
    try:
        print("Interior Colour: ",int_color)
        btn_click(driver, f"//span[text()='{int_color}']", timeout=2)
    except:
        try:
            print("Trying on 2nd index, interior colour: ", int_color)
            btn_click(driver, f"(//span[text()='{int_color}'])[2]", timeout=2)
        except:
            int_color  = color_change.get(int_color)
            btn_click(driver, f"//span[text()='{int_color}']", timeout=2)



def select_model_of_a_vehicle(driver, model_number):
    try:
        btn_click_with_action_chains(driver, "//span[text()='Model']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']", wait_time=5)
        btn_click(driver, f"//span[text()='{model_number}']", timeout=2)
    except:
        try:
            btn_click_with_action_chains(driver, "//span[text()='Model']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']", wait_time=5)
            btn_click(driver, f"//span[text()='{model_number.replace('-', ' ')}']", timeout=2)
        except:
            insert_value(driver, "//span[text()='Model']/following-sibling::input", model_number)


def get_valid_date_input():
    while True:
        user_input = input("Enter a date in the format dd-mm-yyyy: ")
        date_pattern = re.compile(r'^\d{2}-\d{2}-\d{4}$')

        if date_pattern.match(user_input):
            return user_input
        else:
            print("Invalid date format. Please enter the date in the format dd-mm-yyyy.")



def get_user_email():
    user_email = input("Please enter the email account you want to use: ")
    email = user_email.split('@')[0]
    if not os.path.exists(rf"{BASE_DIR}/{email}"):
        print("Account directory not exists, please use chrome_cd.py file to create directory.")
        return False
    return email