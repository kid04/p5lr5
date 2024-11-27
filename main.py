import csv

import requests
import time
import json
from xml.etree import ElementTree as ET
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Component():
    def get_currencies(self) -> str:
        pass

class CurrenciesLst(Component, metaclass=Singleton):
    def __init__(self, id_lst, limit=1000):
        self.__id_list = id_lst
        self.__cur_dict = {}
        self.last_time = 0
        self.limit = limit

    def get_currencies(self) -> list:
        if time.time() - self.last_time < self.limit:
            time.sleep((self.limit - time.time() + self.last_time)/1000)
        self.last_time = time.time()
        cur_res_str = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')
        result = {}

        root = ET.fromstring(cur_res_str.content)
        valutes = root.findall(
            "Valute"
        )
        for _v in valutes:
            valute_id = _v.get('ID')

            if str(valute_id) in self.__id_list:
                valute_cur_name, valute_cur_val = _v.find('Name').text, tuple(int(x) for x in _v.find('Value').text.split(','))
                valute_charcode = _v.find('CharCode').text
                if _v.find('Nominal').text != '1':
                    valute_cur_nominal = int(_v.find('Nominal').text)
                    result[valute_charcode] = (valute_cur_name, valute_cur_val, valute_cur_nominal)
                else:
                    result[valute_charcode] = (valute_cur_name, valute_cur_val)

        self.__cur_dict = result
        return result

    def get_graph(self):
        import matplotlib.pyplot as pplt
        x, y = [], []
        for cur in self.__cur_dict.values():
            x.append(cur[0])
            y.append(cur[1][0])
        pplt.bar(x, y)
        pplt.savefig('currencies.jpg')


    @property
    def cur_lst(self):
        return self.__cur_dict

    @property
    def id_list(self):
        return self.__id_list

    @id_list.setter
    def id_list(self, lst):
        self.__id_list = lst

class Decorator(Component):

    _component: Component = None

    def __init__(self, component: Component) -> None:
        self._component = component

    @property
    def component(self):

        return self._component

    def get_currencies(self) -> str:
        return self._component.get_currencies()

class ConcreteDecoratorJSON(Decorator):
    def get_currencies(self) -> str:
        """
        Декораторы могут вызывать родительскую реализацию операции, вместо того,
        чтобы вызвать обёрнутый объект напрямую. Такой подход упрощает
        расширение классов декораторов.
        """

        return json.dumps(self.component.get_currencies(), ensure_ascii=False)

class ConcreteDecoratorSCV(Decorator):
    def get_currencies(self) -> None:
        currencies = self.component.get_currencies()
        with open('currencies.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for currency in currencies:
                row = [currencies[currency][i] for i in range(len(currencies[currency]))]
                row.insert(0, currency)
                writer.writerow(row)


if __name__ == '__main__':

    cclass = CurrenciesLst(['R01090B', 'R01335', 'R01700J'])
    jclass = ConcreteDecoratorJSON(cclass)
    CSVclass = ConcreteDecoratorSCV(cclass)
    print(jclass.get_currencies())
    print(CSVclass.get_currencies())

