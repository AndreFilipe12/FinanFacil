from django.shortcuts import render, redirect
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import pandas as pd

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
        {
            'form': form
        }
    )


def relatorios(request):

    # ==========================================
    # FILTRO DE PERÍODO
    # ==========================================

    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')


    # ==========================================
    # BUSCA AS TRANSAÇÕES
    # ==========================================

    transacoes = Transacao.objects.all()


    # ==========================================
    # APLICA DATA INICIAL
    # ==========================================

    if data_inicio:

        transacoes = transacoes.filter(
            data__gte=data_inicio
        )


    # ==========================================
    # APLICA DATA FINAL
    # ==========================================

    if data_fim:

        transacoes = transacoes.filter(
            data__lte=data_fim
        )


    # ==========================================
    # CALCULA RECEITAS
    # ==========================================

    receitas = transacoes.filter(
        tipo='receita'
    ).aggregate(
        total=Sum('valor')
    )['total'] or 0


    # ==========================================
    # CALCULA DESPESAS
    # ==========================================

    despesas = transacoes.filter(
        tipo='despesa'
    ).aggregate(
        total=Sum('valor')
    )['total'] or 0


    # ==========================================
    # CALCULA SALDO
    # ==========================================

    saldo = receitas - despesas


    # ==========================================
    # DADOS DOS GRÁFICOS
    # ==========================================

    dados_grafico_queryset = (
        transacoes
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


    # ==========================================
    # CONTEXTO
    # ==========================================

    contexto = {

        'dados_grafico': dados_grafico,

        'receitas': receitas,

        'despesas': despesas,

        'saldo': saldo,

        'data_inicio': data_inicio,

        'data_fim': data_fim,

    }


    return render(
        request,
        'relatorios.html',
        contexto
    )


def analises(request):

    # ==========================================
    # FILTRO DE PERÍODO
    # ==========================================

    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')


    # ==========================================
    # BUSCA AS TRANSAÇÕES
    # ==========================================

    transacoes = Transacao.objects.all()


    # ==========================================
    # APLICA DATA INICIAL
    # ==========================================

    if data_inicio:

        transacoes = transacoes.filter(
            data__gte=data_inicio
        )


    # ==========================================
    # APLICA DATA FINAL
    # ==========================================

    if data_fim:

        transacoes = transacoes.filter(
            data__lte=data_fim
        )


    # ==========================================
    # SELECIONA OS CAMPOS
    # ==========================================

    transacoes = transacoes.values(
        'tipo',
        'descricao',
        'valor',
        'data'
    )


    # ==========================================
    # VERIFICA SE EXISTEM TRANSAÇÕES
    # ==========================================

    if not transacoes:

        contexto = {

            'total_transacoes': 0,

            'total_receitas': 0,

            'total_despesas': 0,

            'media_despesas': 0,

            'maior_despesa': 0,

            'descricao_maior_despesa': '',

            'percentual_despesas': 0,

            'maiores_despesas': [],

            'receitas_mes_atual': 0,

            'receitas_mes_anterior': 0,

            'variacao_receitas': 0,

            'despesas_mes_atual': 0,

            'despesas_mes_anterior': 0,

            'variacao_despesas': 0,

            'maior_gasto_diario': 0,

            'data_maior_gasto': None,

            'data_inicio': data_inicio,

            'data_fim': data_fim,

        }

        return render(
            request,
            'analises.html',
            contexto
        )


    # ==========================================
    # CRIA DATAFRAME
    # ==========================================

    df = pd.DataFrame(
        list(transacoes)
    )


    # ==========================================
    # CONVERTE VALORES
    # ==========================================

    df['valor'] = pd.to_numeric(
        df['valor']
    )


    # ==========================================
    # CONVERTE DATA
    # ==========================================

    df['data'] = pd.to_datetime(
        df['data']
    )


    # ==========================================
    # TOTAL DE TRANSAÇÕES
    # ==========================================

    total_transacoes = len(df)


    # ==========================================
    # RECEITAS
    # ==========================================

    receitas = df[
        df['tipo'] == 'receita'
    ]

    total_receitas = receitas[
        'valor'
    ].sum()


    # ==========================================
    # DESPESAS
    # ==========================================

    despesas = df[
        df['tipo'] == 'despesa'
    ]

    total_despesas = despesas[
        'valor'
    ].sum()


    # ==========================================
    # MÉDIA DAS DESPESAS
    # ==========================================

    if not despesas.empty:

        media_despesas = despesas[
            'valor'
        ].mean()

    else:

        media_despesas = 0


    # ==========================================
    # MAIOR DESPESA
    # ==========================================

    if not despesas.empty:

        maior_despesa = despesas[
            'valor'
        ].max()

        registro_maior_despesa = despesas.loc[
            despesas['valor'].idxmax()
        ]

        descricao_maior_despesa = (
            registro_maior_despesa['descricao']
        )

    else:

        maior_despesa = 0

        descricao_maior_despesa = ''


    # ==========================================
    # PARTICIPAÇÃO DAS DESPESAS
    # ==========================================

    total_movimentado = (
        total_receitas +
        total_despesas
    )


    if total_movimentado > 0:

        percentual_despesas = (
            total_despesas /
            total_movimentado
        ) * 100

    else:

        percentual_despesas = 0


    # ==========================================
    # MAIORES DESPESAS
    # ==========================================

    maiores_despesas = despesas.sort_values(
        by='valor',
        ascending=False
    ).head(5)


    maiores_despesas = maiores_despesas[
        [
            'descricao',
            'valor',
            'data'
        ]
    ].to_dict(
        orient='records'
    )


    # ==========================================
    # ANÁLISE DE GASTOS POR DIA
    # ==========================================

    despesas_por_dia = (
        despesas
        .groupby('data')['valor']
        .sum()
    )


    # ==========================================
    # MAIOR GASTO EM UM ÚNICO DIA
    # ==========================================

    if not despesas_por_dia.empty:

        maior_gasto_diario = despesas_por_dia.max()

        data_maior_gasto = (
            despesas_por_dia.idxmax()
        )

    else:

        maior_gasto_diario = 0

        data_maior_gasto = None


    # ==========================================
    # COMPARAÇÃO MENSAL
    # ==========================================

    df['mes'] = df['data'].dt.to_period('M')


    ultimo_mes = df['mes'].max()


    mes_anterior = (
        ultimo_mes - 1
    )


    # ==========================================
    # DADOS DO ÚLTIMO MÊS
    # ==========================================

    dados_mes_atual = df[
        df['mes'] == ultimo_mes
    ]


    # ==========================================
    # DADOS DO MÊS ANTERIOR
    # ==========================================

    dados_mes_anterior = df[
        df['mes'] == mes_anterior
    ]


    # ==========================================
    # RECEITAS DOS MESES
    # ==========================================

    receitas_mes_atual = dados_mes_atual[
        dados_mes_atual['tipo'] == 'receita'
    ]['valor'].sum()


    receitas_mes_anterior = dados_mes_anterior[
        dados_mes_anterior['tipo'] == 'receita'
    ]['valor'].sum()


    # ==========================================
    # DESPESAS DOS MESES
    # ==========================================

    despesas_mes_atual = dados_mes_atual[
        dados_mes_atual['tipo'] == 'despesa'
    ]['valor'].sum()


    despesas_mes_anterior = dados_mes_anterior[
        dados_mes_anterior['tipo'] == 'despesa'
    ]['valor'].sum()


    # ==========================================
    # VARIAÇÃO DAS RECEITAS
    # ==========================================

    if receitas_mes_anterior > 0:

        variacao_receitas = (
            (
                receitas_mes_atual -
                receitas_mes_anterior
            )
            /
            receitas_mes_anterior
        ) * 100

    else:

        variacao_receitas = 0


    # ==========================================
    # VARIAÇÃO DAS DESPESAS
    # ==========================================

    if despesas_mes_anterior > 0:

        variacao_despesas = (
            (
                despesas_mes_atual -
                despesas_mes_anterior
            )
            /
            despesas_mes_anterior
        ) * 100

    else:

        variacao_despesas = 0


    # ==========================================
    # CONTEXTO
    # ==========================================

    contexto = {

        'total_transacoes':
            total_transacoes,

        'total_receitas':
            total_receitas,

        'total_despesas':
            total_despesas,

        'media_despesas':
            media_despesas,

        'maior_despesa':
            maior_despesa,

        'descricao_maior_despesa':
            descricao_maior_despesa,

        'percentual_despesas':
            percentual_despesas,

        'maiores_despesas':
            maiores_despesas,

        'receitas_mes_atual':
            receitas_mes_atual,

        'receitas_mes_anterior':
            receitas_mes_anterior,

        'variacao_receitas':
            variacao_receitas,

        'despesas_mes_atual':
            despesas_mes_atual,

        'despesas_mes_anterior':
            despesas_mes_anterior,

        'variacao_despesas':
            variacao_despesas,

        'maior_gasto_diario':
            maior_gasto_diario,

        'data_maior_gasto':
            data_maior_gasto,

        'data_inicio':
            data_inicio,

        'data_fim':
            data_fim,

    }


    return render(
        request,
        'analises.html',
        contexto
    )


def transacoes(request):

    lista_transacoes = Transacao.objects.order_by(
        '-data',
        '-id'
    )

    return render(
        request,
        'transacoes.html',
        {
            'transacoes': lista_transacoes
        }
    )


def editar_transacao(request, id):

    transacao = Transacao.objects.get(
        id=id
    )


    if request.method == 'POST':

        form = TransacaoForm(
            request.POST,
            instance=transacao
        )

        if form.is_valid():

            form.save()

            return redirect(
                'transacoes'
            )

    else:

        form = TransacaoForm(
            instance=transacao
        )


    return render(
        request,
        'editar_transacao.html',
        {
            'form': form,
            'transacao': transacao
        }
    )


def excluir_transacao(request, id):

    transacao = Transacao.objects.get(
        id=id
    )


    if request.method == 'POST':

        transacao.delete()

        return redirect(
            'transacoes'
        )


    return render(
        request,
        'excluir_transacao.html',
        {
            'transacao': transacao
        }
    )