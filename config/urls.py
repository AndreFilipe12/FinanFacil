from django.contrib import admin
from django.urls import path

from financeiro.views import (
    home,
    nova_transacao,
    relatorios,
    transacoes,
    analises,
    editar_transacao,
    excluir_transacao
)


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        '',
        home,
        name='home'
    ),

    path(
        'nova-transacao/',
        nova_transacao,
        name='nova_transacao'
    ),

    path(
        'transacoes/',
        transacoes,
        name='transacoes'
    ),

    path(
        'transacoes/editar/<int:id>/',
        editar_transacao,
        name='editar_transacao'
    ),

    path(
        'transacoes/excluir/<int:id>/',
        excluir_transacao,
        name='excluir_transacao'
    ),

    path(
        'relatorios/',
        relatorios,
        name='relatorios'
    ),

path(
    'analises/',
    analises,
    name='analises'
),

]