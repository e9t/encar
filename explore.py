#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from collections import Counter, defaultdict
from datetime import datetime
from glob import glob
import json
import re

from konlpy.utils import pprint
import numpy as np

from settings import BRAND

DATAFILES = glob('data/%s/*' % BRAND)

def idx(x, i):
    return [y[i] for y in x]

def get_attr(filename, attr):
    attrs = attr.split('.')
    depth = len(attrs)
    with open('%s' % filename, 'r') as f:
        if depth==1:
            return json.load(f).get(attr)
        if depth==2:
            return json.load(f).get(attrs[0]).get(attrs[1])

def parse_birthday(birthday):
    return datetime.strptime(re.sub(u'[년월식]', '', birthday), '%y %m')

def tocsv(l, filename, headers=None):
    with open(filename, 'w') as f:
        if headers:
            s = '%s\n' % ','.join(headers)
            f.write(s.encode('utf-8'))
        for row in l:
            s = '%s\n' % ','.join(map(unicode, row))
            f.write(s.encode('utf-8'))

print u'가격'
prices = [get_attr(g, 'price') for g in DATAFILES]
print np.mean(prices), np.median(prices)

print u'주행거리'
mileage = [int(get_attr(g, 'mileage').strip('km')) for g in DATAFILES]
print np.mean(mileage), np.median(mileage)


print u'색상'
colors = [(get_attr(g, 'color').split('(')[0], get_attr(g, 'price')) for g in DATAFILES]
colorcnt = Counter(idx(colors, 0))
colormap = sorted([(
    color,
    np.mean([i[1] for i in colors if i[0]==color]),
    dict(colorcnt)[color]
    ) for color in set([c[0] for c in colors])], key=lambda x: x[1])
pprint(colorcnt.most_common(5))
pprint(colormap)

print u'연료'
fuel = [get_attr(g, 'fuel') for g in DATAFILES]
pprint(dict(Counter(fuel)))

print u'기어'
t = [get_attr(g, 'transmission') for g in DATAFILES]
pprint(dict(Counter(t)))

print u'연식'
birthday = [parse_birthday(get_attr(g, 'birthday')) for g in DATAFILES]
pprint(Counter(birthday).most_common(10))
pprint(Counter(b.year for b in birthday))
pprint(Counter(b.month for b in birthday).most_common(12))

print u'사고이력'
accidents1 = [int(get_attr(g, 'accidents').get(u'보험사고이력 (내차 피해)', '0').strip(u'회')) for g in DATAFILES]
accidents2 = [int(get_attr(g, 'accidents').get(u'보험사고이력 (타차 가해)', '0').strip(u'회')) for g in DATAFILES]
print accidents1
print np.mean(accidents1)
print accidents2
print np.mean(accidents2)

print u'옵션'
d = defaultdict(int)
for g in DATAFILES:
    for k, v in get_attr(g, 'options').items():
        if v=='yes':
            d[k] += 1
pprint(sorted(list(d.items()), key=lambda x :x[1], reverse=True))

tocsv([[
    get_attr(g, 'encar_id'),
    get_attr(g, 'name')[1],
    get_attr(g, 'price'),
    get_attr(g, 'fuel'),
    get_attr(g, 'color'),
    get_attr(g, 'mileage').strip('km'),
    get_attr(g, 'encar.page_hit'),
    get_attr(g, 'encar.page_favs'),
    get_attr(g, 'encar.registration_date'),
    get_attr(g, u'options.CD 체인저'),
    get_attr(g, u'options.선루프'),
    get_attr(g, u'options.ECS(전자제어 서스펜션)'),
    get_attr(g, u'seller.address').split()[0],
    parse_birthday(get_attr(g, 'birthday')).year
] for g in DATAFILES], 'data/%s.csv' % BRAND,
headers=['id', 'name', 'price', 'fuel', 'color', 'mileage', 'page_hit', 'page_favs', 'registered', 'CD changer', 'sunroof', 'suspension', 'address', 'year'])

