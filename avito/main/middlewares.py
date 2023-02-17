from .models import SubRubric

def avito_context_processor(request):
    """Обработчик контекста, добавляющий в контекс шаблона rubrics,
    keyword, page. All нам понадобится для гиперссылок.
    """
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    context['keyword'] = ''
    context['all'] = ''
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context['keyword']
    if 'page' in request.GET:
        page = request.GET['page']
        if page != 1:
            if context['all']:
                context['all'] += '&page=' + page
            else:
                context['all'] += '?page=' + page

    return context