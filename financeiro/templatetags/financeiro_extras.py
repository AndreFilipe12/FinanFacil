from django import template

register = template.Library()


@register.filter
def moeda_brasileira(valor):

    valor = float(valor)

    valor_formatado = f"{valor:,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return valor_formatado