from system import SistemaGerenciadorTarefas
import datetime

sistema = SistemaGerenciadorTarefas()

print("KastIA - Seu assistente no gerenciamento de tarefas!")

def exibir_menu():
    print("\n--- Menu ---")
    print("1. Criar Novo Usuário")
    print("2. Criar Nova Tarefa")
    print("3. Listar Usuários")
    print("4. Listar Tarefas")
    print("5. Verificar Lembretes do Agente")
    print("6. Sair e Salvar")
    print("------------")


while True:
    exibir_menu()
    opcao = input("\nO que você gostaria de fazer?")

    if opcao == "1":
        nome = input("Nome do usuário: ")
        email = input("Email do usuário: ")
        sistema.criar_usuario(nome, email)
    elif opcao == "2":
        titulo = input("Título da tarefa: ")
        descricao = input("Descrição da tarefa: ")
        
        qtd_usuarios = len(sistema.usuarios)
        usuario_selecionado = None
        nome_usuario_input = ""

        if qtd_usuarios == 0:
            print("Não há usuários cadastrados para associar a tarefa.")
            confirmacao = input("Deseja criar um novo usuário agora? (s/n): ")
            if confirmacao.lower() == 's':
                nome = input("Nome do novo usuário: ")
                email = input("Email do novo usuário: ")
                novo_usuario = sistema.criar_usuario(nome, email)
                if novo_usuario:
                    usuario_selecionado = novo_usuario
                    print(f"Tarefa criada para o usuário: {novo_usuario.nome}")
                else:
                    print("Falha ao criar o novo usuário. Tarefa não criada.")
                    continue
            else:
                print("Não é possivel criar uma tarefa sem um usuário associado.")
                continue
        elif qtd_usuarios == 1:
            usuario_selecionado = sistema.usuarios[0]
            print(f"Tarefa associada ao usuário(a): {usuario_selecionado.nome}, criada com sucesso!")
        else:
            nome_usuario_input = input("Para qual usuário é esta tarefa? ")
            usuarios_encontrados = sistema.buscar_usuario_por_nome(nome_usuario_input)
            
            if usuarios_encontrados:
                if len(usuarios_encontrados) == 1:
                    usuario_selecionado = usuarios_encontrados[0]
                else:
                    print(f"Múltiplos usuários encontrados com o nome '{nome_usuario_input}':")
                    for user in usuarios_encontrados:
                        print(f"  ID: {user.id_usuario}, Nome: {user.nome}, Email: {user.email}")
                    try:
                        id_escolhido = int(input("Digite o ID do usuário correto para associar a tarefa: "))
                        usuario_selecionado = sistema.buscar_usuario_por_id(id_escolhido)
                        if not usuario_selecionado or usuario_selecionado.nome.lower() != nome_usuario_input.lower():
                            print("ID inválido ou não corresponde ao nome. Tarefa não criada.")
                            continue
                    except ValueError:
                        print("ID inválido. Tarefa não criada.")
                        continue
            else:
                print(f"Erro: Usuário '{nome_usuario_input}' não encontrado!")
                confirmacao = input("Deseja criar um novo usuário com esse nome? (s/n): ")
                if confirmacao.lower() == 's':
                    email = input("Email do novo usuário: ")
                    novo_usuario = sistema.criar_usuario(nome_usuario_input, email)
                    if novo_usuario:
                        usuario_selecionado = novo_usuario
                    else:
                        print("Falha ao criar o novo usuário. Tarefa não criada.")
                        continue
                else:
                    print("Tarefa não criada.")
                    continue

        if usuario_selecionado:
            sistema.criar_tarefa(titulo, descricao, usuario_selecionado.id_usuario)
        else:
            print("Erro ao criar tarefa.")
            continue
    elif opcao == "3":
        print("\n--- Lista de Usuários ---")
        sistema.listar_usuarios()
    elif opcao == "4":
        print("\n--- Lista de Tarefas ---")
        sistema.listar_tarefas()
    elif opcao == "5":
        print("\n--- Verificando Lembretes ---")
        sistema.verificar_lembretes_tarefas()
    elif opcao == "6":
        sistema.exportar_json()
        print("Até logo!")
        break
    else:
        print("\nOpção inválida ou em desenvolvimento.")