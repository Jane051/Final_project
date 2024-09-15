from django.views.generic import TemplateView, DetailView, ListView
from viewer.models import Television


class BaseView(TemplateView):
    template_name = 'home.html'
    extra_context = {}


class IndexView(TemplateView):
    template_name = 'index.html'
    extra_context = {}


class TVListView(ListView):
    template_name = 'tv_list.html'
    model = Television


class TVDetailView(DetailView):
    template_name = 'tv_detail.html'
    model = Television

