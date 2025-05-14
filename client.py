import socket
import json
import datetime


#string -> datetime
def validar_data_hora(data_hora_str):
    try:
        datetime.datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False

def menu():
    print("\n=== MENU ===")
    print("1. Agendar tarefa")
    print("2. Listar tarefas")
    print("3. Cancelar tarefa")
    print("0. Sair")
    return input("Escolha uma opção: ")


# cria uma conexão com o servidor
# envia um comando e retornar um socket
def enviar_comando(comando):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('localhost', 5555))
    cliente.send(comando.encode('utf-8'))
    return cliente

def main():
    while True:
        opcao = menu()
        if opcao == '1':
            nome = input("Nome da tarefa: ")
            while True:
                horario = input("Hora agendada (AAAA-MM-DD HH:MM:SS): ")
                if validar_data_hora(horario):
                    data_agendada = datetime.datetime.strptime(horario, "%Y-%m-%d %H:%M:%S")
                    if data_agendada <= datetime.datetime.now():
                        print("Erro: Não é possível agendar para uma data/hora no passado.")
                        continue
                    break
                else:
                    print("Formato inválido. Use o formato AAAA-MM-DD HH:MM:SS (ex: 2023-12-31 23:59:00)")
            
            cliente = enviar_comando(f"agendar;{nome};{horario}")
            resposta = cliente.recv(1024).decode('utf-8')
            print(resposta)
            if "Digite o comando" in resposta:
                comando_exec = input("Comando a ser executado (ex: start calc, start regedit, etc.): ")
                cliente.send(comando_exec.encode('utf-8'))
                resposta_final = cliente.recv(1024).decode('utf-8')
                print(resposta_final)
            cliente.close()

        elif opcao == '2':
            cliente = enviar_comando("listar;;")
            resposta = cliente.recv(4096).decode('utf-8')
            try:
                tarefas = json.loads(resposta)
                print("\nTarefas agendadas:")
                for t in tarefas:
                    print(f"- {t['nome']} (Horário: {t['hora_agendada']})")
            except:
                print(resposta)
            cliente.close()

        elif opcao == '3':
            nome = input("Nome da tarefa a cancelar: ")
            cliente = enviar_comando(f"cancelar;{nome};")
            resposta = cliente.recv(1024).decode('utf-8')
            print(resposta)
            cliente.close()

        elif opcao == '0':
            break

        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()