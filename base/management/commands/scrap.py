import os
import time
import requests

from django.core.management.base import BaseCommand
from base.models import Noticia

from base64 import b64decode
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from selenium.webdriver.common.by import By

from .get_text import extract_text, extract_scripts_and_styles, load_html, scrap_best_image, save_image, get_url_base


def print_pdf(url, filename):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(executable_path='webdrive/chromedriver', options=options)
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(10)
    driver.implicitly_wait(5)
    internal_id = filename.split('/pdf/')[ 1 ].split('.pdf')[0]
    try:
        driver.get(url)
    except TimeoutException:
        print(f'Timeout exception ({internal_id}): {url}')
        driver.quit()
        return None, None
    except Exception as e:
        print(f'General exception ({internal_id}): {url}')
        print(e.__str__())
        driver.quit()
        return None, None

    html = driver.page_source
    soup = extract_scripts_and_styles(html)
    if url != driver.current_url:
        print(f'URL Redirected: filename: {filename}')
        print(f'{url}, {driver.current_url}')

    # código de exemplo para travar a página após encontrar um elemento
    # if driver.find_element(By.XPATH, '//*[@id="tags"]'):
    possible_btns = ["toolkit-privacy-box__btn",
                     "cookie-banner-lgpd_accept-button", "onesignal-slidedown-cancel-button"]
    #for class_btn in possible_btns:
    #    try:
    #        button = driver.find_element_by_class_name(class_btn)
    #        webdriver.ActionChains(driver).click(button)
    #        break
    #    except NoSuchElementException:
    #        None

    try:
        a = driver.execute_cdp_cmd("Page.printToPDF", {"path": 'html.pdf', "format": 'A4'})
        # Define the Base64 string of the PDF file
        if a:
            b64 = a['data']
            # Decode the Base64 string, making sure that it contains only valid characters
            raw_content = b64decode(b64, validate=True)
            if raw_content[0:4] != b'%PDF':
                raise ValueError('Missing the PDF file signature')
            # Write the PDF contents to a local file
            f = open(filename, 'wb')
            f.write(raw_content)
            f.close()
        else:
            raise ValueError('No data')
    except Exception as e:
        print(f'PDF exception ({internal_id}): {url}')
        print(e.__str__())
        filename = None
    finally:
        driver.quit()

    return soup, filename


class Command(BaseCommand):
    help = 'Importa as URLs em formato de texto e PDF'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', type=str, help='Id da Notícia')

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        html_path = os.path.join('/', base_dir, 'media', 'html')
        pdf_path = os.path.join('/', base_dir, 'media', 'pdf')
        img_path = os.path.join('/', base_dir, 'media', 'img')
        os.makedirs(pdf_path, exist_ok=True)
        os.makedirs(img_path, exist_ok=True)

        tot_lidos = 0
        tot_scrap = 0
        tot_pdfs = 0
        tot_imagens = 0
        st = time.time()

        if options['id']:
            dataset = Noticia.objects.filter(id=options['id'], revisado=False)
        else:
            dataset = Noticia.objects.filter(url_valida=True, atualizado=False,
                                             revisado=False, origem=2, visivel=True)

        for noticia in dataset:
            tot_lidos += 1
            if tot_lidos % 100 == 0:
                print(f'Lidos: {noticia.id} {noticia.id_externo}')

            # if not os.path.exists("%s/%d.pdf" % (html_path, noticia.id)):
            print(f'Scraping {noticia.url}')
            if noticia.origem == 2:
                soup = load_html(noticia.url, noticia.id, True)
                # noticia.media contém por enquanto o screenshot do site por isso não pode ser utilizado
                if not noticia.imagem:
                    melhor_imagem = scrap_best_image(soup)
                    if melhor_imagem:
                        if melhor_imagem[0] == '/':
                            base_site = get_url_base(noticia.url)
                            melhor_imagem = base_site + melhor_imagem[1:]
                        filename = "%s/%d" % (img_path, noticia.id)
                        file_path = save_image(melhor_imagem, filename)
                        noticia.imagem = file_path
                        tot_imagens += 1
                # TODO: Gerar o PDF a partir do snippet do Arquivo.pt
                pdf_result = None
                pdf_filename = None
            else:
                pdf_filename = '%s/%d.pdf' % (pdf_path, noticia.id)
                soup, pdf_result = print_pdf(url=noticia.url, filename=pdf_filename)
            if soup:
                if pdf_result:
                    tot_pdfs += 1
                else:
                    # caso o não se consiga criar o PDF e caso algum PDF já exista com essa numeração,
                    # deve-se alterar para _old.
                    if pdf_filename and os.path.exists(pdf_filename):
                        os.rename(pdf_filename, pdf_filename.replace('.pdf','_old.pdf'))

                # get text
                tot_scrap += 1
                noticia.texto_completo = extract_text(soup)
                noticia.atualizado = True
                noticia.save()
            else:
                noticia.atualizado = False
                noticia.save()

        print(f'Total de registros lidos: {tot_lidos}')
        print(f'Total de pdfs gerados: {tot_pdfs}')
        print(f'Total de novas imagens: {tot_imagens}')
        print(f'Total de textos capturados: {tot_scrap}')
        elapsed_time = (time.time() - st) / 60
        print('Execution time:', elapsed_time, 'minutes')