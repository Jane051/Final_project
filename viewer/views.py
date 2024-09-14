from django.views.generic import TemplateView


class BaseView(TemplateView):
    template_name = 'index.html'
    extra_context = {}
