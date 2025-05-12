import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm


def main():
    option = Options()
    option.add_argument("--disable-infobars")

    df = pd.read_excel('ZHK.xlsx', sheet_name='полный список НН')
    df_out = pd.DataFrame({})

    with tqdm(total=df.shape[0]) as pbar:
        for tqdmindex, row in df.iterrows():
            print(f"Start address: {row['Адрес']}")
            print(f"Start coordinates: {row['Широта']} {row['Долгота']}")

            # Initialise chrome driver
            browser = webdriver.Chrome('D:\chromedriver.exe', chrome_options=option)
            browser.get('https://2gis.ru/')
            elem = browser.find_element(By.CLASS_NAME, '_1gvu1zk')

            elem.send_keys(f"{row['Широта']} {row['Долгота']}" + Keys.RETURN)
            names = []

            # Here we go
            time.sleep(3)
            items = browser.find_elements(By.CLASS_NAME, '_tvxwjf')  # adress
            names += [x.get_attribute("textContent").replace(u'\xa0', '') for x in items]

            items = browser.find_elements(By.CLASS_NAME, '_1w9o2igt')
            names += [x.get_attribute("textContent").replace(u'\u200b', '') for x in items]
            try:
                items = browser.find_elements(By.CLASS_NAME, '_15a9jdw')
                names += [x.get_attribute("textContent").replace(u'\u200b', '') for x in items]

                items = browser.find_elements(By.CLASS_NAME, '_oqoid')
                names += [x.get_attribute("textContent").replace(u'\u200b', '') for x in items]
            except:
                continue
            #print(names)
            #df_out.loc[len(df_out)] = [row['Широта'], row['Долгота']] + names
            df_out = df_out.append({'lat': row['Широта'],
                                    'lon': row['Долгота'],
                                    'addr': row['Адрес'],
                                    'type': row['Вид строения (п.9.2.1)'],
                                    'buildingClass': row['buildingClass'],
                                    'name1': names[0] if len(names) >= 1 else '',
                                    'name2': names[1] if len(names) >= 2 else '',
                                    'name3': names[2] if len(names) >= 3 else '',
                                    'name4': names[3] if len(names) >= 4 else ''
                                    },
                                   ignore_index=True)
            #print(df_out)

            pbar.update(1)
            # Export in new df
            #df_out['city'] = city_name
            #df_out.to_excel(f'{city_name}_out.xlsx')
            #continue
    df_out.to_excel('zhk_names_out_new.xlsx')
    # items = browser.find_elements(By.CLASS_NAME, '_tluih8')  # adress
    # addr += [x.get_attribute("textContent").replace(u'\xa0', ' ') for x in items]
    # next_btn.click()

    # while True:  # while next button exists
    #     print(len(items), 'is grabbed')
    #     try:
    #         next_btn = \
    #         WebDriverWait(browser, 3).until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_n5hmn94')))[1]
    #     except:
    #         break
    #
    #     actions.move_to_element(next_btn).perform()
    #     try:
    #         items = browser.find_elements(By.CLASS_NAME, '_tluih8')  # adress
    #         addr += [x.get_attribute("textContent").replace('\n', ';').replace(u'\xa0', ' ') for x in items]
    #     except:
    #         items = browser.find_elements(By.CLASS_NAME, '_tluih8')  # adress
    #         addr += [x.get_attribute("textContent").replace(u'\xa0', ' ') for x in items]
    #     next_btn.click()
    #
    # df_out = pd.DataFrame(addr, columns=['addr'])
    # #df_out['city'] = city_name
    # #df_out.to_excel(f'{city_name}_out.xlsx')
    #
    #     print(len(set(addr)))


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
