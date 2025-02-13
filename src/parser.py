from bs4 import BeautifulSoup
import re

regexp = "（[^）]*）"
names_sep = "、"
works_sep = "："


class Parser:
    html = ""
    base_url = ""

    def __init__(self, html: str, base_url: str = ""):
        self.html = html
        self.base_url = base_url

    def aiueo(self):
        soup = BeautifulSoup(self.html, "lxml")

        base_url = "/".join(self.base_url.split("/")[0:3])

        a_list = soup.find("div", attrs={"data-e2eid": "panel-index"}).find_all("a")
        return [self.base_url] + list(map(lambda a: base_url + a["href"], a_list))

    def pages(self):
        soup = BeautifulSoup(self.html, "lxml")

        last_page_li = soup.find("ul", attrs={"data-e2eid": "pagination"}).find_all(
            "li"
        )[-2]
        last_page = int(last_page_li.find(string=True))

        if last_page > 1:
            urls = list(
                map(
                    lambda page: self.base_url + "&page=" + str(page),
                    range(2, last_page + 1),
                )
            )
            return [self.base_url] + urls
        else:
            return [self.base_url]

    def parse(self):
        soup = BeautifulSoup(self.html, "lxml")

        out = list()
        for li in soup.find("ul", attrs={"data-e2eid": "list-actress-root"}).find_all(
            "li"
        ):
            name, name_kana, works = list(li.find_all(string=True))
            pic = li.find("img")["src"]
            link = li.find("a")["href"]
            works_count = int(works.split(works_sep)[1].replace(",", ""))

            name_result = re.search(regexp, name)
            alias_list = list()
            if name_result:
                alias_list = alias_list + name_result.group()[1:-1].split(names_sep)

            name = re.sub(regexp, "", name)
            name_kana = re.sub(regexp, "", name_kana)

            row = [name, name_kana, works_count, pic, [link], alias_list]

            out = out + [row]

        return out
