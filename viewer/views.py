import logging

from django.http import Http404
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from viewer.models import Television, MobilePhone, Order, Profile
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from viewer.forms import TVForm, CustomAuthenticationForm, CustomPasswordChangeForm, ProfileForm, SignUpForm, OrderForm
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile_detail.html'

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(), 'object': self.request.user}


class SubmittableLoginView(LoginView):
    template_name = 'login_form.html'
    form_class = CustomAuthenticationForm
    next_page = reverse_lazy('home')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class SubmittablePasswordChangeView(PasswordChangeView):
    template_name = 'password_change_form.html'
    success_url = reverse_lazy('profile_detail')
    form_class = CustomPasswordChangeForm


class BaseView(TemplateView):
    template_name = 'home.html'
    extra_context = {}


class TVListView(ListView):
    template_name = 'tv_list.html'
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
    template_name = 'tv_detail.html'
    model = Television

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Kontrola, zda uživatel patří do skupiny 'tv_admin', pokud je přihlášen (pro podminkovani v html)
        context['is_tv_admin'] = user.groups.filter(name='tv_admin').exists()
        return context


class TVCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'tv_creation.html'
    form_class = TVForm
    success_url = reverse_lazy('tv_list')

    def test_func(self):
        # Umožní přístup pouze členům skupiny 'tv_admin' nebo superuživatelům
        return self.request.user.is_superuser or self.request.user.groups.filter(name='tv_admin').exists()

    def form_invalid(self, form):
        logger.warning('User provided invalid data.')
        return super().form_invalid(form)


class TVUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'tv_creation.html'
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
    template_name = 'tv_delete.html'
    model = Television
    success_url = reverse_lazy('tv_list')

    def test_func(self):
        # Umožní přístup pouze členům skupiny 'tv_admin' nebo superuživatelům
        return self.request.user.is_superuser or self.request.user.groups.filter(name='tv_admin').exists()


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
        elif smart_tv not in ('smart', 'non-smart', None):
            raise Http404

        # Filtrovaní podle rozliseni(display_resolution)
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

    return render(request, 'edit_profile.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


class MobileListView(ListView):
    template_name = 'mobile_list.html'
    model = MobilePhone
    context_object_name = 'object_list'  # Kontext pro šablonu


class CreateOrderView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'order/create_order.html'

    def get_televison(self):
        # Získání televize podle ID předaného v URL
        return get_object_or_404(Television, pk=self.kwargs['television_id'])

    def get_form_kwargs(self):
        # Přidání uživatele do formuláře
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Neuložíme ještě formulář (commit=False) a upravíme některé jeho hodnoty
        television = self.get_televison()
        order = form.save(commit=False)
        order.user = self.request.user
        order.television = television
        order.status = 'submitted'
        order.save()

        # Po úspěšném uložení přesměrujeme na stránku úspěchu
        return redirect('order_success', order_id=order.order_id)

    def get_context_data(self, **kwargs):
        # Přidáme motorku do kontextu pro použití v šabloně
        context = super().get_context_data(**kwargs)
        context['television'] = self.get_televison()
        return context


class OrderSuccessView(DetailView):
    model = Order
    template_name = 'order/order_success.html'
    context_object_name = 'order'

    def get_object(self):
        # Získáme objednávku podle order_id předaného v URL
        return get_object_or_404(Order, order_id=self.kwargs['order_id'])


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Zobrazí pouze objednávky aktuálně přihlášeného uživatele
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order/order_detail.html'
    context_object_name = 'order'

    def get_object(self):
        # Získáme objednávku podle order_id předaného v URL
        return get_object_or_404(Order, order_id=self.kwargs['order_id'])


class AddToCartView(View):
    def get(self, request, television_id):
        # Získáme televizi podle ID
        television = get_object_or_404(Television, id=television_id)

        # Inicializujeme košík, pokud ještě neexistuje
        cart = request.session.get('cart', {})

        # v teto casti to bez prevedeni na str nenavysovalo pocet v kosiku
        # protoze "V session (která je založena na JSON-u), klíče jsou obvykle řetězce..."
        if str(television_id) in cart:
            cart[str(television_id)]['quantity'] += 1
        else:
            cart[television_id] = {'name': television.brand.brand_name,
                                   'model': television.brand_model,
                                   'price': str(television.price),
                                   'quantity': 1}

        # Uložíme košík do session
        request.session['cart'] = cart

        # Kontrola, zda přidáváme z košíku nebo ze stránky televize
        if 'from_cart' in request.GET:
            return redirect('view_cart')  # Přesměrování zpět na stránku košíku
        else:
            return redirect('tv_detail', pk=television_id)  # Přesměrování zpět na stránku televize


class RemoveFromCartView(View):
    def post(self, request, television_id):
        # Získání košíku ze session
        cart = request.session.get('cart', {})

        # Pokud existuje položka v košíku, snižte její množství
        if str(television_id) in cart:
            if cart[str(television_id)]['quantity'] > 1:
                cart[str(television_id)]['quantity'] -= 1
            else:
                # Pokud je množství 1, odstraňte položku z košíku
                del cart[str(television_id)]

        # Uložíme košík do session
        request.session['cart'] = cart

        # Přesměrujeme zpět na stránku košíku
        return redirect('view_cart')


class CartView(View):
    template_name = 'order/cart.html'

    def get(self, request):
        # Získání košíku ze session
        cart = request.session.get('cart', {})

        # Výpočet celkové ceny a počtu položek
        total_price = sum(float(item['price']) * int(item['quantity']) for item in cart.values())
        total_items = sum(int(item['quantity']) for item in cart.values())

        return render(request, self.template_name, {
            'cart': cart,
            'total_price': total_price,
            'total_items': total_items,
        })


# views.py
class CheckoutView(LoginRequiredMixin, View):
    template_name = 'order/checkout.html'

    def get(self, request):
        # Inicializace formuláře s údaji uživatele (pokud jsou dostupné)
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'address': request.user.profile.address if hasattr(request.user, 'profile') else '',
            'city': request.user.profile.city if hasattr(request.user, 'profile') else '',
            'zipcode': request.user.profile.zipcode if hasattr(request.user, 'profile') else '',
            'phone_number': request.user.profile.phone_number if hasattr(request.user, 'profile') else '',
        }
        # Předání uživatele do formuláře
        form = OrderForm(initial=initial_data, user=request.user)

        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # Předání uživatele do formuláře
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            # Vytvoření objednávky
            order = form.save(commit=False)
            # Nejprve přiřadíme uživatele
            order.user = request.user
            print(f"Order User after assignment: {order.user}")

            # Přidání položek z košíku do objednávky
            cart = request.session.get('cart', {})
            for television_id in cart:
                television = Television.objects.get(id=television_id)
                order.television.add(television)

            order.status = 'submitted'
            order.save()

            # Vyčištění košíku
            request.session['cart'] = {}

            # Přesměrování na úspěšnou objednávku
            return redirect('order_success', order_id=order.order_id)

        return render(request, self.template_name, {'form': form})
