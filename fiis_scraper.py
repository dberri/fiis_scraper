#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import bs4 as bs
import re
import sys
import os
import csv

FILE_NAME = 'analysis.csv'
DIVIDEND_YIELD = 5
PRICE_OVER_NETWORTH = 1.2

class Fundo:
    ticker = ''
    soup = ''
    '''
    {'ticker': [
        'Rendimento % médio 12 meses',
        'Cotação base',
        'Rendimento %:',
        'Cotação/Valor Patrimonial:',
        'Pode comprar'
    ]}
    '''
    resultado = []

    def __init__(self, ticker):
        self.ticker = ticker

    @staticmethod
    def writeCSVHeader():
        print('Writing CSV header...')
        with open(FILE_NAME, 'w+') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([
                "Ticker",
                "Rendimento anual (%)",
                "Cotação",
                "Rendimento mês (%)",
                "C/VP",
                "Recomendado"
            ])

    def getIndicadores(self):
        print(f'Getting data for {self.ticker.upper()}...')
        data = requests.get(f'https://fiis.com.br/{self.ticker}')
        self.soup = bs.BeautifulSoup(data.content, 'html.parser')

        if self.soup:
            self.searchStuff()
    
    def getDividendYield(self):
        dyItem = self.soup.find(id="informations--indexes").find_all(class_='item')[0]
        dy =  dyItem.find_all(class_="value")[0].get_text()
        return float(re.search(r'\d+,\d+', dy).group(0).replace(',', '.')) * 12

    def getCurrentPrice(self):
        return float(self.soup.find(class_="item quotation").find(class_="value").get_text().replace(',', '.'))

    def getNetWorth(self):
        netWorthItem = self.soup.find(id="informations--indexes").find_all(class_='item')[-1]
        netWorth = netWorthItem.find_all(class_="value")[0].get_text()
        return float(re.search(r'\d+,\d+', netWorth).group(0).replace(',', '.'))

    def searchStuff(self):
        data = []
        dy = self.getDividendYield()
        data.append(dy)
        price = self.getCurrentPrice()
        data.append(price)
        netWorthPerQuota = self.getNetWorth()
        data.append(netWorthPerQuota)
        data.append(price / netWorthPerQuota)

        self.resultado = data

        if self.resultado[0] > DIVIDEND_YIELD and self.resultado[3] < PRICE_OVER_NETWORTH:
            self.resultado.append(1)
        else:
            self.resultado.append(0)

        self.writeToCSV()

    def writeToCSV(self):
        print('Writing data to CSV...')
        with open(FILE_NAME, 'a+') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            # writer.writerow([
            #     "Ticker",
            #     "Dividend Yield (%)",
            #     "Cotação",
            #     "Rendimento mês (%)",
            #     "C/VP"
            # ])
            writer.writerow([self.ticker.upper()] + self.resultado)


if __name__ == "__main__":

    if (len(sys.argv) > 1):
        Fundo.writeCSVHeader()
        tickers = sys.argv[1:]
        for ticker in tickers:
            fundo = Fundo(ticker)
            fundo.getIndicadores()
        print('Done!')
    else:
        print('Ticker do fundo não informado!')
