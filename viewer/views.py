import logging
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
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


class TVUpdateView(UpdateView):
    template_name = 'tv_creation.html'
    model = Television
    form_class = TVForm
    success_url = reverse_lazy('tv_list')

    def form_invalid(self, form):
        logger.warning('User provided invalid data while updating a movie.')
        return super().form_invalid(form)


class TVDeleteView(DeleteView):
    template_name = 'tv_delete.html'
    model = Television
    success_url = reverse_lazy('tv_list')


class FilteredTelevisionListView(ListView):
    model = Television
    template_name = 'tv_list_filter.html'
    context_object_name = 'televisions'  # Název kontextu v šabloně

    def get_queryset(self):
        queryset = Television.objects.all()  # Základní queryset se všemi televizemi

        smart_tv = self.kwargs.get('smart_tv')
        if smart_tv == 'smart':
            queryset = queryset.filter(smart_tv=True)
        elif smart_tv == 'non-smart':
            queryset = queryset.filter(smart_tv=False)

        # Filtrovaní podle značky (brand_name)
        brand = self.kwargs.get('brand')
        if brand:
            queryset = queryset.filter(brand_name__name=brand)  # brand_name je ForeignKey na model Brand

        # Filtrovaní podle technologie (display_technology)
        technology = self.kwargs.get('technology')
        if technology:
            queryset = queryset.filter(
                display_technology__name=technology)  # display_technology je ForeignKey na model TVDisplayTechnology

        # Filtrovaní podle velikosti obrazovky (tv_screen_size)
        screen_size = self.kwargs.get('screen_size')
        if screen_size:
            queryset = queryset.filter(tv_screen_size=screen_size)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Přidej aktuální filtry do kontextu (např. pro zobrazení v šabloně)
        context['selected_smart'] = self.kwargs.get('smart', 'All')
        context['selected_brand'] = self.kwargs.get('brand', 'All')
        context['selected_technology'] = self.kwargs.get('technology', 'All')
        context['selected_screen_size'] = self.kwargs.get('screen_size', 'All')
        return context


