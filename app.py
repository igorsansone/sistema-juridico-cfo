import streamlit as st
import pandas as pd
import datetime
import json
import os

st.set_page_config(page_title="Sistema Jurídico CRO/RS", layout="wide")

# --- Inicialização da sessão ---
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = ""

if "processos" not in st.session_state:
    st.session_state.processos = []

if "movimentacoes" not in st.session_state:
    st.session_state.movimentacoes = []

if "despachos" not in st.session_state:
    st.session_state.despachos = []

if "jurisprudencias" not in st.session_state:
    st.session_state.jurisprudencias = []

if "agenda" not in st.session_state:
    st.session_state.agenda = []

# --- Banco de dados simulado ---
usuarios_db = [
    {"usuario": "igorsansone", "senha": "30101987", "permissao": "master"},
    {"usuario": "secretaria", "senha": "1234", "permissao": "normal"}
]

# --- Funções ---
def login(usuario, senha):
    for u in usuarios_db:
        if u["usuario"].lower() == usuario.lower() and u["senha"] == senha:
            st.session_state.logado = True
            st.session_state.usuario = u["usuario"]
            return True
    return False

def usuario_eh_master():
    # Apenas o usuário igorsansone com permissão master é master
    return st.session_state.usuario.lower() == "igorsansone"

def salvar_dados():
    dados = {
        "processos": st.session_state.processos,
        "movimentacoes": st.session_state.movimentacoes,
        "despachos": st.session_state.despachos,
        "jurisprudencias": st.session_state.jurisprudencias,
        "agenda": st.session_state.agenda
    }
    with open("dados.json", "w", encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def carregar_dados():
    if os.path.exists("dados.json"):
        try:
            with open("dados.json", "r", encoding='utf-8') as f:
                dados = json.load(f)
                st.session_state.processos = dados.get("processos", [])
                st.session_state.movimentacoes = dados.get("movimentacoes", [])
                st.session_state.despachos = dados.get("despachos", [])
                st.session_state.jurisprudencias = dados.get("jurisprudencias", [])
                st.session_state.agenda = dados.get("agenda", [])
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")

carregar_dados()

# --- Tela de login ---
if not st.session_state.logado:
    with st.form("login"):
        st.title("🔐 Sistema Jurídico CRO/RS - Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

        if entrar:
            if login(usuario, senha):
                st.success(f"Bem-vindo(a), {st.session_state.usuario}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos.")
    st.stop()

# --- Menu lateral ---
st.sidebar.title("📁 Menu Principal")
menu_opcoes = [
    "Início",
    "Cadastrar Processo",
    "Movimentações",
    "Despachos",
    "Jurisprudência",
    "Agenda",
    "Relatórios"
]
if usuario_eh_master():
    menu_opcoes.append("Gerenciar Usuários")

opcao = st.sidebar.radio("Navegar", menu_opcoes)
st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido por Igor Sansone - Setor de Secretaria")

# --- Funções das abas ---
def aba_inicio():
    st.title("📊 Painel do Sistema Jurídico")
    st.markdown(f"Bem-vindo(a), **{st.session_state.usuario}**!")
    col1, col2, col3 = st.columns(3)
    col1.metric("🔍 Processos cadastrados", len(st.session_state.processos))
    col2.metric("📌 Movimentações registradas", len(st.session_state.movimentacoes))
    col3.metric("📄 Despachos emitidos", len(st.session_state.despachos))

def aba_cadastrar_processo():
    st.title("📝 Cadastrar Novo Processo")
    with st.form("form_cadastrar_processo"):
        numero = st.text_input("Número do Processo")
        vara = st.text_input("Vara ou Plenário")
        partes = st.text_input("Partes (autor, réu)")
        status = st.selectbox("Status", ["Em andamento", "Concluído", "Suspenso"])
        data = st.date_input("Data de Cadastro", datetime.date.today())
        enviar = st.form_submit_button("Cadastrar")

        if enviar:
            if numero.strip() == "":
                st.error("O número do processo é obrigatório.")
                return
            novo_processo = {
                "numero": numero.strip(),
                "vara": vara.strip(),
                "partes": partes.strip(),
                "status": status,
                "data": str(data)
            }
            st.session_state.processos.append(novo_processo)
            salvar_dados()
            st.success("Processo cadastrado com sucesso!")

def aba_movimentacoes():
    st.title("🔄 Movimentações")
    if len(st.session_state.movimentacoes) == 0:
        st.info("Nenhuma movimentação registrada.")
    else:
        df_mov = pd.DataFrame(st.session_state.movimentacoes)
        st.dataframe(df_mov)

    with st.form("form_nova_movimentacao"):
        proc = st.text_input("Nº Processo")
        mov = st.text_area("Descrição da movimentação")
        dt = st.date_input("Data", datetime.date.today())
        enviar = st.form_submit_button("Cadastrar")

        if enviar:
            if proc.strip() == "" or mov.strip() == "":
                st.error("Número do processo e descrição são obrigatórios.")
                return
            nova_mov = {"processo": proc.strip(), "descricao": mov.strip(), "data": str(dt)}
            st.session_state.movimentacoes.append(nova_mov)
            salvar_dados()
            st.success("Movimentação salva!")

def aba_despachos():
    st.title("📑 Despachos")
    if len(st.session_state.despachos) == 0:
        st.info("Nenhum despacho emitido.")
    else:
        df_desp = pd.DataFrame(st.session_state.despachos)
        st.dataframe(df_desp)

    with st.form("form_novo_despacho"):
        proc = st.text_input("Nº Processo")
        conteudo = st.text_area("Conteúdo do despacho")
        dt = st.date_input("Data", datetime.date.today())
        enviar = st.form_submit_button("Emitir Despacho")

        if enviar:
            if proc.strip() == "" or conteudo.strip() == "":
                st.error("Número do processo e conteúdo são obrigatórios.")
                return
            novo_despacho = {"processo": proc.strip(), "despacho": conteudo.strip(), "data": str(dt)}
            st.session_state.despachos.append(novo_despacho)
            salvar_dados()
            st.success("Despacho emitido!")

def aba_jurisprudencia():
    st.title("⚖️ Cadastro de Jurisprudência")
    if len(st.session_state.jurisprudencias) == 0:
        st.info("Nenhuma jurisprudência cadastrada.")
    else:
        df_juri = pd.DataFrame(st.session_state.jurisprudencias)
        st.dataframe(df_juri)

    with st.form("form_nova_jurisprudencia"):
        tribunal = st.selectbox("Tribunal", ["TRF", "JF"])
        ementa = st.text_area("Ementa")
        referencia = st.text_input("Referência")
        enviar = st.form_submit_button("Cadastrar")

        if enviar:
            if ementa.strip() == "" or referencia.strip() == "":
                st.error("Ementa e referência são obrigatórias.")
                return
            nova_juris = {"tribunal": tribunal, "ementa": ementa.strip(), "referencia": referencia.strip()}
            st.session_state.jurisprudencias.append(nova_juris)
            salvar_dados()
            st.success("Jurisprudência cadastrada!")

def aba_agenda():
    st.title("📆 Agenda Jurídica")
    if len(st.session_state.agenda) == 0:
        st.info("Nenhum evento agendado.")
    else:
        df_agenda = pd.DataFrame(st.session_state.agenda)
        st.dataframe(df_agenda)

    with st.form("form_novo_evento"):
        evento = st.text_input("Descrição do Evento")
        local = st.text_input("Local")
        dt = st.date_input("Data", datetime.date.today())
        enviar = st.form_submit_button("Agendar")

        if enviar:
            if evento.strip() == "" or local.strip() == "":
                st.error("Descrição e local são obrigatórios.")
                return
            novo_evento = {"evento": evento.strip(), "local": local.strip(), "data": str(dt)}
            st.session_state.agenda.append(novo_evento)
            salvar_dados()
            st.success("Evento agendado!")

def aba_relatorios():
    st.title("📊 Relatórios do Sistema Jurídico")

    abas = ["Processos", "Movimentações", "Despachos", "Jurisprudências", "Agenda"]
    aba_sel = st.selectbox("Selecione a categoria para visualizar", abas)

    if aba_sel == "Processos":
        df = pd.DataFrame(st.session_state.processos)
        if df.empty:
            st.info("Nenhum processo cadastrado.")
        else:
            filtro_status = st.multiselect("Filtrar por Status", options=df['status'].unique(), default=list(df['status'].unique()))
            df_filtrado = df[df['status'].isin(filtro_status)]
            st.dataframe(df_filtrado)

    elif aba_sel == "Movimentações":
        df = pd.DataFrame(st.session_state.movimentacoes)
        if df.empty:
            st.info("Nenhuma movimentação registrada.")
        else:
            proc_filter = st.text_input("Filtrar por Número do Processo")
            if proc_filter:
                df_filtrado = df[df['processo'].str.contains(proc_filter, case=False, na=False)]
            else:
                df_filtrado = df
            st.dataframe(df_filtrado)

    elif aba_sel == "Despachos":
        df = pd.DataFrame(st.session_state.despachos)
        if df.empty:
            st.info("Nenhum despacho emitido.")
        else:
            proc_filter = st.text_input("Filtrar por Número do Processo")
            if proc_filter:
                df_filtrado = df[df['processo'].str.contains(proc_filter, case=False, na=False)]
            else:
                df_filtrado = df
            st.dataframe(df_filtrado)

    elif aba_sel == "Jurisprudências":
        df = pd.DataFrame(st.session_state.jurisprudencias)
        if df.empty:
            st.info("Nenhuma jurisprudência cadastrada.")
        else:
            filtro_tribunal = st.multiselect("Filtrar por Tribunal", options=df['tribunal'].unique(), default=list(df['tribunal'].unique()))
            df_filtrado = df[df['tribunal'].isin(filtro_tribunal)]
            st.dataframe(df_filtrado)

    elif aba_sel == "Agenda":
        df = pd.DataFrame(st.session_state.agenda)
        if df.empty:
            st.info("Nenhum evento agendado.")
        else:
            st.dataframe(df)

def aba_gerenciar_usuarios():
    st.title("👥 Gerenciar Usuários (Master Only)")
    # Exibir tabela com usuários (somente login e permissão, não exibir senhas para segurança)
    usuarios_visiveis = [{"usuario": u["usuario"], "permissao": u["permissao"]} for u in usuarios_db]
    st.write(pd.DataFrame(usuarios_visiveis))

    with st.form("form_novo_usuario"):
        novo_user = st.text_input("Novo Usuário")
        nova_senha = st.text_input("Senha", type="password")
        permissao = st.selectbox("Permissão", ["normal", "master"])
        enviar = st.form_submit_button("Cadastrar")

        if enviar:
            if novo_user.strip() == "" or nova_senha.strip() == "":
                st.error("Usuário e senha são obrigatórios.")
                return
            # Verificar se usuário já existe
            if any(u["usuario"].lower() == novo_user.lower() for u in usuarios_db):
                st.error("Usuário já existe.")
                return
            usuarios_db.append({
                "usuario": novo_user.strip().lower(),
                "senha": nova_senha.strip(),
                "permissao": permissao
            })
            st.success("Usuário cadastrado com sucesso!")

# --- Controle das abas ---
if opcao == "Início":
    aba_inicio()

elif opcao == "Cadastrar Processo":
    aba_cadastrar_processo()

elif opcao == "Movimentações":
    aba_movimentacoes()

elif opcao == "Despachos":
    aba_despachos()

elif opcao == "Jurisprudência":
    aba_jurisprudencia()

elif opcao == "Agenda":
    aba_agenda()

elif opcao == "Relatórios":
    aba_relatorios()

elif opcao == "Gerenciar Usuários" and usuario_eh_master():
    aba_gerenciar_usuarios()
