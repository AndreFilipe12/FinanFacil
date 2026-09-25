from django import forms
from .models import Transacao


class TransacaoForm(forms.ModelForm):

    tipo = forms.ChoiceField(
        choices=[
            ('', 'Selecione o tipo'),
            ('receita', 'Receita'),
            ('despesa', 'Despesa'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )

    class Meta:
        model = Transacao

        fields = [
            'tipo',
            'descricao',
            'valor',
            'data',
        ]

        widgets = {

            'descricao': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ex: Salário'
                }
            ),

            'valor': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0,00',
                    'step': '0.01'
                }
            ),

            'data': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

        }