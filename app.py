import json
import streamlit as st
from google import genai
from google.genai import types
from system import SistemaGerenciadorTarefas
#
# 1. Configuração da página e cliente IA
st.set_page_config(page_title="KASTAI - Seu assistente no gerenciamento de tarefas!", page_icon="📖✏️")
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Inicializa o sistema no session_state para persistência entre reruns
if "sistema" not in st.session_state:
    st.session_state.sistema = SistemaGerenciadorTarefas()

if "historico" not in st.session_state:
    st.session_state.historico = []


with st.sidebar:
    st.title("👤 Usuário Ativo")
    
    # Força a recarga dos dados para garantir que temos os usuários mais recentes
    st.session_state.sistema.carregar_dados()
    usuarios_cadastrados = st.session_state.sistema.usuarios
    
    if not usuarios_cadastrados:
        st.warning("Nenhum usuário cadastrado no sistema.")
        nome_temp = st.text_input("Criar usuário inicial (Nome):", "João Pedro")
        email_temp = st.text_input("E-mail:", "joao@email.com")
        if st.button("Cadastrar Usuário Inicial"):
            st.session_state.sistema.criar_usuario(nome_temp, email_temp)
            st.session_state.sistema.exportar_json()
            st.rerun()
    else:
        # Mapeia a string de exibição para o ID real do usuário
        opcoes = {f"{u.nome} (ID: {u.id_usuario})": u.id_usuario for u in usuarios_cadastrados}
        escolha = st.selectbox("Selecione quem está usando o sistema:", list(opcoes.keys()))
        
        # Guarda o ID selecionado no session_state para persistência segura
        st.session_state.id_usuario_atual = opcoes[escolha]
        st.success(f"Conectado como ID: {st.session_state.id_usuario_atual}")

# Funções auxiliares para servirem de tools
def criar_usuario(nome: str, email: str) -> str:
    """Cria um novo usuário no sistema."""
    st.session_state.sistema.criar_usuario(nome, email)
    st.session_state.sistema.exportar_json()
    # Retorna uma string clara para o Gemini ler
    return f"Sucesso: Usuário '{nome}' criado com o e-mail '{email}'."

def criar_task(titulo: str, descricao: str, prioridade: str = "Média") -> str:
    """Cria uma nova tarefa para o usuário que está logado atualmente no sistema.
    Use esta função sempre que o usuário pedir para criar, agendar ou anotar uma tarefa."""

    id_usuario = st.session_state.get("id_usuario_atual")
    st.session_state.sistema.criar_tarefa(titulo, descricao, id_usuario, prioridade)
    st.session_state.sistema.exportar_json()
    return f"Tarefa '{titulo}' criada com sucesso."

def listar_tarefas() -> str:
    """Lista todas as tarefas cadastradas."""

    st.session_state.sistema.carregar_dados()
    
    id_usuario = st.session_state.get("id_usuario_atual")
    if id_usuario is None:
        return "Erro: Nenhum usuário ativo selecionado."

    tarefas = st.session_state.sistema.tarefas
    tarefas_filtradas = [t for t in tarefas if t.usuario_associado.id_usuario == id_usuario]
    if not tarefas_filtradas: 
        return "Nenhuma tarefa encontrada."
            
    lista_simples = [{"id": t.id_tarefa, "titulo": t.titulo, "usuario": t.usuario_associado.nome} for t in tarefas]
    return json.dumps(lista_simples, ensure_ascii=False)

def deletar_tarefa(id_tarefa: int) -> str:
    """Exclui uma tarefa do sistema através do seu ID."""
    sucesso = st.session_state.sistema.deletar_tarefa(id_tarefa)
    if sucesso:
        st.session_state.sistema.exportar_json()
        return f"Tarefa {id_tarefa} deletada com sucesso."
    return f"Erro: Tarefa {id_tarefa} não encontrada."

# 2. Configura a IA com as ferramentas vinculadas ao estado do app
config = types.GenerateContentConfig(
    system_instruction=("Você é um assistente de produtividade pessoal. Use as ferramentas para gerenciar usuários e tarefas. "
        "Você NÃO precisa e NÃO deve pedir o ID do usuário para criar ou listar tarefas; o sistema já gerencia o usuário ativo "
        "através do estado da sessão. Sempre execute os comandos tendo em vista o usuário atual."),
    tools=[criar_usuario, criar_task, listar_tarefas, deletar_tarefa], 
    temperature=0.4
)

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(model="gemini-2.5-flash", config=config)

col1, col2 = st.columns([2, 1])

with col1:
# 3. Desenha a interface de Chat na tela
    st.title("Assistente de tarefas 📝 ")
    st.write("Converse com a Agente para gerenciar sua rotina.")

    for msg in st.session_state.historico:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("O que você gostaria de fazer?"):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.historico.append({"role": "user", "content": prompt})
        
        # Envia para a IA, que decide se vai chamar o 'system.py'
        resposta = st.session_state.chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.write(resposta.text)
        st.session_state.historico.append({"role": "assistant", "content": resposta.text})
        # Após a resposta, recarrega os dados para garantir que a interface de tarefas esteja atualizada
        st.session_state.sistema.carregar_dados()
        st.rerun()

with col2:
    st.subheader("📋 Suas Tarefas Atuais")

    st.session_state.sistema.carregar_dados()

    id_usuario = st.session_state.get("id_usuario_atual")
    tarefas_atuais = st.session_state.sistema.tarefas

    tarefas_do_usuario = [t for t in tarefas_atuais if t.usuario_associado.id_usuario == id_usuario] if id_usuario else []
    
    tarefas_atuais = st.session_state.sistema.tarefas
    if not tarefas_do_usuario:
        st.info("Nenhuma tarefa criada ainda. Peça para que eu crie uma!")
    else:
        # O loop lerá a lista atualizada após o st.rerun()
        for t in tarefas_do_usuario:
            cols_tarefa = st.columns([0.85, 0.15])
            with cols_tarefa[0]:
                status_check = st.checkbox(f"**{t.titulo}**", key=f"t_{t.id_tarefa}", value=(t.status == "Concluída"))
                novo_status = "Concluída" if status_check else "Pendente"
                if novo_status!= t.status:
                    t.mudar_status(novo_status)
                    st.session_state.sistema.exportar_json()
            with cols_tarefa[1]:
                if st.button("🗑️", key=f"del_{t.id_tarefa}"):
                    st.session_state.sistema.deletar_tarefa(t.id_tarefa)
                    st.session_state.sistema.exportar_json()
                    st.rerun()
        
        if st.button("💾 Salvar Alterações"):
            st.session_state.sistema.exportar_json()