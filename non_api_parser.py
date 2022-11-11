from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd

def main():
    option = Options()
    option.add_argument("--disable-infobars")


    df = pd.read_excel('cities_old.xlsx')

    for city_name in df['city_name'].unique():
        print(f'Start city: {city_name}')

        #Initialise chrome driver
        browser = webdriver.Chrome('D:\chromedriver.exe', chrome_options=option)
        browser.get('https://2gis.ru/')
        elem = browser.find_element(By.CLASS_NAME, '_1gvu1zk')
        actions = ActionChains(browser)
        elem.send_keys(f'г. {city_name} ТЦ' + Keys.RETURN)
        addr = []

        # Here we go
        cross_btn = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME,  '_euwdl0')))
        cross_btn.click()
        try:
            next_btn = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME,  '_n5hmn94')))
            actions.move_to_element(next_btn).perform()
        except:
            items = browser.find_elements(By.CLASS_NAME, '_tluih8')  # adress
            addr += [x.get_attribute("textContent").replace(u'\xa0', ' ') for x in items]

            # Export in new df
            df_out = pd.DataFrame(addr, columns=['addr'])
            df_out['city'] = city_name
            df_out.to_excel(f'{city_name}_out.xlsx')
            continue

        items = browser.find_elements(By.CLASS_NAME,  '_tluih8' ) #adress
        addr += [x.get_attribute("textContent").replace(u'\xa0',' ') for x in items]
        next_btn.click()

        while True: # while next button exists
            print(len(items), 'is grabbed')
            try:
                next_btn = WebDriverWait(browser, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME,  '_n5hmn94')))[1]
            except:
                break

            actions.move_to_element(next_btn).perform()
            try:
                items = browser.find_elements(By.CLASS_NAME, '_tluih8')  # adress
                addr += [x.get_attribute("textContent").replace('\n',';').replace(u'\xa0', ' ') for x in items]
            except:
                items = browser.find_elements(By.CLASS_NAME, '_tluih8')  # adress
                addr += [x.get_attribute("textContent").replace(u'\xa0', ' ') for x in items]
            next_btn.click()

        df_out = pd.DataFrame(addr, columns=['addr'])
        df_out['city'] = city_name
        df_out.to_excel(f'{city_name}_out.xlsx')

        print(len(set(addr)))

def load_json():
    import glob, os, pathlib
    os.chdir(pathlib.Path.cwd())
    df = []
    for file in glob.glob(f"*_out.xlsx"):
        print(file)
        try:
            df.append(pd.read_excel(file))
        except:
            continue

    df = pd.concat(df, ignore_index=True)
    df.to_excel('out_all.xlsx')

if __name__ == '__main__':
    main()
