#!/usr/bin/env python

import requests
import json
import configparser
import os
import sys



config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()

if not os.path.exists('settings.ini'):
    print('Не найден конфигурационный файл')
    sys.exit()

config.read('settings.ini')

##### Получение телефонного номера

URL = config.get('urls', 'URL')
request_res = requests.get(URL) #выполняем запрос

if request_res.status_code == 200:
    data = request_res.json()
    #print(data)
    if data['IsSuccess'] == True:
        number = data['Data']['Msisdn']
        uniq_id = data['Data']['Id']
        print('Получен следующий простой номер телефона {0}'.format(number))
    else:
        print('Не удалось получить номер!')
        print('Ошибка {0}'.format(data['ErrorReason']))
        print('Текст ошибки: {0}'.format(data['ErrorMessage']))
else:
    print('Получен код возврата {0} '.format(request_res.status_code))
    print('Ошибка выполнения запроса!')


##### Резервирование номера

# получения номера телефона в регионе Москва

URL_RES = config.get('urls', 'URL_RES')
list_number = []
list_number.append(number)
data = list_number
data_json = json.dumps(data) # формируем входные данные для запроса.
headers = {'Content-type': 'application/json'}
response = requests.post(URL_RES, data=data_json, headers=headers) #выполняем запрос

if response.status_code == 200: # проверяем статус возрата сообщения
    result = response.json()
    if result['IsSuccess'] == True and result['Data']['IsCompleteReserve'] == True:
        print('Телефонный номер {0}, успешно зарезервирован'.format(number))
        token = result['Data']['ReservationToken']
    else:
        print('Не удалось зарезервировать номер!')
        print('Ошибка {0}'.format(result['ErrorReason']))
        print('Текст ошибки: {0}'.format(result['ErrorMessage']))
else:
    print('Получен код возврата {0}'.format(response.status_code))
    print('Ошибка выполнения запроса!')


##### оформляем заказ

##### изначально получаем город в регионе

URL_CITY = config.get('urls', 'URL_CITY')
request_city = requests.get(URL_CITY) #выполняем запрос

if request_city.status_code == 200:
    data_city = request_city.json()
    #print(data_city)
    if data_city['IsSuccess'] == True:
        city_id = data_city['Data'][1]['Id']
        print('Получен следующий уникальный идентификатор города {0}'.format(city_id))
    else:
        print('Не удалось получить город!')
        print('Ошибка {0}'.format(data_city['ErrorReason']))
        print('Текст ошибки: {0}'.format(data_city['ErrorMessage']))
else:
    print('Получен код возврата {0} '.format(request_city.status_code))
    print('Ошибка выполнения запроса!')

##### Получаем список точек продаж в городе

URL_SAL = config.get('urls', 'URL_SAL')
URL_SAL = '{0}{1}'.format(URL_SAL, city_id)
#print(URL_SAL)
request_sale = requests.get(URL_SAL) #выполняем запрос

if request_sale.status_code == 200:
    data_sale = request_sale.json()
    #print(data_sale)
    if data_sale['IsSuccess'] == True:
        sale_id = data_sale['Data'][0]['Id']
        print('Получен следующий уникальный идентификатор точки продаж {0}'.format(sale_id))
    else:
        print('Не удалось получить уникальный идентификатор точки продаж!')
        print('Ошибка {0}'.format(data_sale['ErrorReason']))
        print('Текст ошибки: {0}'.format(data_sale['ErrorMessage']))
else:
    print('Получен код возврата {0} '.format(request_sale.status_code))
    print('Ошибка выполнения запроса!')

##### Получаем тариф в регионе

URL_TAR = config.get('urls', 'URL_TAR')
request_tar = requests.get(URL_TAR) #выполняем запрос

if request_tar.status_code == 200:
    data_tar = request_tar.json()
    #print(data_tar)
    if data_tar['IsSuccess'] == True:
        tarif_id = data_tar['Data'][0]['Id']
        print('Получен следующий уникальный идентификатор тарифа {0}'.format(tarif_id))
    else:
        print('Не удалось получить уникальный идентификатор тарифа!')
        print('Ошибка {0}'.format(data_tar['ErrorReason']))
        print('Текст ошибки: {0}'.format(data_tar['ErrorMessage']))
else:
    print('Получен код возврата {0} '.format(request_tar.status_code))
    print('Ошибка выполнения запроса!')


#####
URL_ORDER = config.get('urls', 'URL_ORDER')
URL_ORDER = '{0}{1}'.format(URL_ORDER, token)
#print(URL_ORDER)
# Входные данные
with open('data.json', 'r', encoding='utf-8') as data_in:
    input_data = json.load(data_in)

for key in input_data:
    if key == 'SalesPointId':
        input_data[key] = sale_id
    elif key == 'CityId':
        input_data[key] = city_id
    elif key == 'Products':
        input_data[key][0]['Msisdn'] = number
        input_data[key][0]['TariffId'] = tarif_id
#print(input_data)

data2_json = json.dumps(input_data)
#print(data2_json)
response_order = requests.post(URL_ORDER, data=data2_json, headers=headers)
if response_order.status_code == 200:
    result_order = response_order.json()
    #print(result_order)
    if result_order['IsSuccess'] == True:
        print('Получен номер заказа {0}'.format(result_order['Data']['OrderNumber']))
    else:
        print('Не удалось обработать заказ!')
        print('Ошибка {}'.format(result_order['ErrorReason']))
        print('Текст ошибки: {0}'.format(result_order['ErrorMessage']))
else:
    print('Получен код возврата {0}'.format(result_order.status_code))
    print('Ошибка выполнения запроса!')
