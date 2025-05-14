import socket
import threading
import time
import datetime
import json
import os
import subprocess

arquivo_tarefas = "tarefas.json"
tarefas_agendadas = []
# aqui nessa func vamos ler o arquivo tarefas.json
# e carrega as tarefas salvas anteriormente para a lista tarefas_agendadas


def carregar_tarefas():
    global tarefas_agendadas
    if os.path.exists(arquivo_tarefas):
        with open(arquivo_tarefas, 'r') as f:
            tarefas_json = json.load(f)
            for tarefa in tarefas_json:
                tarefa['hora_agendada'] = datetime.datetime.strptime(
                    tarefa['hora_agendada'], "%Y-%m-%d %H:%M:%S")
                # aqui vamos converter texto para o formato da biblicoteca datatime
            tarefas_agendadas = tarefas_json


# aqui basicamente vai fazer o seguinte:
# salva a lista tarefas_agendadas no arquivo tarefas.json convertendo os objetos datetime em string
def salvar_tarefas():
    tarefas_para_salvar = [
        {'nome': t['nome'], 'hora_agendada': t['hora_agendada'].strftime(
            "%Y-%m-%d %H:%M:%S"), 'comando': t['comando']}
        for t in tarefas_agendadas
    ]
    with open(arquivo_tarefas, 'w') as f:
        json.dump(tarefas_para_salvar, f, indent=4)


# aqui qeu vai executar o comando agendado usando subprocess.Popen
def executar_tarefa(tarefa):
    print(f"Tarefa '{tarefa['nome']}' executada em {datetime.datetime.now()}")
    try:
        subprocess.Popen(tarefa['comando'], shell=True)
    except Exception as e:
        print(f"Erro ao executar comando: {e}")


# simples tbm vai verificar se é o momento de executar ou não
def verificar_tarefas():
    while True:
        now = datetime.datetime.now()
        for tarefa in tarefas_agendadas[:]:
            if tarefa['hora_agendada'] <= now:
                tarefas_agendadas.remove(tarefa)
                salvar_tarefas()
                executar_tarefa(tarefa)
        time.sleep(2)


# é grande mas tenha calma rapaz
# aqui vamos lidar com agendar, listar e cancelar
# cada cliente é tratada por uma thread separada (permite varios clientes ao msm tempo)
def gerenciar_cliente(cliente):
    try:
        while True:
            data = cliente.recv(1024).decode('utf-8')
            if not data:
                break

            comando, nome_tarefa, hora_ou_comando = data.split(';')

            if comando == 'agendar':
                try:
                    hora_agendada = datetime.datetime.strptime(
                        hora_ou_comando, "%Y-%m-%d %H:%M:%S")

                    if hora_agendada <= datetime.datetime.now():
                        cliente.send(
                            "Erro: Não é possível agendar para uma data/hora no passado.".encode('utf-8'))
                        continue

                    for t in tarefas_agendadas:
                        if t['hora_agendada'] == hora_agendada:
                            cliente.send(
                                "Erro: já existe uma tarefa agendada nesse horário.".encode('utf-8'))
                            break
                    else:
                        cliente.send(
                            "Digite o comando da tarefa:".encode('utf-8'))
                        comando_exec = cliente.recv(1024).decode('utf-8')

                        tarefa = {
                            'nome': nome_tarefa, 'hora_agendada': hora_agendada, 'comando': comando_exec}
                        tarefas_agendadas.append(tarefa)
                        salvar_tarefas()
                        cliente.send(
                            f"Tarefa '{nome_tarefa}' agendada para {hora_agendada}".encode('utf-8'))

                except ValueError:
                    cliente.send(
                        "Erro: Formato de data/hora inválido. Use o formato AAAA-MM-DD HH:MM:SS".encode('utf-8'))

            elif comando == 'listar':
                if tarefas_agendadas:
                    resposta = json.dumps(
                        tarefas_agendadas, indent=4, default=str)
                else:
                    resposta = "Nenhuma tarefa agendada."
                cliente.send(resposta.encode('utf-8'))

            elif comando == 'cancelar':
                antes = len(tarefas_agendadas)
                tarefas_agendadas[:] = [
                    t for t in tarefas_agendadas if t['nome'] != nome_tarefa]
                depois = len(tarefas_agendadas)
                salvar_tarefas()
                if antes == depois:
                    cliente.send("Tarefa não encontrada.".encode('utf-8'))
                else:
                    cliente.send(
                        "Tarefa cancelada com sucesso.".encode('utf-8'))

    except Exception as e:
        print(f"Erro ao gerenciar cliente: {e}")
    finally:
        cliente.close()

# essa função inicia o socket do servidor
# executa conexões e cria threads para cada cliente


def iniciar_servidor():
    carregar_tarefas()

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('localhost', 5555))
    servidor.listen(5)
    print("Servidor iniciado, aguardando conexões...")

    thread_verificar = threading.Thread(target=verificar_tarefas)
    thread_verificar.daemon = True
    thread_verificar.start()

    while True:
        cliente, endereco = servidor.accept()
        print(f"Cliente conectado: {endereco}")
        threading.Thread(target=gerenciar_cliente, args=(cliente,)).start()


if __name__ == "__main__":
    iniciar_servidor()
