import json
import os
import re
from collections import Counter

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask
from slimit.parser import Parser
from slimit.visitors.nodevisitor import ASTVisitor

load_dotenv('../.env')
STATUS_URL = os.environ.get('STATUS_URL')

if STATUS_URL is None:
    raise RuntimeError('Must set STATUS_URL')

app = Flask(__name__)


class WidgetExtractor(ASTVisitor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget_html = None

    def visit_Object(self, node):
        """Visit object literal nodes, looking for a "widgethtml" key with a value that looks like markup."""
        for prop in node:
            if prop.left.value == 'widgethtml' and prop.right.value.startswith('"<'):
                # parse JSON string
                self.widget_html = json.loads(prop.right.value)


@app.route('/')
def root():
    return {'status': 'ok'}


@app.route('/status')
def get_status_counts():
    response = requests.get(STATUS_URL)

    parser = Parser()
    tree = parser.parse(response.text)

    visitor = WidgetExtractor()
    visitor.visit(tree)
    soup = BeautifulSoup(visitor.widget_html, 'html.parser')
    products = soup.find_all(id=re.compile(r'product\d+'))
    status_map = {p.find('a').text.strip(): p.find(class_='s-la-product-status').text for p in products}

    count = Counter()
    for name, status in status_map.items():
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
