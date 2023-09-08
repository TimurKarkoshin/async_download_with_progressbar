import asyncio
import httpx
import tqdm
from colorama import init, Fore
from art import text2art, aprint

init(autoreset=True)


class Menu:
    def __init__(self):
        self.urls_list = []

    def add_url_to_list(self, url, file_name):
        tup = (url, file_name)
        self.urls_list.append(tup)
        self.choice_event()

    def remove_list(self):
        try:
            self.urls_list.clear()
            print("[-]Список очищен")

        finally:
            self.choice_event()

    async def compile(self):
        cycle = asyncio.get_running_loop()
        urls = self.urls_list

        tasks = [cycle.create_task(download(url, file_name)) for url, file_name in urls]
        await asyncio.gather(*tasks, return_exceptions=True)

    def choice_event(self):
        choice = int(input("[1]Запустить\n"
                           "[2]Добавить ссылку в очередь\n"
                           "[3]Очистить список\n"
                           "[4]Вывести список ссылок\n"
                           "[5]Выйти из программы\n"
                           "[?]Ваш выбор: "))

        match choice:
            case 1:
                asyncio.run(self.compile())

            case 2:
                url_to_add = input("Введите вашу ссылку: ")
                file_name = input("Введите имя файла с предпологаемым расширением: ")
                self.add_url_to_list(url_to_add, file_name)

            case 3:
                self.remove_list()

            case 4:
                for url in self.urls_list:
                    print(url)
                self.choice_event()

            case 5:
                exit()

            case _:
                print("Выбор некорректен, пожалуйста, проверьте ввод!")
                self.choice_event()


async def download(url: str, file_name: str):
    """
    Функция для скачивания файлов
    :param url:
    :param file_name:
    :return:
    """

    with open(file_name, "wb") as file:
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url) as f:
                f.raise_for_status()
                total = int(f.headers.get('content-length', 0))

                tqdm_params = {
                    'desc': url,
                    'total': total,
                    'miniters': 1,
                    'unit': 'it',
                    'unit_scale': True,
                    'unit_divisor': 1024,
                }

                with tqdm.tqdm(**tqdm_params) as cf:
                    async for chunk in f.aiter_bytes():
                        cf.update(len(chunk))
                        file.write(chunk)


if __name__ == '__main__':
    print(text2art("hello", "block"))
    aprint('happy')
    print(Fore.LIGHTWHITE_EX +
          "[i]Добрый день! Эта программа нужна для скачки файлов в асинронном режиме.\n"
          "[i]Старт невероятно прост - добавьте ссылку и будущее название файла с помощью команды [2]\n"
          "[i]Поняли что добавили что-то не то? "
          "Не время разбивать клавиатуру об экран, просто нажмите [3] находясь в меню!\n"
          "[i]Забыли что добавялили в список? Команда [4] отобразит весь существующий список ссылок и имён файлов.\n"
          "[i]Для запуска скачивания всех файлов команда [1]\n"
          "[i]Что бы выйти нажмите [5]\n"
          )
    menu = Menu()
    menu.choice_event()
