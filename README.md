# Aplicação de Agendamento de Tarefas com Sockets

## Descrição
Aplicação cliente-servidor par matéria de redes desenvolvida em Python, utilizando apenas **sockets** e **threads**. Permitindo que o cliente agende tarefas para serem executadas no servidor no horário determinado pelo usuário. As tarefas além de serem adicionadas podem também ser listadas e canceladas. 

## Como executar

1. **Abra dois terminais.**

2. **No primeiro terminal**, execute o servidor:
   ```bash
   python server.py
   ```

3. **No segundo terminal**, execute o cliente:
   ```bash
   python client.py
   ```

4. Agora basta seguir o menu:
   - Agendar tarefas com nome, data e comando.
   - Listar tarefas.
   - Cancelar tarefas.

## Exemplos de comandos
- `calc` → abre a calculadora.
- `notepad` → abre o bloco de notas.
- `https://www.google.com` → abre o navegador no site informado.
