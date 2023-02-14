from .models import SubRubric

def avito_context_processor(request):
    """Обработчик контекста, добавляющий в контекс шаблона rubrics.
    Можно было создавать в каждом контроллере переменную rubrics,
    но это тудоемко."""
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    return context