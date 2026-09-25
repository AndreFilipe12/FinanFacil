from django.shortcuts import render, redirect
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from .forms import TransacaoForm
from .models import Transacao


def home(request):

    receitas = Transacao.objects.filter(
        tipo='receita'
    ).aggregate(
        total=Sum('valor')
    )['total'] or 0

    despesas = Transacao.objects.filter(
        tipo='despesa'
    ).aggregate(
        total=Sum('valor')
    )['total'] or 0

    saldo = receitas - despesas

    dados_grafico_queryset = (
        Transacao.objects
        .values('tipo')
        .annotate(
            mes=TruncMonth('data'),
            total=Sum('valor')
        )
        .order_by('mes')
    )

    dados_grafico = []

    for item in dados_grafico_queryset:
        dados_grafico.append({
            'mes': item['mes'].strftime('%m/%Y'),
            'tipo': item['tipo'],
            'total': float(item['total']),
        })

    transacoes = Transacao.objects.order_by(
        '-data',
        '-id'
    )[:10]

    contexto = {
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo,
        'transacoes': transacoes,
        'dados_grafico': dados_grafico,
    }

    return render(
        request,
        'home.html',
        contexto
    )


def nova_transacao(request):

    if request.method == 'POST':
        form = TransacaoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')

    else:
        form = TransacaoForm()

    return render(
        request,
        'nova_transacao.html',
        {'form': form}
    )


def relatorios(request):

    return render(
        request,
        'relatorios.html'
    )