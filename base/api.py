from django.http import JsonResponse
from base.models import Noticia
from django.conf import settings

def arquivoTM(request):
    query = request.GET.get('query')

    noticias = Noticia.objects.filter(texto__contains=query)

    results = {
        "serviceName": "Timeline Covid-19",
        "linkToService": "https://www.larhud.ibict.br/",
        "next_page": f"http://{settings.SITE_URL}arquivotm/?query={query}&offset={100}",
        "previous_page": f"http://{settings.SITE_URL}arquivotm/?q={query}&offset={0}",
        "estimated_nr_results": noticias.count(),
        "request_parameters": {
            "offset": 50,
            "dedupValue": 2,
            "dedupField": "site",
            "q": query,
            "maxItems": 50
        },
        "response_items": []
    }

    for item in noticias:
        results['response_items'].append(
            {
                "title": item.titulo,
                "originalURL": item.url,
                "linkToArchive": item.url,
                "tstamp": item.dt,
                "contentLength": 60161,
                "digest": item.url.__hash__(),
                "mimeType": "text/html",
                "encoding": "UTF-8",
                "date": "1327097234",
                "linkToScreenshot": item.media,
                "linkToNoFrame": "",
                "linkToExtractedText": f"{settings.SITE_URL}texto_completo/{item.id}",
                "linkToMetadata": "",
                "linkToOriginalFile": "",
                "snippet":  item.texto,
                "fileName": f"{settings.SITE_URL}media/pdf/{item.id}.pdf",
                "collection": "larhud",
                "offset": 73931448
            }
        )

#retornar o results em json
    return JsonResponse(results, safe=False)