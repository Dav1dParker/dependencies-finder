from bs4 import BeautifulSoup
import requests


"""
ДЗ №2. Визуализатор зависимостей пакета
Написать на выбранном вами языке программирования программу,
которая принимает в качестве аргумента командной строки имя пакета,
а возвращает граф его зависимостей в виде текста на языке Graphviz.
На выбор: для npm или для pip. Пользоваться самими этими менеджерами пакетов запрещено.
Главное, чтобы программа работала даже с неустановленными пакетами и без использования pip/npm.
"""


def get_file_dependencies_part1(name_package):

    PIP_URL = "https://pypi.org/project/"

    page = requests.get(PIP_URL + name_package) # Получаем html страницы указанного пакета
    if page.status_code != 200: # Если ошибка в запросе, то возвращаем None
        #print ("Пакет не существует")
        return None
    text = page.text
    soup = BeautifulSoup(text, "html.parser")
    links_html = soup.find_all('a') #найти все элементы a (ссылки HTML) в разобранной HTML-странице

    for link_html in links_html: # Ищем ссылку на github указанного пакета
        if link_html.get('href') is not None \
                and "https://github.com/" in link_html.get("href") \
                and name_package.lower() in link_html.get("href") \
                and (link_html.get("href")[-len(name_package) - 1:] == name_package + "/"
                     or link_html.get("href")[-len(name_package):] == name_package):
            return link_html.get("href")
    return None


def get_file_dependencies_part2(link): #Функция, возвращающая вторую часть ссылки на файл с зависимостями
    """Возвращает вторую часть ссылки на файл с зависимостьями"""

    page = requests.get(link) # Получаем html страницы указанной ссылки
    if page.status_code != 200:# Если ошибка в запросе, то возвращаем None
        #print("Пакет не существует")
        return None
    text = page.text
    soup = BeautifulSoup(text, "html.parser")
    links_html = soup.find_all('a')
    array = [] #Хранит ссылки на файлы setup.py или setup.org

    # Ищем ссылки на файлы setup.py или setup.cfg
    for link_html in links_html:
        if link_html.get('href') is not None and (
                "setup.py" in link_html.get("href") or "setup.cfg" in link_html.get("href")):
            array.append(link_html.get("href"))
    return array


def get_file_dependencies(name_package):
    """Возвращает ссылку на файл с зависимостьями пакета"""
    links = []

    link_part1 = get_file_dependencies_part1(name_package)
    if link_part1 is None:
        return None

    repeated_part = link_part1.replace("https://github.com/", "")

    link_part2 = get_file_dependencies_part2(link_part1)
    if link_part2 is None:
        return None
    for link_2 in link_part2:
        links.append(link_part1 + link_2.replace(repeated_part, "")[1:])
    return links


def get_name_packages(page_url):
    """Возвращает названия зависимых пакетов"""
    page = requests.get(page_url) # Получаем html страницы указанной ссылки
    if page.status_code != 200:
        return None
    text = page.text
    soup = BeautifulSoup(text, "html.parser")

    name_packages = set() # Хранит имена всех пакетов

    flag = False # Флаг для отслеживания, находимся ли мы в блоке зависимостей
    body_fail = soup.find_all('tr')# Находим все элементы 'tr' в HTML
    for line in body_fail:
        if "]" in line.text or line.text is None:
            flag = False # Если мы достигаем конца блока зависимостей, устанавливаем флаг в False
        if flag: # Если мы находимся в блоке зависимостей
            count = 0 # Счетчик количества ведущих пробелов в строке
            for el in line.text:
                if el == " " or el == "\n": # Увеличиваем счетчик для каждого ведущего пробела или переноса
                    count += 1
                else:
                    break
            first_index = count
            if line.text[first_index:].find(" ") != -1:
                last_index = line.text[first_index:].find(" ") + first_index
            elif line.text[first_index:].find(";") != -1:
                last_index = line.text[first_index:].find(";") + first_index
            elif line.text[first_index:].find(">") != -1:
                last_index = line.text[first_index:].find(">") + first_index
            else:
                last_index = 0
            name = line.text[first_index:last_index].replace(";", "").replace(" ", "").replace('"', "")
            if "\n" in name or name == "":
                continue
            name_packages.add(name)
        if "install_requires" in line.text or "requires = [" in line.text:
            flag = True
    return name_packages



def start(package, tab, output): #Функция вызывает себя рекурсивно, чтобы найти все зависимости пакета
    urls = get_file_dependencies(package) # Получаем ссылки на файлы с зависимостями пакета
    if urls is not None: # Для каждой ссылки
        for url in urls:
            if url is not None:
                if get_name_packages(url) is not None: # Получаем имена зависимостей из файла
                    for name in get_name_packages(url):
                        if name is None:
                            continue
                        output += "\t" * tab + package + " -> " + name + ';\n'
                        output = start(name, tab + 1, output)# Рекурсивно вызываем функцию для найденной зависимости
    return output


package = input("Введите название пакета для которого нужно вывести дерево зависимостей: ")
output = ("digraph " + package + "{\n")
result = start(package, 0, '')
if result == '':
    print("Такой пакет не найден")
else:
    output += result +"}"
    print (output)