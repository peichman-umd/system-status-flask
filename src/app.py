import json
import os
import re
from collections import Counter

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask
from slimit.lexer import Lexer

load_dotenv('../.env')
STATUS_URL = os.environ.get('STATUS_URL')

if STATUS_URL is None:
    raise RuntimeError('Must set STATUS_URL')


def get_widget_html(text):
    lexer.input(text)
    for token in lexer:
        if token.type == 'ID' and token.value == 'widgethtml':
            # next two tokens should be a COLON and a STRING
            _colon = lexer.token()
            string = lexer.token()
            if string.value.startswith('"<'):
                return json.loads(string.value)


def get_status_map(widget_html):
    soup = BeautifulSoup(widget_html, 'html.parser')
    products = soup.find_all(id=re.compile(r'product\d+'))
    return {p.find('a').text.strip(): p.find(class_='s-la-product-status').text for p in products}


app = Flask(__name__)
lexer = Lexer()


@app.route('/')
def root():
    return {'status': 'ok'}


@app.route('/status')
def get_status_counts():
    response = requests.get(STATUS_URL)
    if not response.ok:
        app.logger.error(f'Request to {STATUS_URL} returned {response.status_code} {response.reason}')
        return {'error': 'Service Unavailable'}, 500

    app.logger.debug(response.headers)

    widget_html = get_widget_html(response.text)
    if widget_html is None:
        app.logger.error(f'Widget HTML could not be extracted from {STATUS_URL}')
        return {'error': 'Service Unavailable'}, 500

    status_map = get_status_map(widget_html)

    count = Counter()
    for status in status_map.values():
        count[status] += 1

    total = len(status_map)
    non_normals = [k for k, v in status_map.items() if v != 'Normal']

    return {
        'total': total,
        'normal': count['Normal'],
        'outage': count['Outage'],
        'problem': total - (count['Normal'] + count['Outage']),
        'non_normal': len(non_normals),
        'non_normal_list': non_normals
    }
