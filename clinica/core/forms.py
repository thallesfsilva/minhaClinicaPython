from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from core.models import Paciente, Procedimento, Agendamento


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

class PacienteForm(forms.ModelForm):
    nome = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    telefone = forms.CharField(required=True)
    data_nascimento = forms.DateField(required=True)

    class Meta:
        model = Paciente
        fields = ('nome', 'email', 'telefone', 'data_nascimento')

class ProcedimentoForm(forms.ModelForm):
    nome = forms.CharField(required=True)
    preco = forms.DecimalField(required=True)
    data_criacao = forms.DateField(required=True)

    class Meta:
        model = Procedimento
        fields = ('nome', 'descricao', 'preco', 'data_criacao')

class AgendamentoForm(forms.ModelForm):
    data_agendamento = forms.DateTimeField(
        widget=forms.DateInput(attrs={'type': 'datetime-local'}, format='%d/%m/%Y %H:%M'),
        input_formats=['%d/%m/%Y %H:%M']
    )
    class Meta:
        model = Agendamento
        fields = ('paciente', 'procedimento' ,'data_agendamento', 'status_agendamento')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['paciente'].queryset = Paciente.objects.filter(user=user)
            self.fields['procedimento'].queryset = Procedimento.objects.filter(user=user)

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']