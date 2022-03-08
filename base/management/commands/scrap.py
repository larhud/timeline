import os

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from base.models import Noticia

import json
from base64 import b64decode
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


def print_pdf(url, filename):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path='webdrive/chromedriver', options=options)
    driver.set_page_load_timeout(60)
    try:
        driver.get(url)
    except TimeoutException:
        print('Timeout exception %s' % url)
        return None

    html = driver.page_source
    if url != driver.current_url:
        print(filename, driver.current_url)

    # a = driver.find_element_by_css_selector("#loanamountslider")
    # webdriver.ActionChains(driver).click(
    #    a).click_and_hold().move_by_offset(0, 0).perform()

    a = driver.execute_cdp_cmd(
        "Page.printToPDF", {"path": 'html.pdf', "format": 'A4'})
    # Define the Base64 string of the PDF file
    b64 = a['data']

    # Decode the Base64 string, making sure that it contains only valid characters
    raw_content = b64decode(b64, validate=True)
    if raw_content[0:4] != b'%PDF':
        raise ValueError('Missing the PDF file signature')

    # Write the PDF contents to a local file
    f = open(filename, 'wb')
    f.write(raw_content)
    f.close()
    return html


class Command(BaseCommand):
    help = 'Importa as URLs em formato de texto e PDF'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        html_path = os.path.join('/', base_dir, 'media', 'html')
        pdf_path = os.path.join('/', base_dir, 'media', 'pdf')
        # driver = configure_driver(dest_path)
        os.makedirs(pdf_path, exist_ok=True)
        for noticia in Noticia.objects.filter(url_valida=True, atualizado=False):
            # html = print_page(driver, url=noticia.url, id=noticia.id)
            print(noticia.id)
            html = print_pdf(url=noticia.url, filename='%s/%d.pdf' % (pdf_path, noticia.id))
            if html:
                soup = BeautifulSoup(html, features="html.parser")
                # kill all script and style elements
                for script in soup(["script", "style", "noscript"]):
                    script.extract()    # rip it out
                with open('%s/%d.html' % (html_path, noticia.id),'w',encoding='utf-8') as f:
                    f.write(str(soup))

                # get text
                text = soup.get_text()
                # break into lines and remove leading and trailing space on each
                lines = (line.strip() for line in text.splitlines())
                # break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # drop blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
                noticia.texto_completo = text
                noticia.atualizado = True
                noticia.save()
