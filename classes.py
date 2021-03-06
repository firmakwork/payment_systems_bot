import bs4
import pickle
from typing import Literal
from dataclasses import dataclass
def save_object(data, file_name="tasks.pkl"):
    with open(file_name, "wb+") as fp:
        pickle.dump(data, fp)


def load_object(file_name="tasks.pkl"):
    with open(file_name, "rb+") as fp:
        data = pickle.load(fp)
    return data


@dataclass
class User:
    username: str
    fio: str
    subscription: int
    flag: int
    message_id: int
    type_payment: str
    price: int
    invoice_id: int

    def set_type_payment(self, choice: Literal["yookassa", "interkassa"]):
        self.type_payment = choice

    def set_type_subscription(self, choice: Literal[3, 10, 30]):
        self.subscription = choice

    def set_price(self, choice: Literal[400, 800, 1800]):
        self.price = choice

###Класс нереляционной бд
class nsql_database:
    def __init__(self) -> None:
        self.data = {}

    # Получение значения по ключу
    def get_elem(self, key: int | str) -> User | bool:
        if key in self.data:
            return self.data[key]
        else:
            return False


class Users(nsql_database):
    def __init__(self):
        super().__init__()

    def __contains__(self, other: int) -> bool:
        if other in self.data:
            return True
        else:
            return False

    def __add_user(self, id: int):
        self.data[id] = User(username="",
                             fio="",
                             subscription=-1,
                             flag=-1,
                             message_id=-1,
                             type_payment="",
                             price=-1,
                             invoice_id=-1)
        return self

    def __add__(self, id: int):
        return self.__add_user(id)

    def __iadd__(self, id: int):
        return self.__add_user(id)

    @staticmethod
    def create_pay(id: int, price: Literal[400, 800, 1800]) -> str:
        with open("./templates/pay.html", "r", encoding='utf-8') as inf:
            txt = inf.read()
        soup = bs4.BeautifulSoup(txt, 'html.parser')
        page = str(soup).split(' ')
        ind = page.index(f'value="ID_122344"/>\n<input')
        page[ind] = f'value="ID_{id}"/>\n<input'
        html = ""
        ind = page.index(f'value="99999"/>\n<input')
        page[ind] = f'value="{price}"/>\n<input'
        for i in page:
            html += i + ' '
        return html
