import random
import csv
import pandas as pd
from utils import *
from selenium.webdriver.common.by import By
import time
import config
import os
from fuzzywuzzy import fuzz
import datetime

# Get valid date input from the user
selected_date = get_valid_date_input()
print("You entered a valid date:", selected_date)
main_url = "https://www.facebook.com/marketplace/create/vehicle"
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
account_dir = get_user_email()
if account_dir:
    driver = get_google_driver(path=account_dir)
    time.sleep(5)
    driver.get("https://web.facebook.com/?_rdc=1&_rdr")

    time.sleep(5)
    if not click_login_button(driver):
        time.sleep(3)
        input("")
        driver.get(main_url)
    else:
        input("")
    csv_path = f"Scrapped-data-tampa-{selected_date}.csv"
    df = pd.read_csv(csv_path)
    time.sleep(5)
    driver.get(main_url)
    # Read the completed links CSV file if it exists
    completed_links_path = r'completed_links.csv'
    completed_links = set()
    if os.path.exists(completed_links_path):
        with open(completed_links_path, 'r') as file:
            reader = csv.reader(file)
            for line in reader:
                completed_links.add(line[0])

    for index, row in df.iterrows():
        if row['Url'] in completed_links:
            print(f"Skipping row {index + 1}, link already completed: {row['Url']}")
            continue
        try:
            year = row['Year']
            model = row['Model'].strip()
            ext_color = row['Ext. Color'].replace('Ext. Color:', '').replace('Color:', '').strip()
            btn_click_with_action_chains(driver,
                                         "//span[text()='Vehicle type']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']")
            btn_click(driver, "//span[text()='Car/Truck'] | //span[text()='Car/Van'] | //span[text()='Car/van']")
            btn_click_with_action_chains(driver,
                                         "//span[text()='Year']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']")

            btn_click(driver, f"//span[text()='{year}']")
            make = row['Make'].strip()
            select_make_value(driver, make)

            select_model_of_a_vehicle(driver, model)
            mileage = row['Mileage'].strip()
            insert_value(driver, "//span[text()='Mileage']/following-sibling::input", mileage)
            price = row['Price']
            insert_value(driver, "//span[text()='Price']/following-sibling::input", price)
            btn_click_with_action_chains(driver,
                                         "//span[text()='Body style']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']")
            body_style = row['Body Style'].strip()
            try:
                btn_click(driver, f"//span[text()='{body_style}']", timeout=2)
            except:
                body_style = body_style_dict.get(body_style)
                try:
                    btn_click(driver, f"//span[text()='{body_style}']", timeout=2)
                except:
                    body_style = 'Other'
                    btn_click(driver, f"//span[text()='{body_style}']", timeout=2)

            btn_click_with_action_chains(driver,
                                         "//span[text()='Exterior color']/../following-sibling::div/div[@class='xamitd3 x1pi30zi'] | //span[text()='Exterior colour']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']")
            try:
                print("Exterior Colour: ", ext_color)
                btn_click(driver, f"//span[text()='{ext_color}']", timeout=5)
            except:
                ext_color = color_change.get(ext_color)
                btn_click(driver, f"//span[text()='{ext_color}']", timeout=5)
            btn_click_with_action_chains(driver,
                                         "//span[text()='Interior color']/../following-sibling::div/div[@class='xamitd3 x1pi30zi'] | //span[text()='Interior colour']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']")
            # Select interior Color
            int_color = row['Int. Color'].strip()
            select_interior_colour(driver, int_color)
            btn_click_with_action_chains(driver,
                                         "//span[text()='Vehicle condition']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']")
            condition = 'Excellent'
            btn_click(driver, f"//span[text()='{condition}']")
            btn_click_with_action_chains(driver,
                                         "//span[text()='Fuel type']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']")
            fuel_type = row['Fuel'].strip()
            try:
                btn_click(driver, f"//span[text()='{fuel_type}']", timeout=5)
            except:
                fuel_type = fuel_type_change.get(fuel_type)
                btn_click(driver, f"//span[text()='{fuel_type}']", timeout=5)
            btn_click_with_action_chains(driver,
                                         "//span[text()='Transmission']/../following-sibling::div/div[@class='xamitd3 x1pi30zi']")
            transmission = row['Trans']
            btn_click(driver, f"//span[text()='{transmission}']")
            description = row['Description'].strip()
            insert_value(driver, "//span[text()='Description']/following-sibling::textarea", description)
            # ... Continue with other fields in a similar manner
            ########
            # name year model trim ext_color
            folder_name = f'{row["Name"]} {ext_color}'.strip()
            print('Vehicle folder name: ', folder_name)
            all_images_folder_names = os.listdir(rf"{BASE_DIR}\Inventory-{selected_date}")
            for one_folder_name in all_images_folder_names:
                print("name match with this percentage: ", fuzz.ratio(folder_name, one_folder_name))
                if fuzz.ratio(folder_name, one_folder_name) > 97:
                    folder_name = one_folder_name
                    print("found  this folder name: ", folder_name)
                    break
            image_folder = rf'{BASE_DIR}\Inventory-{selected_date}\{folder_name}'
            print('Vehicle folder path:', image_folder)
            image_files = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if
                           file.endswith('.jpg')]
            image_upload_count = 0
            for image in image_files:
                file_input = driver.find_element(By.XPATH,
                                                 "//span[text()='Add Photos']/ancestor::div/preceding-sibling::label[2]/input | //span[text()='Add photo']/ancestor::div/preceding-sibling::label[2]/input")
                try:
                    driver.execute_script("arguments[0].value = '';", file_input)
                except:
                    pass
                file_input.send_keys(image)
                image_upload_count += 1
                if image_upload_count >= 20:
                    break
                time.sleep(2)
                image = None
            #########
            driver.find_element(By.XPATH, "//div[@aria-label='Next']").click()
            time.sleep(random.randint(7, 10))
            publish_button = driver.find_element(By.XPATH, "//div[@aria-label='Publish']")
            publish_button.click()
            time.sleep(random.randint(20, 25))
            publish_button = driver.find_elements(By.XPATH, "//div[@aria-label='Publish']")
            while publish_button:
                time.sleep(3)
                publish_button = driver.find_elements(By.XPATH, "//div[@aria-label='Publish']")
            # Add the link after succesful posting
            completed_links.add(row['Url'])
            with open(completed_links_path, 'a+', newline='') as failedFile:
                writer = csv.writer(failedFile)
                writer.writerow([row['Url']])

            driver.get(main_url)
            time.sleep(random.randint(5, 7))
        except Exception as e:
            print(e)
            traceback.print_exc()
            with open('failed_urls.csv', 'a+', newline='') as failedFile:
                writer = csv.writer(failedFile)
                writer.writerow([row['Url']])
            driver.get(main_url)
    print("All posting Done")
    driver.quit()

