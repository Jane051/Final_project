import logging
from django.views.generic import TemplateView, DetailView, ListView, CreateView
from viewer.models import Television
from django.urls import reverse_lazy
from viewer.forms import TVForm

logger = logging.getLogger(__name__)


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


class TVCreateView(CreateView):
    template_name = 'tv_creation.html'
    form_class = TVForm
    success_url = reverse_lazy('tv_list')

    def form_invalid(self, form):
        logger.warning('User provided invalid data.')
        return super().form_invalid(form)

