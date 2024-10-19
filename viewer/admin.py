from django.contrib import admin
from .models import Television, Brand, TVDisplayResolution, TVDisplayTechnology, TVOperationSystem, MobilePhone

# Pokus o registraci modelů s ošetřením výjimky
try:
    admin.site.register(Television)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(Brand)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(TVDisplayResolution)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(TVDisplayTechnology)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(TVOperationSystem)
except admin.sites.AlreadyRegistered:
    pass

try:
    admin.site.register(MobilePhone)
except admin.sites.AlreadyRegistered:
    pass
