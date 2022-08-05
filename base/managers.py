import ast
import requests
from collections import Counter
from bs4 import BeautifulSoup

from django.db import models
from cms.models import Recurso

from django.core.validators import EMPTY_VALUES
from django.db import models
from django.db.models import Count


def test_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, features="html.parser")
            if soup.title:
                title = soup.title.string
            return True
    except Exception as e:
        return False


def remove_charlist(text, charlist, sep):
    """
    Args:
        text (str): Texto
        charlist (list): Lista com strings a serem removidas.
        sep (char): new separator
    Returns:
        str
    """
    result = ''
    for c in text:
        result += sep if c in charlist else c

    return result


# Cria uma lista com as frases criadas a partir dos delimitadores informados
def make_phrases(texto, separators):
    return [x for x in remove_charlist(texto, separators, '.').split('.') if x]


# Texto: Texto Livre que será quebrado em palavras e Bigramas
# Keywords: Lista de Palavras Chaves que tem que entrar sem ser quebradas em palavras
# Stopwords: Lista de Palavras que não devem ser incluídas na tabela final
#
# A rotina retorna 2 counters: o primeiro com os bigramas e o segundo sem bigramas
#
def build_wordcloud(texto, keywords, stopwords=None):
    texto = remove_charlist(texto, ['’', '”', '(', ')', '`', '"', '\t', '\r', '\''], ' ')
    phrase_delimiters = [':', '.', ',', ';', '?', '!', '\n']
    words = make_phrases(texto, phrase_delimiters + [' '])

    if stopwords is None:
        stopwords = []
    else:
        if len(stopwords) > 0:
            stopwords = set(stopwords)

    cleaned = []
    for termo in words:
        if not termo.isdigit():
            if not (termo.isupper() and len(termo) < 8):
                termo = termo.lower()

        if len(termo) > 2 and termo not in stopwords:
            cleaned.append(termo)

    # Monta os bigramas
    phrases_list = make_phrases(texto, phrase_delimiters)
    bigrams = ['%s %s' % (ele, tex.split()[i + 1]) for tex in phrases_list for i, ele in enumerate(tex.split()) if
               i < len(tex.split()) - 1] + cleaned

    for index, termo in enumerate(bigrams):
        if len(termo.split(' ')[-1]) < 3 and index + 1 < len(bigrams):
            bigrams[index] = ' '.join(bigrams[index].split(' ')[:-1]) + ' ' + bigrams[index + 1]
            del bigrams[index + 1]

    # se houver keywords, faz a separação se baseando nos delimitadores
    for item in keywords:
        for chave in make_phrases(item, [',', ';', '.']):
            if len(chave.strip()) > 2:
                bigrams.append(chave.strip())

    bigrams_cleaned = cleaned.copy()
    for termo in bigrams:
        if termo.isupper() and len(termo) < 8:
            bigrams_cleaned.append(termo)
        else:
            bigrams_cleaned.append(termo.lower())

    return Counter(bigrams_cleaned), Counter(cleaned)


class Search(models.Lookup):
    lookup_name = 'search'

    def as_mysql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'MATCH (%s) AGAINST (%s IN BOOLEAN MODE)' % (lhs, rhs), params


models.TextField.register_lookup(Search)


def add_criteria(dct, opcoes, campo, lookup=None, tipo_lookup='__contains'):
    """
    Atualiza dct com os parâmetros de busca.
    Se lookup for passado, ele será utilizado na montagem do critério de busca.
    Ex.: add_criteria(dct, opcoes, 'nome')
         add_criteria(dct, opcoes, 'nome', lookup='tabela__nome')
         add_criteria(dct, opcoes, 'valor', tipo_lookup='__gte')
    """
    valor = opcoes.get(campo)

    if valor not in EMPTY_VALUES:
        chave = lookup + tipo_lookup if lookup else campo + tipo_lookup
        dct[chave] = valor


class NoticiaQueryset(models.QuerySet):

    def pesquisa(self, **kwargs):
        params = {}
        add_criteria(params, kwargs, 'busca', 'texto_busca', '__search')
        add_criteria(params, kwargs, 'veiculo', 'fonte', '__icontains')
        if kwargs.get('datafiltro', ''):
            add_criteria(params, kwargs, 'datafiltro', 'dt', tipo_lookup='__range')
        else:
            add_criteria(params, kwargs, 'ano_mes', 'dt', tipo_lookup='__range')

        add_criteria(params, kwargs, 'datafiltro', 'dt', tipo_lookup='__range')
        add_criteria(params, kwargs, 'ano_mes', 'dt', tipo_lookup='__range')
        add_criteria(params, kwargs, 'termo', 'assunto__termo__id', tipo_lookup='')
        return self.filter(**params).filter(visivel=True).order_by('dt')

    def anos(self):
        """Retorna uma lista com distinct dos anos da base de notícias"""
        return [r.year for r in self.dates('dt', 'year')]

    def nuvem(self):
        stopwords = Recurso.objects.get_or_create(recurso='TAGS-EXC')[0].valor or ''
        stopwords = [exc.strip() for exc in stopwords.split(',')] if stopwords else []
        result = Counter()
        for record in self.all():
            if record.nuvem:
                nuvem = ast.literal_eval(record.nuvem)
                for termo in nuvem:
                    if termo[0] not in stopwords:
                        result[termo[0]] += termo[1]
        return result.most_common(40)


class AssuntoManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('termo')

    def fontes(self, termo):
        return self.filter(termo__pk=termo).exclude(noticia__fonte='').values('noticia__fonte'). \
            annotate(Count('noticia__fonte')).order_by('noticia__fonte')
