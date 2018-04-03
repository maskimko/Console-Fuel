#!/usr/bin/env python3

import json
import urllib3
import certifi
from termcolor import colored
from terminaltables import AsciiTable
from bs4 import BeautifulSoup
from bs4.element import Tag

URL_UKRNET = "https://www.ukr.net/ajax/fuel.json"
URL_MINFIN = "http://index.minfin.com.ua/fuel/tm/"
DIESEL_ID = "\u0414\u0422"
DIESEL_PLUS_ID = DIESEL_ID + "+"
FUEL_TYPES = ['A92', 'A95', 'A95plus', 'Diesel', 'LPG']
A92 = "\u0410\xa092"
A95 = "\u0410\xa095"
A95plus = "\u0410\xa095+"
LPG = "\u0413\u0430\u0437"  # "Газ"
BRAND = "\u041e\u043f\u0435\u0440\u0430\u0442\u043e\u0440"  # "Оператор"
COLOR_MAP = {BRAND: "white", A92: "cyan", A95: "grey", A95plus: "magenta", DIESEL_ID: "blue", LPG: "yellow"}


class FuelPrice:

    def __init__(self, name, fuel_prices):
        self.fuel_prices = dict()
        self.brand = name
        for key in fuel_prices.keys():
            if key not in FUEL_TYPES:
                raise Exception("Unsupported fuel type")
            self.fuel_prices[key] = fuel_prices.get(key, "--")


def get_data_ukr_net(http, url):
    # TODO Standardize prices to list of FuelPrice objects
    r = http.request('GET', url)
    prs = json.loads(r.data.decode('utf-8'))
    return prs


def get_data_minfin(http, url):
    user_agent = "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"
    r = http.request('GET', url, headers={'user-agent': user_agent})
    soup = BeautifulSoup(r.data.decode('utf-8'), 'html.parser')

    def find_content(tag):
        return tag.name == 'div' and tag.has_attr('id') and tag['id'] == 'tm-table'

    def find_price_table(tag):
        return tag.name == 'table' and tag.has_attr('class') and 'zebra' in tag['class'] and find_content(tag.parent)

    def parse_table_header(headers):
        column_order = []
        i = 0
        if len(headers) < 6:
            raise Exception('Unsupported table format')
        while i < len(headers):
            header = headers[i]
            if header.name == 'th':
                if str(header.contents[0].string) == BRAND:
                    column_order.append('name')
                elif header.contents[0].name == 'a':
                    ft = header.contents[0].contents[0]
                    if ft == A92:
                        column_order.append(FUEL_TYPES[0])
                    elif ft == A95:
                        column_order.append(FUEL_TYPES[1])
                    elif ft == A95plus:
                        column_order.append(FUEL_TYPES[2])
                    elif ft == DIESEL_ID:
                        column_order.append(FUEL_TYPES[3])
                    elif ft == LPG:
                        column_order.append(FUEL_TYPES[4])
                else:
                    raise Exception('Cannot parse table header')
            else:
                return None
            i += 1
        return column_order

    def parse_price_table(table):
        table_rows = []
        for row in table.children:
            if type(row) is Tag and row.name == 'tr':
                table_rows.append(row)
        has_header = False
        fuel_prices = []
        column_order = dict()
        if len(table_rows) > 0:

            headers = table_rows[0].contents
            co = parse_table_header(headers)
            if co:
                column_order = co
                has_header = True

            j = 1 if has_header else 0
            while j < len(table_rows):
                tr = table_rows[j]
                name = None
                prices_dict = dict()
                col = 0
                # number of the html table column to parse
                pcol = 0
                while col < len(column_order):
                    if column_order[col] == 'name':
                        name = tr.contents[pcol].contents[0].text
                    else:
                        string_price = str(tr.contents[pcol].contents[0])
                        if string_price == '<br/>':
                            if tr.contents[pcol].attrs.get('style', None) == 'padding:3px':
                                pcol += 1
                            else:
                                col += 1
                            continue
                        prices_dict[column_order[col]] = float(string_price.replace(',', '.'))
                    col += 1
                    pcol += 1
                fuel_prices.append(FuelPrice(name, prices_dict))
                j += 1
        else:
            raise Exception('Empty table')
        return fuel_prices
    price_table = soup.find(find_price_table)
    parsed_fuel_prices = parse_price_table(price_table)
    return parsed_fuel_prices


def compute_average(fuel_prices):
    avg = dict()
    for ft in FUEL_TYPES:
        total = float(0)
        count = 0
        for price in fuel_prices:
            p = price.fuel_prices.get(ft, None)
            if p:
                total += p
                count += 1
        if count == 0:
            avg[ft] = '--'
        else:
            avg[ft] = total / count
    return avg


def make_table_data(fuel_prices):
    heading = [colored(br, col) for br, col in COLOR_MAP.items()]
    tableData = [heading]
    avg = compute_average(fuel_prices)
    for price in fuel_prices:
        row = [price.brand]
        for ft in FUEL_TYPES:
            p = price.fuel_prices.get(ft, '--')
            if p != '--':
                color = decide_color(p, avg[ft])
                row.append(colored(p, color))
            else:
                row.append(p)
        tableData.append(row)

    return tableData


def decide_color(average, value):
    color = "grey"
    if average != '--':
        if value > average:
            color = "green"
        elif value < average:
            color = "red"
    return color


def print_table(fuel_prices):
    table_instance = AsciiTable(make_table_data(fuel_prices))
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)


if __name__ == "__main__":
    http_pool_manager = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    # prices = get_data_ukr_net(http, URL_UKRNET)
    prices = get_data_minfin(http_pool_manager, URL_MINFIN)
    print_table(prices)
