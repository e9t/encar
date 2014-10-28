#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

import datetime
import json
import re

import get
import settings

def x(elem, path):
    return elem.xpath(path)[0].strip()

def xte(elem, path):
    try:
        return elem.xpath(path)[0].strip()
    except IndexError:
        return ''

def get_car_ids(path=None):
    if path:
        with open(path, 'r') as f:
            return f.read().splitlines()
    else:
        f = get.htmltree(settings.LIST_URL[settings.BRAND])
        root = get.webpage(f)
        car_ids = root.xpath('//table[@class="car_list"]//tr/td[@class="inf"]/a[@class="newLink"]/@href')
        return [id.split('=')[1].split('&')[0] for id in car_ids]

def check_new_ids(idlist='idlist.txt'):
    champ_ids = get_car_ids(idlist)
    chall_ids = get_car_ids()
    return list(set(chall_ids) - set(champ_ids))

def get_new_cars():
    def format_car(encar_id):
        info = get_car_info(encar_id)
        obj = {
            'id': encar_id,
            'title': '%s %s (%s, %s): %s' % (info['color'], info['name'][1], info['birthday'], info['mileage'], info['price']),
            'title_type': 'text',
            'content': '',
            'content_type': 'html',
            'url': 'http://encar.com/dc/dc_cardetailview.do?carid=%s' % encar_id,
            'updated': datetime.datetime.today(),
            'author': info['seller'].get('address', ''),
        }
        return obj

    new_ids = check_new_ids()
    return [format_car(i) for i in new_ids]


def get_car_info(encar_id):
    info = dict(encar_id=encar_id)

    url = settings.car_baseurl % encar_id
    f = get.htmltree(url)
    root = get.webpage(f)

    # summary
    summary = root.xpath('//div[@class="section summary hproduct"]')[0]
    info['name'] = [i.strip()\
            for i in summary.xpath('.//h3[@class="car"]/span/text()')]
    info['transmission'] =\
            x(summary, './/div[@class="short"]//li[@class="trs"]/text()')
    info['fuel'] = x(summary, './/div[@class="short"]//li[@class="fue"]/i/text()')
    info['engine'] = x(summary, './/div[@class="short"]//li[@class="eng"]/text()')
    info['type'] = x(summary, './/div[@class="short"]//li[@class="typ"]/text()')
    try:
        info['tags'] = x(summary, './/div[@class="merit"]//span/text()')
    except IndexError:
        info['tags'] = []
    info['price'] = int(x(summary, './/div[@class="prc"]//strong/text()'))

    # detail
    car_detail = root.xpath('//div[@class="field detail"]')[0]
    info['car_id'] = x(car_detail, './/li[@class="cid"]/i/text()')
    info['birthday'] = x(car_detail, './/li[@class="yer"]/i/text()')
    info['mileage'] = x(car_detail, './/li[@class="dts"]/i/text()')
    info['color'] = x(car_detail, './/li[@class="clr"]/i/text()')

    # options
    car_options = root.xpath('//table[@class="option_table"]//span[@class="check"]')
    info['options'] = {x(option, './/a/text()'): x(option, './/sup/@class')\
                                                 for option in car_options}

    # seller
    seller = root.xpath('//div[@class="field seller"]//dd[not(contains(@class, "image") or contains(@class, "email"))]')
    info['seller'] = {x(s, './@class'): xte(s, './p/span/text()|./p/strong/text()|./p/strong/a/text()') for s in seller[:5]}

    # accidents
    accident_list = root.xpath('//ul[@class="acclist"]/li')
    info['accidents'] = {x(a, './b/text()'): x(a, './/strong/text()')
                                             for a in accident_list}

    # etc
    encar = {}
    encar['registration_date'] = x(root, '//div[@class="field etc"]//span[@class="date"]/text()').strip(' :').replace('/', '-')
    encar['page_hit'] = int(x(root, '//div[@class="field etc"]//span[@class="hit"]/text()').strip(': '))
    encar['page_favs'] = int(x(root, '//div[@class="field etc"]//span[@class="hot"]//i/text()'))
    info['encar'] = encar

    return info

if __name__=='__main__':

    ids = get_car_ids()
    cnt = len(ids)
    for i, encar_id in enumerate(ids):
        print '%s (%d/%d)' % (encar_id, i, cnt)
        with open('data/%s/%s.json' % (settings.BRAND, encar_id), 'w') as f:
            info = get_car_info(encar_id)
            json.dump(info, f)
