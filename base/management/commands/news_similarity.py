from django.core.management.base import BaseCommand
from base.models import Noticia
from newspaper import Article
from difflib import SequenceMatcher


class Command(BaseCommand):
    help = 'Analisa a similaridade entre o texto revisado do usuário e o artigo original'

    def handle(self, *args, **kwargs):
        # obtendo todas as notícias que foram revisadas pelo usuário
        noticias_revisadas = Noticia.objects.filter(revisado=True)

        for noticia in noticias_revisadas:
            url = noticia.url  # substitua pela sua maneira de obter a URL da notícia
            article = Article(url)
            article.download()
            article.parse()

            original_text = article.text
            reviewed_text = noticia.texto_completo  # substitua pela sua maneira de obter o texto revisado

            similarity = self.calculate_similarity(original_text, reviewed_text)
            self.stdout.write(self.style.SUCCESS(f'A similaridade entre os textos revisado e original é {similarity}'))

    @staticmethod
    def calculate_similarity(a, b):
        return SequenceMatcher(None, a, b).ratio()
