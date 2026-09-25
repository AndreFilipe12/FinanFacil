from django.contrib import admin
from .models import Transacao


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = (
        'tipo',
        'descricao',
        'valor',
        'data',
    )

    list_filter = (
        'tipo',
        'data',
    )

    search_fields = (
        'descricao',
    )