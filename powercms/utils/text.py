# -*- coding: utf-8 -*-
import html
import string
from collections import Counter

from django.utils.html import strip_tags


class Format:
    """
        Classe utilizada para formatação e "limpeza" de textos.
        Como exemplo remoção de caracteres seja de pontuação ou especificados nos parâmetros.
    """
    @staticmethod
    def remove_characteres(text, list_characteres, sep=''):
        """
        Args:
            text (str): Texto.
            list_characteres (list): Lista com caracteres a serem removidos.
            sep (''): Marca a substituir os caracteres.
        Returns:
            str
        """
        text_formated = ''
        for c in list_characteres:
            text_formated = text.replace(c, sep)

        return text_formated.replace('(', ' ').replace(')', ' ').replace('/', ' ')

    @staticmethod
    def remove_punctuation(text, sep=''):
        """
        Args:
            text (str): Texto.
            sep (''): Marca a substituir os caracteres.
        Returns:
            str
        """
        text_formated = ''
        for p in [p for p in string.punctuation]:
            text_formated = text.replace(p, sep)

        return text_formated

    @staticmethod
    def remove_tag(text):
        """
        Args:
            text (str): Texto.
        Returns:
            str
        """
        return '%s' % html.unescape(strip_tags(text))


class Map:
    """
        Classe utilizada para mapeamento de texto ou listas
    """
    @staticmethod
    def make_phrases(text):
        """
        Args:
            text (str): Texto.
        Returns:
            list
        """
        sep = '.'
        _phrases = text.replace('!', sep).replace('?', sep).replace(u':', sep).replace(u';', sep).split(sep)
        phrases = []
        for p in _phrases:
            phrases += p.split(u',')

        return Map.words_length(phrases)  # remove conteudos sem palavras

    @staticmethod
    def vocabulary_list(list_phrases, exclude_words, minimun_size=3):
        """
        Args:
            list_phrases (list): Lista de frases.
            exclude_words (list): Lista de palavras a serem excluidas.
            minimun_size (int): Tamanho minino de palavras a serem desconsiderada.
        Returns:
            tuple(list, list)
        """
        double_words = []
        simple_words = []
        for phrases in list_phrases:
            flag_last = False
            words = phrases.split(u' ')
            last_word = words[-1]
            for w in words:
                if w != last_word:
                    if w not in exclude_words and len(w) > minimun_size:
                        simple_words.append(w)  # Palavra simples
                        next_w = words[words.index(w) + 1]
                        if next_w not in exclude_words and len(next_w) > minimun_size:
                            double_words.append("%s %s" % (w, next_w))
                            simple_words.remove(w)  # Formou uma palavra composta
                            flag_last = (next_w == last_word)

            if flag_last and last_word in simple_words:
                simple_words.remove(last_word)  # formou palavra composta

        return simple_words, double_words

    @staticmethod
    def words_length(list_words, length=3, bigger=True):
        """Cria uma lista somente com palavras com tamanho maior ou menor
            que length.
        Args:
            list_words (list): Lista de frases.
            length (int): Tamanho limite de uma palavra para.
            bigger (bool): True - word > length. False - word < length.
        Returns:
            list
        """
        if bigger:
            return [word for word in list_words if len(word) > length]
        else:
            return [word for word in list_words if len(word) < length]


class Computation:
    """
        Classe que manipula estatistica e frequência de palavras numa lista
        de frases e de frequência.
    """
    @staticmethod
    def frequently(list_words, quantity=None, list_ignore=[]):
        """Cria uma lista com as palavras mais frequentes
        Args:
            list_words (list): Lista de frases.
            quantity (int): Quantidades de palavras a serem recuperadas.
            list_ignore (list): Lista de palavras a serem desconsideradas.
        Returns:
            list
        """
        if quantity:
            fq = Counter(list_words).most_common(quantity)
        else:
            fq = Counter(list_words).most_common()

        if list_ignore:
            for lw in list_words:
                if lw[0] in list_ignore:
                    if not fq:
                        fq.append(lw)
                    else:
                        for f in fq:
                            if lw[0] not in f:
                                fq.append(lw)
        return fq

    @staticmethod
    def more_less_frequently(list_words, cut_frequently, list_ignore=[], more=True):
        """Com lista de Counter(de palavras) filtrar as de maiores ou menores frequências.
        Args:
            list_words (list(Counter)): Lista de frases.
            cut_frequently (int): Frequencia de corte.
            list_ignore (list): Lista de palavras a serem desconsideradas.
            more (bool): True - frequencia >= cut_frequently. False - frequência <= cut_frequently.
        Returns:
            list
        """
        more_less = []
        if more:
            more_less = [w[0] for w in list_words if w[1] >= cut_frequently]
        else:
            more_less = [w[0] for w in list_words if w[1] <= cut_frequently]

        for lw in list_words:
            if lw[0] in list_ignore:
                if not more_less:
                    more_less.append(lw[0])
                else:
                    for mf in more_less:
                        if lw[0] not in mf:
                            more_less.append(lw[0])

        return more_less
