from django.core.management.base import BaseCommand
from Levenshtein import ratio
from newspaper import Article
from base.models import Noticia


class Command(BaseCommand):
    help = 'Compares the user-reviewed text with the processed text from the Newspaper library'

    def handle(self, *args, **options):
        news = Noticia.objects.filter(revisado=True, id=6636)
        for noticia in news:
            article = Article(noticia.url)
            article.download()
            article.parse()

            lev_ratio = ratio(noticia.texto, article.text)
            print(f"A semelhança de Levenshtein para a notícia {noticia.id} é {lev_ratio}")

            if lev_ratio < 0.6:  # Altere este valor conforme necessário
                print(f"As versões são muito diferentes para a notícia {noticia.id}")

            print(article.text)
