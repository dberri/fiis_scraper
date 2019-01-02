import requests
import bs4 as bs
import re
import sys
import os
import csv

FILE_NAME = 'analysis.csv'


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
        data = requests.get(f'https://fiis.com.br/{self.ticker}/?aba=indicadores')
        # data.status_code
        # ?aba=geral
        self.soup = bs.BeautifulSoup(data.content, 'html.parser')

        self.searchStuff()

    def searchStuff(self):
        search = [
            ['Rendimento % médio 12 meses', r"\d+,\d+%"],
            ['Cotação base', r"R\$ \d+,\d+"],
            ['Rendimento %:', r"\d+,\d+%"],
            ['Cotação/Valor Patrimonial:', r"\d+,\d+"],
        ]

        data = []
        for search_str in search:
            result = self.soup.find_all(string=re.compile(search_str[0]))
            parsed = re.findall(search_str[1], result[0])
            # print(search_str[0])
            # print(parsed[0])
            # print('')
            value_str = re.search(r'\d+,\d+', parsed[0]).group(0)
            value_num = float(value_str.replace(',', '.'))
            data.append(value_num)

        self.resultado = data

        if self.resultado[0] > 7.5 and self.resultado[3] < 1.1:
            self.resultado.append(1)
        else:
            self.resultado.append(0)

        # print(self.resultado)

        self.writeToCSV()

    def writeToCSV(self):
        print('Writing data to CSV...')
        with open(FILE_NAME, 'a+') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            # writer.writerow([
            #     "Ticker",
            #     "Rendimento anual (%)",
            #     "Cotação",
            #     "Rendimento mês (%)",
            #     "C/VP"
            # ])
            writer.writerow([self.ticker.upper()] + self.resultado)


if __name__ == __main__:

    if (len(sys.argv) > 1):
        Fundo.writeCSVHeader()
        tickers = sys.argv[1:]
        for ticker in tickers:
            fundo = Fundo(ticker)
            fundo.getIndicadores()
        print('Done!')
    else:
        print('Ticker do fundo não informado!')
