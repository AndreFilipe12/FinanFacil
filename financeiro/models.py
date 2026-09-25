from django.db import models


class Transacao(models.Model):

    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES
    )

    descricao = models.CharField(max_length=200)

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    categoria = models.CharField(max_length=100)

    data = models.DateField()

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descricao