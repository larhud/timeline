# coding: utf-8
from collections import Counter

from django import template
from django.contrib.admin.views.main import PAGE_VAR

from powercms.cms.models import Section, Article, ArticleComment, Recurso, ArticleAttribute

from django.conf import settings
import re


register = template.Library()


@register.simple_tag(takes_context=True)
def get_section(context, slug):
    try:
        section = Section.objects.get(slug=slug)
        if section.have_perm(context.get('request').user):
            return section
    except Section.DoesNotExist: pass
    return None


@register.simple_tag(takes_context=True)
def get_article(context, slug):
    try:
        article = Article.objects.get(slug=slug)
        if article.have_perm(context.get('request').user):
            return article
    except Article.DoesNotExist: pass

    return None


# Retorna os atributos de um determinado artigo
@register.simple_tag(takes_context=True)
def get_article_attributes(context, slug, key=None):
    if key:
        return ArticleAttribute.objects.filter(article__slug=slug, attrib=key, active=True)
    else:
        return ArticleAttribute.objects.filter(article__slug=slug, active=True)


@register.simple_tag(takes_context=True)
def get_section_articles(context, slug, num=5):
    articles = []
    try:
        section = Section.objects.get(slug=slug)
        for article in section.get_articles():
            if article.have_perm(context.get('request').user):
                articles.append(article)
            if len(articles) == num: break
        return articles
    except Section.DoesNotExist:
        return []


@register.simple_tag(takes_context=True)
def get_last_comments(context, num=5):
    return ArticleComment.objects.filter(active=True).order_by('-created_at')[:num]


@register.simple_tag(takes_context=True)
def get_sections(context):
    sections = []
    for section in Section.objects.exclude(order=0):
        if section.have_perm(context.get('request').user) and section.num_articles() > 0:
            sections.append(section)
    return sections


@register.simple_tag(takes_context=True)
def get_last_articles(context, num=10):
    articles = []
    for article in Article.objects.filter(is_active=True).order_by('sectionitem__order', '-created_at', '-pk')[:num]:
        if article.have_perm(context.get('request').user):
            articles.append(article)
    return articles


@register.simple_tag
def site_name():
    try:
        return Recurso.objects.get(recurso='SITE_NAME').valor
    except Recurso.DoesNotExist:
        return settings.SITE_NAME


@register.simple_tag
def site_setting(parameter):
    try:
        if settings.SITE_TYPE == parameter:
            return True
    except:
        return None


@register.simple_tag
def facebook_app_id():
    try:
        return Recurso.objects.get(recurso='FACEBOOK').valor
    except Recurso.DoesNotExist:
        return '507957735984728'


@register.simple_tag(takes_context=True)
def get_cloudtags(context):
    try:
        content_words_fixa = Recurso.objects.get(recurso='TAGS-FIXA').valor.split(u',')
        content_words_fixa_counter = Counter(content_words_fixa).most_common(30)
        content_words_tags = dict(eval(Recurso.objects.get(recurso='TAGS').valor)).items()
        for word in content_words_tags:
            if (len(content_words_fixa_counter) < 30):
                content_words_fixa_counter.append(word)
        return content_words_fixa_counter
        #return dict(eval(Recurso.objects.get(recurso='TAGS').valor)).items()
    except:
        return dict(eval(Recurso.objects.get(recurso='TAGS').valor)).items()


@register.simple_tag
def get_signup():
    try:
        return Recurso.objects.get(recurso='SIGNUP').ativo
    except Recurso.DoesNotExist:
        return False


@register.simple_tag
def update_variable(value):
    """Allows to update existing variable in template"""
    return False


@register.filter(name='times')
def times(number):
    return range(number)


@register.simple_tag
def version():
    return settings.VERSION


@register.simple_tag
def comment_title(article):
    if article.allow_comments == 'P':
        try:
            return Recurso.objects.get(recurso='COMMENT_P').valor
        except Recurso.DoesNotExist: return u'Faça um contato conosco'
    else:
        try:
            return Recurso.objects.get(recurso='COMMENT').valor
        except Recurso.DoesNotExist: return u'Adicione um comentário'


@register.simple_tag
def og_title(article):
    return article.og_title if article.og_title else article.title


@register.simple_tag
def og_image(article):
    if article.og_image:
        return u'%s%s' % (settings.SITE_HOST, article.og_image.url)
    elif article.first_image():
        if 'http' in article.first_image():
            return article.first_image()
        return u'%s%s' % (settings.SITE_HOST, article.first_image())
    try:
        return Recurso.objects.get(recurso='OG-IMAGE').valor
    except Recurso.DoesNotExist:
        return '%s/static/public/images/facebook_padrao.png' % settings.SITE_HOST

@register.simple_tag
def default_og_image():
    try:
        return Recurso.objects.get(recurso='OG-IMAGE').valor
    except Recurso.DoesNotExist:
        return '%s/static/public/images/facebook_padrao.png' % settings.SITE_HOST


@register.simple_tag(takes_context=True)
def get_items(context, section, query_param):
    request = context.get('request')
    query = request.GET.get(query_param)

    if section.link:
        raw_items = section.get_link_items(query=query)
        items = []
        for item in raw_items:
            items.append({
                'is_dataset': True,
                'url': item.get('url'),
                'title': item.get('descricao'),
            })
    else:
        raw_items = section.get_articles(query=query)
        items = []
        for item in raw_items:
            items.append({
                'is_dataset': False,
                'url': item.get_absolute_url(),
                'title': item.title,
            })

    return items


@register.tag(name='cleanwhitespace')
def do_cleanwhitespace(parser, token):
    nodelist = parser.parse(('endcleanwhitespace',))
    parser.delete_first_token()
    return CleanWhitespaceNode(nodelist)


class CleanWhitespaceNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        output = self.nodelist.render(context)
        output = re.sub(r'\n[\s\t]*(?=\n)', '', output)
        output = re.sub(r'[\s\t]{2,}', '', output)
        output = output.strip()
        return output

@register.simple_tag(takes_context=True)
def page_parameters(context, pagenum, page_var=None):
    """Retorna a url com o número página mantendo os outros parâmetros do request"""
    if page_var is None:
        page_var = PAGE_VAR

    params = context['request'].GET.copy()
    params[page_var] = pagenum

    return '?%s' % params.urlencode()