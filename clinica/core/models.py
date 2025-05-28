from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models

class Paciente(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, blank=False, null=False)
    telefone = models.CharField(max_length=15, unique=True, blank=False, null=False)
    data_nascimento = models.DateField()
    email = models.EmailField(unique=True, blank=False, null=False)

    def __str__(self):
        return self.nome

class Procedimento(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, blank=False, null=False)
    preco = models.DecimalField(max_digits= 8, decimal_places=2, blank=False, null=False)
    data_criacao = models.DateTimeField(default=timezone.now)
    descricao = models.TextField()

    def __str__(self):
        return self.nome

class Agendamento(models.Model):

    STATUS_CHOICES = [
        ('Marcado', 'Marcado'),
        ('Realizado', 'Realizado'),
        ('Pago', 'Pago'),
        ('Cancelado', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, blank=False, null=False)
    procedimento = models.ForeignKey(Procedimento, on_delete=models.CASCADE, blank=False, null=False)
    data_agendamento = models.DateTimeField(blank=False, null=False)
    status_agendamento = models.CharField(choices=STATUS_CHOICES, default='Marcado')

    def __str__(self):
        return f"{self.procedimento.nome} - {self.paciente.nome} em {self.data_agendamento.strftime('%d/%m/%Y %H:%M') if self.data_agendamento else 'Sem data'} ({self.get_status_display()})"