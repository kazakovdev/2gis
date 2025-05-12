import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from tqdm import tqdm
import glob


def main():
    option = Options()
    option.add_argument("--disable-infobars")

    df = pd.read_excel('cities_old.xlsx')

    for city_name in tqdm(df['city_name'].unique()[::-1]):

        print(f'Start city: {city_name}')
        files = glob.glob(f'out/{city_name}*.xlsx')
        if files:
            print(f'City: {city_name} already exists')
            continue
        # Или в поддиректории:
        # files = glob.glob('папка/*.txt')

        # Initialise chrome driver
        browser = webdriver.Chrome()
        browser.get('https://2gis.ru/')
        while True:
            try:
                elem = browser.find_element(By.CLASS_NAME, '_cu5ae4')
                break
            except:
                print(f'NO FIND ELEMENT(SHIT)')
                browser.close()
                browser = webdriver.Chrome()
                browser.get('https://2gis.ru/')
                sleep(10)

        actions = ActionChains(browser)
        elem.send_keys(f'г. {city_name} ТЦ' + Keys.RETURN)
        addr = []

        # Here we go
        #cross_btn = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME, '_awwm2v')))
        #cross_btn.click()
        try:
            next_btn = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME, '_n5hmn94')))
            actions.move_to_element(next_btn).perform()
        except:
            items = browser.find_elements(By.CLASS_NAME, '_klarpw')  # adress
            #addr += [x.get_attribute("textContent").replace(u'\xa0', ' ') for x in items]
            addr += [x.text for x in items]
            #raw_string = items[1].text.split('\n')
            # Export in new df
            df_out = pd.DataFrame(addr, columns=['addr'])
            df_out['city'] = city_name
            df_out.to_excel(f'out/{city_name}_out.xlsx')
            continue

        items = browser.find_elements(By.CLASS_NAME, '_klarpw')  # adress
        addr += [x.text for x in items]
        #addr += [x.get_attribute("textContent").replace(u'\xa0', ' ') for x in items]


        next_btn.click()

        while True:  # while next button exists
            sleep(1)
            print(len(items), 'is grabbed')
            try:
                next_btn = \
                WebDriverWait(browser, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_n5hmn94')))[1]
            except:
                break

            actions.move_to_element(next_btn).perform()
            try:
                items = browser.find_elements(By.CLASS_NAME, '_klarpw')  # adress
                addr += [x.text for x in items]
                #addr += [x.get_attribute("textContent").replace('\n', ';').replace(u'\xa0', ' ') for x in items]
            except:
                items = browser.find_elements(By.CLASS_NAME, '_klarpw')  # adress
                addr += [x.text for x in items]
                #addr += [x.get_attribute("textContent").replace(u'\xa0', ' ') for x in items]
            next_btn.click()

        df_out = pd.DataFrame(addr, columns=['addr'])
        df_out['city'] = city_name
        df_out.to_excel(f'out/{city_name}_out.xlsx')

        print(len(set(addr)))
        browser.close()
        sleep(5)


def load_json():
    import glob, os, pathlib
    os.chdir(pathlib.Path.cwd())
    df = []
    for file in glob.glob(f"out/*_out.xlsx"):
        print(file)
        try:
            df.append(pd.read_excel(file))
        except:
            continue

    df = pd.concat(df, ignore_index=True)
    df.to_excel('out/out_all.xlsx')


if __name__ == '__main__':
    load_json()
