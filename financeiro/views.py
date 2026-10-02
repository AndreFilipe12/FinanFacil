from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.db.models.functions import TruncMonth

import pandas as pd

from .models import Transacao
from .forms import TransacaoForm


def home(request):
    receitas = (
        Transacao.objects
        .filter(tipo='receita')
        .aggregate(total=Sum('valor'))['total'] or 0
    )

    despesas = (
        Transacao.objects
        .filter(tipo='despesa')
        .aggregate(total=Sum('valor'))['total'] or 0
    )

    saldo = receitas - despesas

    transacoes = Transacao.objects.order_by('-data', '-id')[:10]

    dados_grafico = []

    dados = (
        Transacao.objects
        .values('tipo')
        .annotate(
            mes=TruncMonth('data'),
            total=Sum('valor')
        )
        .order_by('mes')
    )

    for item in dados:
        dados_grafico.append({
            'mes': item['mes'].strftime('%Y-%m'),
            'tipo': item['tipo'],
            'total': float(item['total'])
        })

    return render(request, 'home.html', {
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo,
        'transacoes': transacoes,
        'dados_grafico': dados_grafico,
    })


def nova_transacao(request):
    if request.method == 'POST':
        form = TransacaoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TransacaoForm()

    return render(request, 'nova_transacao.html', {
        'form': form
    })


def relatorios(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    transacoes = Transacao.objects.all()

    if data_inicio:
        transacoes = transacoes.filter(data__gte=data_inicio)

    if data_fim:
        transacoes = transacoes.filter(data__lte=data_fim)

    receitas = (
        transacoes
        .filter(tipo='receita')
        .aggregate(total=Sum('valor'))['total'] or 0
    )

    despesas = (
        transacoes
        .filter(tipo='despesa')
        .aggregate(total=Sum('valor'))['total'] or 0
    )

    saldo = receitas - despesas

    dados_mensais = (
        transacoes
        .values('tipo')
        .annotate(
            mes=TruncMonth('data'),
            total=Sum('valor')
        )
        .order_by('mes')
    )

    meses = []
    receitas_mensais = []
    despesas_mensais = []

    for item in dados_mensais:
        mes = item['mes'].strftime('%Y-%m')

        if mes not in meses:
            meses.append(mes)
            receitas_mensais.append(0)
            despesas_mensais.append(0)

        indice = meses.index(mes)

        if item['tipo'] == 'receita':
            receitas_mensais[indice] = float(item['total'])
        elif item['tipo'] == 'despesa':
            despesas_mensais[indice] = float(item['total'])

    return render(request, 'relatorios.html', {
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'meses': meses,
        'receitas_mensais': receitas_mensais,
        'despesas_mensais': despesas_mensais,
    })


def analises(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    transacoes = Transacao.objects.all()

    if data_inicio:
        transacoes = transacoes.filter(data__gte=data_inicio)

    if data_fim:
        transacoes = transacoes.filter(data__lte=data_fim)

    dados = transacoes.values(
        'id',
        'tipo',
        'descricao',
        'valor',
        'data'
    )

    df = pd.DataFrame(list(dados))

    if df.empty:
        context = {
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'total_transacoes': 0,
            'total_receitas': 0,
            'total_despesas': 0,
            'media_despesas': 0,
            'maior_despesa': 0,
            'descricao_maior_despesa': '-',
            'percentual_despesas': 0,
            'top_despesas': [],
            'maior_gasto_diario': 0,
            'data_maior_gasto': None,
            'media_diaria': 0,
            'dias_com_despesas': 0,
            'tendencia_mensal': [],
            'variacao_receitas': 0,
            'variacao_despesas': 0,
        }

        return render(request, 'analises.html', context)

    df['valor'] = pd.to_numeric(df['valor'])

    total_transacoes = len(df)

    receitas = df[df['tipo'] == 'receita']
    despesas = df[df['tipo'] == 'despesa']

    total_receitas = receitas['valor'].sum()
    total_despesas = despesas['valor'].sum()

    if not despesas.empty:
        media_despesas = despesas['valor'].mean()

        maior_despesa = despesas['valor'].max()

        linha_maior_despesa = despesas.loc[
            despesas['valor'].idxmax()
        ]

        descricao_maior_despesa = linha_maior_despesa['descricao']
    else:
        media_despesas = 0
        maior_despesa = 0
        descricao_maior_despesa = '-'

    total_movimentado = total_receitas + total_despesas

    if total_movimentado > 0:
        percentual_despesas = (
            total_despesas / total_movimentado
        ) * 100
    else:
        percentual_despesas = 0

    top_despesas = (
        despesas
        .sort_values('valor', ascending=False)
        .head(5)
        .to_dict('records')
    )

    despesas_por_dia = (
        despesas
        .groupby('data')['valor']
        .sum()
    )

    if not despesas_por_dia.empty:
        maior_gasto_diario = despesas_por_dia.max()
        data_maior_gasto = despesas_por_dia.idxmax()
        media_diaria = despesas_por_dia.mean()
        dias_com_despesas = len(despesas_por_dia)
    else:
        maior_gasto_diario = 0
        data_maior_gasto = None
        media_diaria = 0
        dias_com_despesas = 0

    # Tendência mensal das despesas
    despesas_por_mes = (
        despesas
        .groupby(despesas['data'].dt.to_period('M'))['valor']
        .sum()
    )

    tendencia_mensal = [
        {
            'mes': str(mes),
            'valor': float(valor)
        }
        for mes, valor in despesas_por_mes.items()
    ]

    # Comparação mensal
    df['mes'] = df['data'].dt.to_period('M')

    receitas_por_mes = (
        df[df['tipo'] == 'receita']
        .groupby('mes')['valor']
        .sum()
    )

    despesas_por_mes_comparacao = (
        df[df['tipo'] == 'despesa']
        .groupby('mes')['valor']
        .sum()
    )

    variacao_receitas = 0
    variacao_despesas = 0

    if len(receitas_por_mes) >= 2:
        ultimo = receitas_por_mes.iloc[-1]
        anterior = receitas_por_mes.iloc[-2]

        if anterior != 0:
            variacao_receitas = (
                (ultimo - anterior) / anterior
            ) * 100

    if len(despesas_por_mes_comparacao) >= 2:
        ultimo = despesas_por_mes_comparacao.iloc[-1]
        anterior = despesas_por_mes_comparacao.iloc[-2]

        if anterior != 0:
            variacao_despesas = (
                (ultimo - anterior) / anterior
            ) * 100

    context = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_transacoes': total_transacoes,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'media_despesas': media_despesas,
        'maior_despesa': maior_despesa,
        'descricao_maior_despesa': descricao_maior_despesa,
        'percentual_despesas': percentual_despesas,
        'top_despesas': top_despesas,
        'maior_gasto_diario': maior_gasto_diario,
        'data_maior_gasto': data_maior_gasto,
        'media_diaria': media_diaria,
        'dias_com_despesas': dias_com_despesas,
        'tendencia_mensal': tendencia_mensal,
        'variacao_receitas': variacao_receitas,
        'variacao_despesas': variacao_despesas,
    }

    return render(request, 'analises.html', context)


def transacoes(request):
    transacoes = Transacao.objects.order_by('-data', '-id')

    return render(request, 'transacoes.html', {
        'transacoes': transacoes
    })


def editar_transacao(request, id):
    transacao = get_object_or_404(Transacao, id=id)

    if request.method == 'POST':
        form = TransacaoForm(request.POST, instance=transacao)

        if form.is_valid():
            form.save()
            return redirect('transacoes')
    else:
        form = TransacaoForm(instance=transacao)

    return render(request, 'editar_transacao.html', {
        'form': form,
        'transacao': transacao
    })


def excluir_transacao(request, id):
    transacao = get_object_or_404(Transacao, id=id)

    if request.method == 'POST':
        transacao.delete()
        return redirect('transacoes')

    return render(request, 'excluir_transacao.html', {
        'transacao': transacao
    })