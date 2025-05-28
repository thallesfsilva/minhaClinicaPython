from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
import json

from collections import Counter

from openpyxl.workbook import Workbook
from weasyprint import HTML

from core.forms import RegistroForm, PacienteForm, ProcedimentoForm, AgendamentoForm, UserEditForm
from core.models import Paciente, Procedimento, Agendamento


def registrar_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('registrar')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Usuário já existente!')
            return redirect('registrar')

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        user.set_password(senha)
        user.save()

        messages.success(request, 'Usuário criado com sucesso!')
        return redirect('login')

    return render(request, 'core/registro.html')

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        print(f'username: {username}, senha: {senha}')

        user = authenticate(request, username=username, password=senha)
        if user is not None:
            login(request, user)
            print("Login bem-sucedido, redirecionando para home...")
            return redirect('listar_agendamentos')
        else:
            messages.error(request, 'Usuário ou senha inválidos!')
    return render(request, 'core/login.html')

def logout_usuario(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    user = request.user
    agendamentos = Agendamento.objects.filter(user=user)
    pacientes = Paciente.objects.filter(user=user)

    # Procedimentos mais agendados
    procedimento_nomes = [a.procedimento.nome for a in agendamentos]
    procedimentos_mais_agendados = Counter(procedimento_nomes).most_common(5)

    # Faturamento (soma dos preços dos agendamentos pagos)
    faturamento_total = sum(
        a.procedimento.preco for a in agendamentos if a.status_agendamento == 'Pago'
    )

    # Próximo agendamento
    futuros = agendamentos.filter(data_agendamento__gt=timezone.now()).order_by('data_agendamento')
    proximo_agendamento = futuros.first() if futuros.exists() else None

    # Quantidade total de pacientes
    total_pacientes = pacientes.count()

    # Total de agendamentos futuros
    total_agendamentos_futuros = futuros.count()

    procedimentos_labels = [item[0] for item in procedimentos_mais_agendados]
    procedimentos_data = [item[1] for item in procedimentos_mais_agendados]

    context = {
        'procedimentos_mais_agendados': procedimentos_mais_agendados,
        'faturamento_total': faturamento_total,
        'proximo_agendamento': proximo_agendamento,
        'total_pacientes': total_pacientes,
        'total_agendamentos_futuros': total_agendamentos_futuros,
        'procedimentos_labels': procedimentos_labels,
        'procedimentos_data': procedimentos_data
    }

    return render(request, 'core/home.html', context)
@login_required
def cadastrar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(commit=False)
            paciente.user = request.user
            paciente.save()
            return redirect('listar_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'core/cadastrar_paciente.html', {'form': form})

@login_required
def listar_pacientes(request):
    query = request.GET.get('q')
    pacientes = Paciente.objects.filter(user=request.user)

    if query:
        pacientes = pacientes.filter(nome__icontains=query)

    return render(request, 'core/listar_pacientes.html', {
        'pacientes': pacientes,
        'query': query
    })

@login_required
def cadastrar_procedimento(request):
    if request.method == 'POST':
        form = ProcedimentoForm(request.POST)
        if form.is_valid():
            procedimento = form.save(commit=False)
            procedimento.user = request.user
            procedimento.save()
            return redirect('listar_procedimentos')
    else:
       form = ProcedimentoForm()
    return render(request, 'core/cadastrar_procedimento.html', {'form': form})

@login_required
def listar_procedimentos(request):
    procedimentos = Procedimento.objects.filter(user=request.user)
    return render(request, 'core/listar_procedimentos.html', {
        'procedimentos': procedimentos
    })

@login_required()
def cadastrar_agendamento(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST, user=request.user)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.user = request.user
            agendamento.save()
            return redirect('listar_agendamentos')
    else:
        form = AgendamentoForm(user=request.user)
    return render(request, 'core/cadastrar_agendamento.html', {'form': form})

@login_required()
def listar_agendamentos(request):
    query = request.GET.get('q')

    agendamentos = Agendamento.objects.filter(
        user=request.user,
        data_agendamento__gte=timezone.now()
    ).order_by('data_agendamento')

    if query:
        agendamentos = agendamentos.filter(paciente__nome__icontains=query)

    return render(request, 'core/listar_agendamentos.html', {
        'agendamentos': agendamentos,
        'query': query
    })

@login_required()
def editar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, user=request.user)

    if request.method == 'POST':
        novo_status = request.POST.get('status_agendamento')
        if novo_status in dict(Agendamento.STATUS_CHOICES).keys():
            agendamento.status_agendamento = novo_status
            agendamento.save()
            return redirect('listar_agendamentos')

    return render(request, 'core/editar_status.html', {
        'agendamento': agendamento,
        'status_agendamento': agendamento.status_agendamento
    })

@login_required
def editar_paciente(request, paciente_id):
    print(f"[DEBUG] Usuário: {request.user}")
    print(f"[DEBUG] ID do paciente: {paciente_id}")

    paciente = get_object_or_404(Paciente, id=paciente_id, user=request.user)
    print(f"[DEBUG] Paciente encontrado: {paciente}")

    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('listar_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'core/editar_paciente.html', {'form': form})

@login_required()
def historico_agendamentos(request):
    status = request.GET.get('status')
    agendamentos = Agendamento.objects.filter(user=request.user)

    if status:
        agendamentos = agendamentos.filter(status_agendamento=status)

    agendamentos = agendamentos.order_by('-data_agendamento')

    return render(request, 'core/historico_agendamentos.html',{
        'agendamentos': agendamentos,
        'status_agendamento': status,
        'status_choices': Agendamento.STATUS_CHOICES
    })

@login_required
def dashboard(request):
    agendamentos = Agendamento.objects.filter(user=request.user)

    # Procedimentos mais agendados
    procedimento_nomes = [a.procedimento.nome for a in agendamentos]
    procedimentos_mais_agendados = Counter(procedimento_nomes).most_common(5)

    # Faturamento (soma dos preços dos agendamentos pagos)
    faturamento_total = sum(a.procedimento.preco for a in agendamentos if a.status_agendamento == 'Pago')

    # Próximo agendamento
    futuros = agendamentos.filter(data_agendamento__gt=timezone.now()).order_by('data_agendamento')
    proximo_agendamento = futuros.first() if futuros.exists() else None

    context = {
        'procedimentos_mais_agendados': procedimentos_mais_agendados,
        'faturamento_total': faturamento_total,
        'proximo_agendamento': proximo_agendamento
    }

    return render(request, 'core/home.html', context)

@login_required
def exportar_agendamentos_excel(request):
    agendamentos = Agendamento.objects.filter(
        user=request.user,
        data_agendamento__gt=timezone.now()
    ).order_by('-data_agendamento')

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Agendamentos'

    # Cabeçalho
    headers = ['Paciente', 'Procedimento', 'Data Do Procedimento', 'Valor (R$)','Status']
    sheet.append(headers)

    # Dados
    for agendamento in agendamentos:
        sheet.append([
            str(agendamento.paciente),
            str(agendamento.procedimento),
            agendamento.data_agendamento.strftime('%d/%m/%Y'),
            f"{agendamento.procedimento.preco:.2f}".replace('.',','),
            agendamento.status_agendamento
        ])

    # Resposta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="agendamentos.xlsx"'
    workbook.save(response)
    return response

@login_required
def meu_cadasro(request):
    user = request.user

    if request.method == 'POST':
        if 'dados_submit' in request.POST:
            form = UserEditForm(request.POST, instance=user)
            senha_form = PasswordChangeForm(user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Dados atualizados com sucesso.')
                return redirect('meu_cadasro')

        elif 'senha_submit' in request.POST:
            form = UserEditForm(instance=user)
            senha_form = PasswordChangeForm(user, request.POST)
            if senha_form.is_valid():
                senha_form.save()
                update_session_auth_hash(request, senha_form.user)
                messages.success(request, 'Senha alterada com sucesso.')
                return redirect('meu_cadasro')
            else:
                messages.error(request, 'Corrija os erros no formulário de senha.')
    else:
        form = UserEditForm(instance=user)
        senha_form = PasswordChangeForm(user)

    return render(request, 'core/meu_cadastro.html', {
        'form': form,
        'senha_form': senha_form
    })

@login_required
def relatorio_faturamento_pdf(request):
    inicio = request.GET.get('inicio')
    fim = request.GET.get('fim')

    if not inicio or not fim:
        return HttpResponse("É necessário informar o período.", status=400)

    inicio_data = datetime.strptime(inicio, '%Y-%m-%d')
    fim_data = datetime.strptime(fim, '%Y-%m-%d')

    agendamentos = Agendamento.objects.filter(
        user=request.user,
        status_agendamento='Pago',
        data_agendamento__range=(inicio_data, fim_data)
    )

    total = sum(a.procedimento.preco for a in agendamentos)

    template = get_template('core/relatorio_faturamento_pdf.html')
    html = template.render({'agendamentos': agendamentos, 'total': total, 'inicio': inicio, 'fim': fim_data})

    pdf_file = HTML(string=html).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Relatorio_Faturamento.pdf"'
    return response