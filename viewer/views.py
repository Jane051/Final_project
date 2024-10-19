import logging

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView, FormView, View

from viewer.forms import (TVForm, CustomAuthenticationForm, CustomPasswordChangeForm, ProfileForm, SignUpForm,
                          OrderForm, BrandForm, ItemOnStockForm)
from viewer.models import Television, MobilePhone, ItemsOnStock, Order, Profile

logger = logging.getLogger(__name__)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user/profile_detail.html'

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(), 'object': self.request.user}


class SubmittableLoginView(LoginView):
    template_name = 'user/login_form.html'
    form_class = CustomAuthenticationForm
    next_page = reverse_lazy('home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class SubmittablePasswordChangeView(PasswordChangeView):
    template_name = 'user/password_change_form.html'
    success_url = reverse_lazy('profile_detail')
    form_class = CustomPasswordChangeForm


class BaseView(TemplateView):
    template_name = 'home.html'
    extra_context = {}


class SearchResultsView(ListView):
    template_name = 'search_results.html'
    model = Television
    context_object_name = 'search_results'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Television.objects.filter(
                Q(brand__brand_name__icontains=query) |  # Vyhledávání podle Brand name
                Q(display_technology__name__icontains=query) | # Vyhledávání podle Display technology
                Q(brand_model__icontains=query) # Vyhledávání podle Brand model
            )
        return Television.objects.none()  # Vrací prázdný queryset pokud není žádný k dispozici


class BrandCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'television/brand_create.html'
    form_class = BrandForm
    success_url = reverse_lazy('tv_create')

    def test_func(self):
        # Umožní přístup pouze členům skupiny 'tv_admin' nebo superuživatelům
        return self.request.user.is_superuser or self.request.user.groups.filter(name='tv_admin').exists()

    def form_invalid(self, form):
        logger.warning('User provided invalid data.')
        return super().form_invalid(form)


class TVListView(ListView):
    template_name = 'television/tv_list.html'
    model = Television
    context_object_name = 'object_list'  # Kontext pro šablonu

    def get_queryset(self):
        # Získání všech televizí
        queryset = Television.objects.all()

        # Filtrování podle značek
        selected_brand = self.request.GET.getlist('brand')
        if selected_brand:
            queryset = queryset.filter(brand__brand_name__in=selected_brand)

        # Filtrování podle technologie
        selected_technology = self.request.GET.getlist('technology')
        if selected_technology:
            queryset = queryset.filter(display_technology__name__in=selected_technology)

        # Filtrování podle rozliseni displeje
        selected_resolution = self.request.GET.getlist('resolution')
        if selected_resolution:
            queryset = queryset.filter(display_resolution__name__in=selected_resolution)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Kontrola, zda uživatel patří do skupiny 'tv_admin', pokud je přihlášen (pro podminkovani v html)
        context['is_tv_admin'] = user.groups.filter(name='tv_admin').exists()
        context['selected_brand'] = self.request.GET.getlist('brand')
        context['selected_technology'] = self.request.GET.getlist('technology')
        context['selected_resolution'] = self.request.GET.getlist('resolution')
        return context


class TVDetailView(DetailView):
    template_name = 'television/tv_detail.html'
    model = Television

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        """Kontrola, zda uživatel patří do skupiny 'tv_admin', pokud je přihlášen (pro podminkovani v html)"""
        context['is_tv_admin'] = user.groups.filter(name='tv_admin').exists()

        """Načtení zásob spojených s konkrétní televizí"""
        television = self.get_object()  # Získáme aktuální instanci Television
        """First zde mám, abych nemusel pracovat s QuerySetem"""
        item_on_stock = ItemsOnStock.objects.filter(television_id=television).first()
        context['item_on_stock'] = item_on_stock
        return context


class TVCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'television/tv_creation.html'
    form_class = TVForm
    success_url = reverse_lazy('tv_list')

    def test_func(self):
        # Umožní přístup pouze členům skupiny 'tv_admin' nebo superuživatelům
        return self.request.user.is_superuser or self.request.user.groups.filter(name='tv_admin').exists()

    def form_invalid(self, form):
        logger.warning('User provided invalid data.')
        return super().form_invalid(form)


class TVUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'television/tv_creation.html'
    model = Television
    form_class = TVForm
    success_url = reverse_lazy('tv_list')

    def test_func(self):
        # Umožní přístup pouze členům skupiny 'tv_admin' nebo superuživatelům
        return self.request.user.is_superuser or self.request.user.groups.filter(name='tv_admin').exists()

    def form_invalid(self, form):
        logger.warning('User provided invalid data while updating a movie.')
        return super().form_invalid(form)


class TVDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'television/tv_delete.html'
    model = Television
    success_url = reverse_lazy('tv_list')

    def test_func(self):
        """"Umožní přístup pouze členům skupiny 'tv_admin' nebo superuživatelům"""
        return self.request.user.is_superuser or self.request.user.groups.filter(name='tv_admin').exists()


class FilteredTelevisionListView(ListView):
    model = Television
    template_name = 'television/tv_list_filter.html'
    context_object_name = 'televisions'

    def get_queryset(self):
        queryset = Television.objects.all()  # Základní queryset se všemi televizemi

        smart_tv = self.kwargs.get('smart_tv')
        if smart_tv == 'smart':
            queryset = queryset.filter(smart_tv=True)
        elif smart_tv == 'non-smart':
            queryset = queryset.filter(smart_tv=False)
        elif smart_tv not in ('smart', 'non-smart', None):
            raise Http404

        """"Filtrovaní podle rozliseni(display_resolution)"""
        resolution = self.kwargs.get('resolution')
        if resolution:
            queryset = queryset.filter(
                display_resolution__name=resolution)  # display_resolution je ForeignKey na model TV display resolution

        # Filtrovaní podle technologie (display_technology)
        technology = self.kwargs.get('technology')
        if technology:
            queryset = queryset.filter(
                display_technology__name=technology)  # display_technology je ForeignKey na model TVDisplayTechnology

        # Filtrovaní podle operacniho systemu
        op_system = self.kwargs.get('op_system')
        if op_system:
            queryset = queryset.filter(operation_system__name=op_system)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Přidej aktuální filtry do kontextu (např. pro zobrazení v šabloně)
        context['selected_smart'] = self.kwargs.get('smart', 'All')
        context['selected_resolution'] = self.kwargs.get('resolution', 'All')
        context['selected_technology'] = self.kwargs.get('technology', 'All')
        context['selected_op_system'] = self.kwargs.get('op_system', 'All')
        return context


class ItemOnStockListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = ItemsOnStock
    template_name = 'stock/stock_list.html'
    context_object_name = 'items'

    def test_func(self):
        """"Umožní přístup pouze členům skupiny 'stock_admin' nebo superuživatelům"""
        return self.request.user.is_superuser or self.request.user.groups.filter(name='stock_admin').exists()


class ItemOnStockCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ItemsOnStock
    template_name = 'stock/item_on_stock_create_update.html'
    form_class = ItemOnStockForm
    success_url = reverse_lazy('stock_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='stock_admin').exists()

    """Zamezení duplicit je pořešeno na úrovni databáze, zde"""

    def form_invalid(self, form):
        # Přidání logu při neplatném formuláři
        logger.warning('User provided invalid data.')
        # Vrátíme neplatný formulář (s chybami)
        return super().form_invalid(form)


class ItemOnStockUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'stock/item_on_stock_create_update.html'
    model = ItemsOnStock
    form_class = ItemOnStockForm
    success_url = reverse_lazy('stock_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='stock_admin').exists()


class ItemOnStockDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = 'stock/item_on_stock_delete.html'
    model = ItemsOnStock
    success_url = reverse_lazy('stock_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='stock_admin').exists()

@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'user/edit_profile.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'user/signup.html', {'form': form})


class MobileListView(ListView):
    template_name = 'mobile_list.html'
    model = MobilePhone
    context_object_name = 'object_list'



class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, television_id):
        # Ziskame televizi podle ID
        television = get_object_or_404(Television, id=television_id)

        # Ziskame  množství televize na sklade
        item_on_stock = get_object_or_404(ItemsOnStock, television_id=television_id)

        # Inicializujeme kosik, pokud jeste neexistuje
        cart = request.session.get('cart', {})

        # Kontrola, zda uz mame televizor v kosiku
        if str(television_id) in cart:
            current_quantity_in_cart = cart[str(television_id)]['quantity']

            # Kontrola, zda by pridanim dalsiho kusu nepresahl pocet na sklade
            if current_quantity_in_cart + 1 > item_on_stock.quantity:
                # Pokud by pridani dalsiho kusu překrocilo mnozstvi na sklade, zobrazíme chybovou zpravu
                messages.error(request, f'Nelze přidat více než {item_on_stock.quantity} ks do košíku.')
                return redirect('tv_detail', pk=television_id)

            # Pokud skladova zasoba umoznuje pridani, zvysime mnozstvi
            cart[str(television_id)]['quantity'] += 1

        else:
            # Pokud televizor jeste neni v kosiku, zkontrolujeme, zda je alespon 1 kus na sklade
            if item_on_stock.quantity < 1:
                # Neni nic na sklade, zobrazíme chybovou zprávu
                messages.error(request, 'Tento televizor není momentálně na skladě.')
                return redirect('tv_detail', pk=television_id)

            """Přidáme nový televizor do košíku s počátečním množstvím 1"""
            cart[str(television_id)] = {
                'name': television.brand.brand_name,
                'model': television.brand_model,
                'price': str(television.price),
                'quantity': 1
            }

        # Ulozime kosik do session
        request.session['cart'] = cart

        # Kontrola, zda pridavame z kosiku nebo ze stranky televize
        if 'from_cart' in request.GET:
            return redirect('view_cart')
        else:
            return redirect('tv_detail', pk=television_id)


class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, television_id):
        # Ziskani kosiku ze session
        cart = request.session.get('cart', {})

        # Pokud existuje polozka v kosiku, snizte jeji mnozstvi
        if str(television_id) in cart:
            if cart[str(television_id)]['quantity'] > 1:
                cart[str(television_id)]['quantity'] -= 1
            else:
                del cart[str(television_id)]

        # Ulozime kosik do session
        request.session['cart'] = cart
        return redirect('view_cart')


class CartView(LoginRequiredMixin, View):
    template_name = 'order/cart.html'

    def get(self, request):
        cart = request.session.get('cart', {})

        # Vypocet celkove ceny a poctu polozek
        total_price = sum(float(item['price']) * int(item['quantity']) for item in cart.values())
        total_items = sum(int(item['quantity']) for item in cart.values())

        return render(request, self.template_name, {
            'cart': cart,
            'total_price': total_price,
            'total_items': total_items,
        })


class CheckoutView(LoginRequiredMixin, FormView):
    template_name = 'order/checkout.html'
    form_class = OrderForm

    """Přesměrování, pokud je košík prázdný"""
    def dispatch(self, request, *args, **kwargs):
        cart = self.request.session.get('cart', {})
        if not cart:
            return redirect('view_cart')
        return super().dispatch(request, *args, **kwargs)

    """Úspěšné přesměrování po odeslání formuláře"""
    def get_success_url(self):
        return reverse('order_success', kwargs={'order_id': self.order.order_id})

    """
    Inicializace formuláře s údaji uživatele
    """
    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user

        initial.update({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.profile.address if hasattr(user, 'profile') else '',
            'city': user.profile.city if hasattr(user, 'profile') else '',
            'zipcode': user.profile.zipcode if hasattr(user, 'profile') else '',
            'phone_number': user.profile.phone_number if hasattr(user, 'profile') else '',
            })
        return initial

    """Předání uživatele do formuláře při jeho inicializaci"""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Předáme uživatele do formuláře
        return kwargs

    """Logika po úspěšném odeslání formuláře (zpracování objednávky)"""

    def form_valid(self, form):
        """ Vytvoření objednávky, ale zatím neuložíme """
        self.order = form.save(commit=False)
        self.order.user = self.request.user  # Priradime uzivatele k objednávce
        # Nejprve ulozime objednavku
        self.order.save()

        """ Zpracování položek z košíku """
        cart = self.request.session.get('cart', {})
        for television_id in cart:
            television = Television.objects.get(id=television_id)
            self.order.television.add(television)

        """Nastavení stavu objednávky"""
        self.order.status = 'submitted'
        self.order.save()

        """Vyčištění košíku"""
        self.request.session['cart'] = {}
        return super().form_valid(form)


class CreateOrderView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/create_order.html'

    def get_televison(self):
        # Ziskani televize podle ID predaného v URL
        return get_object_or_404(Television, pk=self.kwargs['television_id'])

    def get_form_kwargs(self):
        # Pridani uzivatele do formulare
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Neulozime jeste formular (commit=False) a upravime nektere jeho hodnoty
        television = self.get_televison()
        order = form.save(commit=False)
        order.user = self.request.user
        order.television = television
        order.status = 'submitted'
        order.save()
        return redirect('order_success', order_id=order.order_id)

    def get_context_data(self, **kwargs):
        # Pridame TV do kontextu pro pouziti v sablone
        context = super().get_context_data(**kwargs)
        context['television'] = self.get_televison()
        return context


class OrderSuccessView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order/order_success.html'
    context_object_name = 'order'

    def get_object(self):
        # Ziskame objednavku podle order_id predaneho v URL
        order = get_object_or_404(Order, order_id=self.kwargs['order_id'])

        # Overeni, zda je uzivatel vlastnikem objednávky nebo superuser
        if order.user != self.request.user and not self.request.user.is_superuser:
            # Pokud není, vyvoláme 404 chybu
            raise Http404("Nemáte oprávnění k zobrazení této objednávky.")
        return order


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Zobrazi pouze objednavky aktualne prihlaseneho uzivatele
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'

    def get_object(self):
        # Ziskame objednavku podle order_id predaneho v URL
        order = get_object_or_404(Order, order_id=self.kwargs['order_id'])

        # Overeni, zda je uzivatel vlastnikem objednavky
        if order.user != self.request.user:
            raise Http404("Nemáte oprávnění k zobrazení této objednávky.")
        return order

from django.shortcuts import render
from django.views.generic import TemplateView

def home(request):
    return render(request, 'home.html')


from django.shortcuts import render

def terms_view(request):
    return render(request, 'terms.html')

class TermsView(TemplateView):
    template_name = 'terms.html'

