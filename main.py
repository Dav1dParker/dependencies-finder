from bs4 import BeautifulSoup
import requests


def get_file_dependencies_part1(name_package):
    """Ворзвращает ссылку на github этого пакета"""

    PIP_URL = "https://pypi.org/project/"

    page = requests.get(PIP_URL + name_package) # Получаем html страницы указанного пакета
    if page.status_code != 200: # Если ошибка в запросе, то возвращаем None
        return None
    text = page.text
    soup = BeautifulSoup(text, "html.parser")
    links_html = soup.find_all('a')

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
        return None
    text = page.text
    soup = BeautifulSoup(text, "html.parser")
    links_html = soup.find_all('a')
    array = []

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
    page = requests.get(page_url)
    if page.status_code != 200:
        return None
    text = page.text
    soup = BeautifulSoup(text, "html.parser")

    name_packages = set()

    flag = False
    body_fail = soup.find_all('tr')
    for line in body_fail:
        if "]" in line.text or line.text is None:
            flag = False
        if flag:
            count = 0
            for el in line.text:
                if el == " " or el == "\n":
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


def work(package, tab):
    urls = get_file_dependencies(package)
    if urls is not None:
        for url in urls:
            if url is not None:
                if get_name_packages(url) is not None:
                    for name in get_name_packages(url):
                        if name is None:
                            continue
                        print("\t" * tab + package + " -> " + name)
                        work(name, tab + 1)


if __name__ == '__main__':
    package = input("Введите название пакета для которого нужно вывести дерево зависимостей: ")
    print("digraph " + package + "{")
    work(package, 0)
    print("}")