import json
import math
import time

import pandas as pd
import requests

API_KEY = ''
QUESTION_STRING = 'АЗС'


class city_shape:
    def __init__(self, name, point1=(), point2=()):
        self.MIN_X = 0.09
        self.MIN_Y = 0.07

        self.name = name
        self.point1 = point1[::-1]
        self.point2 = point2[::-1]
        self.x_length = math.sqrt((self.point1[0] - self.point2[0]) ** 2)
        self.y_length = math.sqrt((self.point1[1] - self.point2[1]) ** 2)

    def get_shapes(self):
        MIN_X = self.MIN_X
        MIN_Y = self.MIN_Y

        shapes = [[(), ()]]
        for j in range(math.floor(self.y_length / MIN_Y) + 1):
            for i in range(math.floor(self.x_length / MIN_X) + 1):
                point1 = (self.point1[0] + i * MIN_X, self.point1[1] - j * MIN_Y)
                point2 = (self.point1[0] + (i + 1) * MIN_X, self.point1[1] - (j + 1) * MIN_Y)
                shapes.append([point1, point2])

        shapes.pop(0)

        if not shapes:
            shapes.append([self.point1, self.point2])
            return shapes

        return shapes


def load_cities():
    df = pd.read_excel('cities.xlsx', header=0, dtype={'id': float,
                                                       'city_name': str})
    return df


def get_json_by_city_name_page(city_name, page):
    print(f'    request: {city_name} page={page}')
    url = f"https://catalog.api.2gis.com/3.0/items?q={QUESTION_STRING} '{city_name}'&key={API_KEY}&locale=ru_RU&page={page}&fields=items.full_address_name,items.rubrics,items.capacity,items.floors,items.links,items.itin,items.floors,items.is_paid,items.point".replace(
        " ", "%20")
    response = requests.get(url)
    data_json = json.loads(response.text)
    return data_json


def get_json_by_shape_page(shape, page):
    print(f'    request: {shape}: page={page}')
    url = f"https://catalog.api.2gis.com/3.0/items?q=Торговый центр&point1={shape[0][0]},{shape[0][1]}&point2={shape[1][0]},{shape[1][1]}&key={API_KEY}&locale=ru_RU&page={page}&fields=items.full_address_name,items.rubrics,items.capacity,items.floors,items.links,items.itin,items.floors,items.is_paid,items.point".replace(
        " ", "%20")
    response = requests.get(url)
    time.sleep(1)
    data_json = json.loads(response.text)
    return data_json


def parse_total(data_json):
    if data_json['meta']['code'] == 404:
        return 0
    total = data_json['result']['total']
    return total


def load_json_by_city_name_shape(city_name, shapes):
    shape_num = 0
    for shape in shapes:
        shape_num += 1
        print(f'        1 page of shape {shape} of {city_name}')

        data_json = get_json_by_shape_page(shape, page=1)
        save_json(data_json, city_name + '_' + str(shape_num) + '_' + str(1))
        total = parse_total(data_json)

        print(f'    total for shape {shape} of {city_name}: {total}')
        if total < 10:
            print(f'    shape is DONE, next shape of {city_name}...')
            continue

        total = 50 if total > 50 else total
        for i in range(2, total // 10 + (1 if total % 10 != 0 else 0) + 1):
            print(f'        {i} page of shape {shape} of {city_name}')
            data_json = get_json_by_shape_page(shape, i)
            save_json(data_json, city_name + '_' + str(shape_num) + '_' + str(i))
        print(f'    shape is DONE, next shape of {city_name}...')
    return None


def load_json_by_city_name(city_name):
    page = 1
    data_json = get_json_by_city_name_page(city_name, page)
    save_json(data_json, city_name + str(page))
    total = parse_total(data_json)
    if total < 10:
        print(f'    city is DONE, next city {city_name}...')
        return None

    total = 50 if total > 50 else total
    print(f'total for {city_name}: {total}')
    for i in range(page + 1, total // 10 + (1 if total % 10 != 0 else 0) + 1):
        data_json = get_json_by_city_name_page(city_name, i)
        save_json(data_json, city_name + '_' + str(i))
        print(f'page {i} for {city_name}')
    print(f'{city_name} DONE')
    return None


def save_json(data, filename):
    with open(filename + '.json', 'w') as f:
        json.dump(data, f)
        return True


def load_files():
    cities_df = load_cities()
    for city_name in cities_df['city_name'].unique():
        # point1 = (cities_df.loc[cities_df['city_name'] == city_name]['point1_1'].values[0],
        #           cities_df.loc[cities_df['city_name'] == city_name]['point1_2'].values[0])
        # point2 = (cities_df.loc[cities_df['city_name'] == city_name]['point2_1'].values[0],
        #           cities_df.loc[cities_df['city_name'] == city_name]['point2_2'].values[0])
        # input_shape = city_shape(city_name, point1=point1, point2=point2).get_shapes()

        print(f'go {city_name}...')
        # load_json_by_city_name_shape(city_name, input_shape)
        load_json_by_city_name(city_name)
        print(f'    data loaded')

    return None


def load_json():
    import glob, os, pathlib
    os.chdir(pathlib.Path.cwd())
    df = []
    city_name = 'Санкт-Петербург'
    for file in glob.glob(f"*.json"):
        print(file)

        f = open(file, encoding='utf-8')
        try:
            data = json.load(f)['result']
        except:
            continue
        df.append(pd.json_normalize(data, 'items', [], record_prefix='items_', errors='ignore'))
        f.close()
    df = pd.concat(df, ignore_index=True)
    df.to_excel('data.xlsx')


def main():
    pass


if __name__ == '__main__':
    # load_files()
    load_json()

property
