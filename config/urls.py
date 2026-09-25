from django.contrib import admin
from django.urls import path
from financeiro.views import home, nova_transacao, relatorios

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('nova-transacao/', nova_transacao, name='nova_transacao'),
    path('relatorios/', relatorios, name='relatorios'),
]