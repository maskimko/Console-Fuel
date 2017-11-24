#!/bin/env python3

import json
import urllib3
import certifi
from termcolor import colored
from terminaltables import AsciiTable

URL = "https://www.ukr.net/ajax/fuel.json"
DIESEL_ID = "\u0414\u0422"
DIESEL_PLUS_ID = DIESEL_ID + "+"


def getData(http, url):
    r = http.request('GET', url)
    prices = json.loads(r.data.decode('utf-8'))
    return prices


def makeTableData(prices):
    heading = (colored("Gas station", "white"), colored("Diesel", "blue"), colored("Diesel+", "cyan"))
    tableData = [heading]
    for fuelType in prices["fuel"]:
        if fuelType["Fuel"] == DIESEL_ID:
            for station in fuelType["Stations"]:
                color = decideColor(float(station["Value"]), float(fuelType["Avg"]))
                tableData.append([colored(station["Name"], color), colored(station["Value"], color), "-"])
        if fuelType["Fuel"] == DIESEL_PLUS_ID:
            for station in fuelType["Stations"]:
                color = decideColor(float(station["Value"]), float(fuelType["Avg"]))
                tableData.append([colored(station["Name"], color), "-", colored(station["Value"], color)])
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
    prices = getData(http, URL)
    printTable(prices)
