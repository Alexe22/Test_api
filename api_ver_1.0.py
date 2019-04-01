#!/usr/bin/env python

import requests
import json
import configparser
import os



config = configparser.ConfigParser()
config._interpolation = configparser.ExtendedInterpolation()

if not os.path.exists('settings.ini'):
    print('Не найден конфигурационный файл')

config.read('settings.ini')
URL = config.get('urls', 'URL')

# получения номера телефона в регионе Москва

URL_RES = config.get('urls', 'URL_RES')

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


##### оформить заказ
URL_ORDER = config.get('urls', 'URL_ORDER')
URL_ORDER = URL_ORDER + token
# Входные данные
with open('data.json', 'r', encoding='utf-8') as data:
    input_data = json.load(data)
print(input_data)
data2_json = json.dumps(input_data)
#print(data2_json)
response_order = requests.post(URL_ORDER, data=data2_json, headers=headers)
if response_order.status_code == 200:
    result_order = response_order.json()
    #print(result_order)
    if result_order['IsSuccess'] == True:
        print('Получен заказ {0}'.format(result_order['Data']['ReservationResult']['ReservationToken']))
    else:
        print('Не удалось обработать заказ!')
        print('Ошибка {}'.format(result_order['ErrorReason']))
        print('Текст ошибки: {0}'.format(result_order['ErrorMessage']))
else:
    print('Получен код возврата {0}'.format(result_order.status_code))
    print('Ошибка выполнения запроса!')
