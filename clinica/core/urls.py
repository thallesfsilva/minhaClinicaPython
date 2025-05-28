from core import views
from django.urls import path

urlpatterns = [
    path('registrar', views.registrar_usuario, name='registrar'),
    path('logout', views.logout_usuario, name='logout'),
    path('login', views.login_usuario, name='login'),
    path('home', views.home, name='home'),
    path('pacientes/novo/', views.cadastrar_paciente, name='cadastrar_paciente'),
    path('pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('procedimento/novo/', views.cadastrar_procedimento, name='cadastrar_procedimento'),
    path('procedimentos/', views.listar_procedimentos, name='listar_procedimentos'),
    path('agendamento/novo/', views.cadastrar_agendamento, name='cadastrar_agendamento'),
    path('agendamentos/', views.listar_agendamentos, name='listar_agendamentos'),
    path('agendamento/<int:agendamento_id>/editar-status/', views.editar_agendamento, name='editar_status_agendamento'),
    path('agendamentos/historico/', views.historico_agendamentos, name='historico_agendamentos'),
    path('pacientes/editar/<int:paciente_id>/', views.editar_paciente, name='editar_paciente'),
    path('relatorios/agendamentos/excel/', views.exportar_agendamentos_excel, name='exportar_agendamentos_excel'),
    path('meu-cadastro', views.meu_cadasro, name='meu_cadastro'),
    path('relatorio-faturamento/', views.relatorio_faturamento_pdf, name='relatorio_faturamento_pdf'),
]