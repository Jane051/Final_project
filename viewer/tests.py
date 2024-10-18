#pip install selenium
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
import time

class MySeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()  # Ujisti se, že máš správnou cestu k ChromeDriver
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Vytvoření admin uživatele pro test
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin',
            email='admin@admin.com'
        )

    def test_signup(self):
        # Přístup na stránku registrace
        self.selenium.get(f'{self.live_server_url}/signup/')

        # Nalezení vstupních polí a vyplnění registrace
        username_input = self.selenium.find_element(By.NAME, "username")
        first_name_input = self.selenium.find_element(By.NAME, "first_name")
        last_name_input = self.selenium.find_element(By.NAME, "last_name")
        email_input = self.selenium.find_element(By.NAME, "email")
        password1_input = self.selenium.find_element(By.NAME, "password1")
        password2_input = self.selenium.find_element(By.NAME, "password2")

        username_input.send_keys('testuser')
        first_name_input.send_keys('Test')
        last_name_input.send_keys('User')
        email_input.send_keys('testuser@example.com')
        password1_input.send_keys('testpassword123')
        password2_input.send_keys('testpassword123')

        # Odeslání formuláře
        self.selenium.find_element(By.XPATH, '//button[text()="Registrovat"]').click()

        # Ověření přesměrování na domovskou stránku
        time.sleep(2)  # Čekání na načtení stránky
        self.assertEqual(self.selenium.current_url, f'{self.live_server_url}/')

        # Ověření, že se zobrazuje správný text po registraci
        self.assertIn("Welcome to Online shop", self.selenium.page_source)
def test_login(self):
    # Přístup na stránku přihlášení
    self.selenium.get(f'{self.live_server_url}/login/')

    # Vyplnění vstupních polí pro uživatelské jméno a heslo
    username_input = self.selenium.find_element(By.NAME, "username")
    password_input = self.selenium.find_element(By.NAME, "password")
    username_input.send_keys('admin')
    password_input.send_keys('admin')

    # Odeslání formuláře
    self.selenium.find_element(By.XPATH, '//input[@type="submit"]').click()

    # Čekání na načtení stránky
    time.sleep(5)

    # Ověření, že jsme na domovské stránce
    self.assertEqual(self.selenium.current_url, f'{self.live_server_url}/')

    # Ověření, že se zobrazuje správný text pro přihlášeného uživatele
    self.assertIn("Welcome to Online shop", self.selenium.page_source)

    # Ověření, že se zobrazuje sekce „Sklad“
    self.assertIn("Sklad", self.selenium.page_source)  # Ověření, že sekce Sklad je přítomna

    # Místo kontroly přesného HTML jsem použila text pro snížení chybovosti.
    self.assertIn("Sklad", self.selenium.page_source)




from django.test import TestCase


class BrandModelTest(TestCase):
    def test_create_brand(self):
        brand = Brand.objects.create(brand_name="Samsung")
        self.assertEqual(str(brand), "Samsung")
        # Základní test na vytvoření Brand



from django.test import TestCase
from viewer.models import Television, Brand, TVDisplayTechnology, TVDisplayResolution, TVOperationSystem, Category

class TelevisionModelTest(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(brand_name="LG")
        self.display_technology = TVDisplayTechnology.objects.create(name="LED")
        self.display_resolution = TVDisplayResolution.objects.create(name="4K")
        self.operation_system = TVOperationSystem.objects.create(name="WebOS")
        self.category = Category.objects.create(name="Smart TV")

    def test_create_television(self):
        tv = Television.objects.create(
            brand=self.brand,
            brand_model="LG OLED55CX",
            tv_released_year=2022,
            tv_screen_size=55,
            smart_tv=True,
            refresh_rate=120,
            display_technology=self.display_technology,
            display_resolution=self.display_resolution,
            operation_system=self.operation_system,
            price=1299.99
        )
        tv.categories.add(self.category)
        self.assertEqual(str(tv), 'LG -  LG OLED55CX - 55"')
        self.assertEqual(tv.tv_released_year, 2022)
        self.assertTrue(tv.smart_tv)
        self.assertEqual(tv.categories.count(), 1)
        self.assertEqual(tv.categories.first().name, "Smart TV")

        # Testuje vytvoření televize, validace roku a vztahy s ostatními modely


