#!/bin/env python3

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
A92="\u0410\xa092"
A95="\u0410\xa095"
A95plus="\u0410\xa095+"
LPG="\u0421\u041f\u0411\u0422"


class FuelPrice():

    def __init__(self, name, prices):
        self.fuel_prices = dict()
        self.brand = name
        for key in prices.keys():
            if key not in FUEL_TYPES:
                raise "Unsupported fuel type"
            self.fuel_prices[key] =prices.get(key, "--")


def getDataUkrNet(http, url):
    #TODO Standardize prices to list of FuelPrice objects
    r = http.request('GET', url)
    prices = json.loads(r.data.decode('utf-8'))
    return prices

def getDataMinfin(http, url):
    user_agent = "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"
    r = http.request('GET', url, headers={'user-agent': user_agent})
    soup = BeautifulSoup(r.data.decode('utf-8'), 'html.parser')

    def findContent(tag):
        return tag.name == 'div' and tag.has_attr('id') and tag['id'] == 'content'

    def findPriceTable(tag):
        return tag.name == 'table' and tag.has_attr('class') and 'zebra' in tag['class'] and findContent(tag.parent)

    def parseTableHeader(headers):
        column_order = []
        i = 0
        if len(headers) < 6:
            raise 'Unsupported table format'
        while i < len(headers):
            header = headers[i]
            if header.name == 'th':
                has_header = True
                if header.contents[0] == "\u0422\u041c":
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

    def parsePriceTable(table):
        table_rows = []
        for row in table.children:
            if type(row) is Tag and row.name == 'tr':
                table_rows.append(row)
        has_header = False
        fuel_prices = []
        column_order = dict()
        if len(table_rows) > 0:

            headers = table_rows[0].contents
            co = parseTableHeader(headers)
            if co:
                column_order = co
                has_header = True

            j = 1 if has_header else 0
            while j < len(table_rows):
                tr = table_rows[j]
                name = None
                prices = dict()
                col = 0
                while col < len(column_order):
                    if column_order[col] == 'name':
                        name = tr.contents[col].contents[0].text
                    else:
                        string_price = str(tr.contents[col].contents[0])
                        if string_price == '<br/>':
                            col += 1
                            continue
                        prices[FUEL_TYPES[col-1]] = float(string_price.replace(',','.'))
                    col += 1
                fuel_prices.append(FuelPrice(name, prices))
                j += 1
        else:
            raise Exception('Empty table')
        return fuel_prices
    price_table = soup.find(findPriceTable)
    parsed_fuel_prices = parsePriceTable(price_table)
    return parsed_fuel_prices


def computeAverage( prices):
    avg = dict()
    for ft in FUEL_TYPES:
        sum = float(0)
        count = 0
        for price in prices:
            p  = price.fuel_prices.get(ft, None)
            if p:
                sum += p
                count +=1
        avg[ft] = sum / count
    return  avg

def makeTableData(prices):
    # heading = (colored("Gas station", "white"), colored("Diesel", "blue"), colored("Diesel+", "cyan"))
    heading = (colored("Gas station", "white"), colored(DIESEL_ID, "blue"),
               colored(A92, "cyan"), A95, colored(A95plus,"magenta"), colored(LPG,"yellow"))
    tableData = [heading]
    # for fuelType in prices["fuel"]:
    #     if fuelType["Fuel"] == DIESEL_ID:
    #         for station in fuelType["Stations"]:
    #             color = decideColor(float(station["Value"]), float(fuelType["Avg"]))
    #             tableData.append([colored(station["Name"], color), colored(station["Value"], color), "-"])
    #     if fuelType["Fuel"] == DIESEL_PLUS_ID:
    #         for station in fuelType["Stations"]:
    #             color = decideColor(float(station["Value"]), float(fuelType["Avg"]))
    #             tableData.append([colored(station["Name"], color), "-", colored(station["Value"], color)])
    avg = computeAverage(prices)
    for price in prices:
        row = [price.brand]
        for ft in FUEL_TYPES:
            p = price.fuel_prices.get(ft, '--')
            if p != '--':
                color = decideColor(p, avg[ft])
                row.append(colored(p, color))
            else:
                row.append(p)
        tableData.append(row)

    return tableData


def decideColor(average, value):
    color = "grey"
    if value > average:
        color = "green"
    else:
        color = "red"
    return color


def printTable(prices):
    tableInstance = AsciiTable(makeTableData(prices))
    tableInstance.justify_columns[2] = 'right'
    print(tableInstance.table)


if __name__ == "__main__":
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    #prices = getDataUkrNet(http, URL_UKRNET)
    #printTable(prices)
    prices = getDataMinfin(http, URL_MINFIN)
    printTable(prices)
