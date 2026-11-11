from django.utils.functional import SimpleLazyObject

from core.models import LanguageModel


def languages(request):
    language_code = request.session.get("language")
    languages = SimpleLazyObject(lambda: list(LanguageModel.objects.all()))

    def get_current_language():
        return next(
            (language for language in languages if language.code == language_code),
            None,
        )

    current_language = SimpleLazyObject(get_current_language)

    context = {"languages": languages, "current_language": current_language}
    return context
