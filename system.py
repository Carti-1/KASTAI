import os
import json
import datetime 
from task import Tarefa
from user import Usuario


class SistemaGerenciadorTarefas:

    def __init__(self):
        self.usuarios = [] #Lista de usuário
        self.tarefas = [] #Lista de Tarefas
        self.carregar_dados()

    def criar_usuario(self, nome, email):
        novo_id = len(self.usuarios) + 1 #Id único local
        usuario = Usuario(novo_id, nome, email)
        self.usuarios.append(usuario)
        print(f"Usuário {nome} criado com sucesso!")
        return usuario 
    
    def deletar_usuario(self, id_usuario):
        usuario = self.buscar_usuario_por_id(id_usuario)
        if usuario:
            # Verificar se o usuário tem tarefas associadas
            tarefas_associadas = [t for t in self.tarefas if t.usuario_associado == usuario]
            if tarefas_associadas:
                print(f"Erro: O usuário '{usuario.nome}' tem tarefas associadas. Por favor, reatribua ou exclua essas tarefas antes de deletar o usuário.")
            else:
                self.usuarios.remove(usuario)


    def criar_tarefa(self, titulo, descricao, id_usuario, prioridade="Média"):
        usuario_associado = self.buscar_usuario_por_id(id_usuario)
        if usuario_associado:
            novo_id = len(self.tarefas) + 1 #Id único local
            tarefa = Tarefa(novo_id, titulo, descricao, usuario_associado, prioridade)
            self.tarefas.append(tarefa)
            print(f"Tarefa '{titulo}', criada com sucesso!")
        else:
            print(f"Erro: Usuário com ID: {id_usuario} não encontrado!")
    

    def listar_usuarios(self):
        if not self.usuarios:
            print("Nenhum usuário encontrado.")
            return
        for usuario in self.usuarios:
            print(f"ID: {usuario.id_usuario}, Nome: {usuario.nome}, Email: {usuario.email}")

    def listar_tarefas(self):
        if not self.tarefas:
            print("Nenhuma tarefa cadastrada.")
            return
        for tarefa in self.tarefas:
            print(f"ID: {tarefa.id_tarefa}, Título: {tarefa.titulo}, Descrição: {tarefa.descricao}, Status: {tarefa.status}, Usuário: {tarefa.usuario_associado.nome}")
        
    def buscar_usuario_por_id(self, id_usuario):
        for usuario in self.usuarios:
            if usuario.id_usuario == id_usuario:
                return usuario
                
        return None

    def buscar_usuario_por_nome(self, nome):
        matching_users = []
        for user in self.usuarios:
            if user.nome.lower() == nome.lower():
                matching_users.append(user)
        # Lista de usuários correspondentes ou None se nenhum for encontrado
        return matching_users if matching_users else None

    def buscar_tarefa_por_id(self, id_tarefa):
        for tarefa in self.tarefas:
            if tarefa.id_tarefa == id_tarefa:
                return tarefa
        return None

    def exportar_json(self, nome_arquivo="tasks.json"):
        tarefas_data = []
        for tarefa in self.tarefas:
            tarefa_info = {
                "id_tarefa": tarefa.id_tarefa,
                "titulo": tarefa.titulo,
                "descricao": tarefa.descricao,
                "status": tarefa.status,
                "prioridade": tarefa.prioridade,
                "usuario": { 
                    "id_usuario": tarefa.usuario_associado.id_usuario,
                    "nome": tarefa.usuario_associado.nome,
                    "email": tarefa.usuario_associado.email
                }
            }   
            if tarefa._data_limite: # Salvar a data limite se ela existir
                tarefa_info["data_limite"] = tarefa._data_limite.isoformat() # Converte para string ISO 8601
            tarefas_data.append(tarefa_info)

        with open(nome_arquivo, "w") as file:
            json.dump(tarefas_data, file, indent=4)
        print(f"Tarefas salvas.")

    def verificar_lembretes_tarefas(self, dias_antecedencia=3):
        hoje = datetime.date.today()
        lembretes_encontrados = False
        print("\n--- Verificando Lembretes de Tarefas ---")
        for tarefa in self.tarefas:
            if tarefa._data_limite and tarefa.status != Tarefa.status_concluida:
                diferenca = tarefa._data_limite - hoje
                if 0 <= diferenca.days <= dias_antecedencia:
                    print(f"Lembrete! A tarefa '{tarefa.titulo}' (ID: {tarefa.id_tarefa}) está próxima do prazo: {tarefa._data_limite.strftime('%d/%m/%Y')}.")
                    lembretes_encontrados = True
        if not lembretes_encontrados:
            print("Nenhum lembrete para os próximos dias.")

    def carregar_dados(self, nome_arquivo="tasks.json"):
        if not os.path.exists(nome_arquivo):
            return

        with open(nome_arquivo, "r") as file:
            dados = json.load(file)
            for item in dados:
                u = item["usuario"]
                usuario_obj = self.buscar_usuario_por_id(u["id_usuario"])
                if not usuario_obj:
                    usuario_obj = Usuario(u["id_usuario"], u["nome"], u["email"])
                    self.usuarios.append(usuario_obj)
                
                tarefa = Tarefa(item["id_tarefa"], item["titulo"], item["descricao"], usuario_obj, item.get("prioridade", "Média"))
                tarefa.status = item["status"]
                if "data_limite" in item:
                    tarefa.definir_data_limite(datetime.date.fromisoformat(item["data_limite"]))
                self.tarefas.append(tarefa)
        print("Dados carregados com sucesso!")