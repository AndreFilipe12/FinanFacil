from django import template

register = template.Library()


@register.filter
def moeda_brasileira(valor):
    if valor is None or valor == '':
        valor = 0

    try:
        valor = float(valor)
    except (ValueError, TypeError):
        valor = 0

    valor_formatado = f"{valor:,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return valor_formatado