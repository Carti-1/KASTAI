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

# Funções auxiliares para servirem de tools
def criar_usuario(nome: str, email: str) -> str:
    """Cria um novo usuário no sistema."""
    # Executa a sua lógica original
    st.session_state.sistema.criar_usuario(nome, email)
    st.session_state.sistema.exportar_json() # Garante que salva o usuário no JSON
    # Retorna uma string clara para o Gemini ler
    return f"Sucesso: Usuário '{nome}' criado com o e-mail '{email}'."

def criar_task(titulo: str, descricao: str, prioridade: str = "Média") -> str:
    """Cria uma nova tarefa para o usuário que está logado atualmente no sistema.
    Use esta função sempre que o usuário pedir para criar, agendar ou anotar uma tarefa."""
    st.session_state.sistema.criar_tarefa(titulo, descricao, id_usuario, prioridade)
    st.session_state.sistema.exportar_json()
    return f"Tarefa '{titulo}' criada com sucesso."

def listar_tarefas() -> str:
    """Lista todas as tarefas cadastradas."""
    tarefas = st.session_state.sistema.tarefas
    if not tarefas: 
        return "Nenhuma tarefa encontrada."
    
    # Criamos a estrutura de dados simples
    lista_simples = [{"id": t.id_tarefa, "titulo": t.titulo, "usuario": t.usuario_associado.nome} for t in tarefas]
    
    # 💡 Convertemos para String (JSON) para a API do Gemini não quebrar!
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
    system_instruction="Você é um assistente de produtividade. Use as ferramentas para gerenciar usuários e tarefas.",
    tools=[criar_usuario, criar_tarefa, listar_tarefas, deletar_tarefa], 
    temperature=0.5
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
        
        # Envia para a IA, que decide se vai chamar o seu 'system.py'
        resposta = st.session_state.chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.write(resposta.text)
        st.session_state.historico.append({"role": "assistant", "content": resposta.text})

        st.rerun()

with col2:
    st.subheader("📋 Suas Tarefas Atuais")
    tarefas_atuais = st.session_state.sistema.tarefas
    if not tarefas_atuais:
        st.info("Nenhuma tarefa criada ainda. Peça para a IA criar uma!")
    else:
        # O loop lerá a lista atualizada após o st.rerun()
        for t in tarefas_atuais:
            cols_tarefa = st.columns([0.85, 0.15])
            with cols_tarefa[0]:
                st.checkbox(f"**{t.titulo}**", key=f"t_{t.id_tarefa}", value=(t.status == "Concluída"))
            with cols_tarefa[1]:
                if st.button("🗑️", key=f"del_{t.id_tarefa}"):
                    st.session_state.sistema.deletar_tarefa(t.id_tarefa)
                    st.session_state.sistema.exportar_json()
                    st.rerun()
        
        if st.button("💾 Salvar Alterações"):
            st.session_state.sistema.exportar_json()