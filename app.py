import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from streamlit_option_menu import option_menu

st.set_page_config(layout="wide")
[
  {
    "usuario": "admin",
    "senha": "123456"
  }
]


# Funções de utilidade para carregar/salvar dados
def carregar_dados(arquivo, padrao):
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return padrao

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Arquivos de dados
ARQUIVOS = {
    "processos": "dados_processos.json",
    "movimentacoes": "dados_movimentacoes.json",
    "agenda": "dados_agenda.json",
    "despachos": "dados_despachos.json",
    "jurisprudencia": "dados_jurisprudencia.json",
    "historico": "dados_historico.json",
    "usuarios": "usuarios.json"
}

# Carregar dados
dados = {chave: carregar_dados(ARQUIVOS[chave], []) for chave in ARQUIVOS}

# --- Login ---
st.sidebar.title("Login")
usuario = st.sidebar.text_input("Usuário")
senha = st.sidebar.text_input("Senha", type="password")
botao_login = st.sidebar.button("Entrar")

if botao_login:
    usuarios = dados["usuarios"]
    usuario_valido = next((u for u in usuarios if u["usuario"] == usuario and u["senha"] == senha), None)
    if usuario_valido:
        st.session_state["logado"] = True
        st.session_state["usuario"] = usuario
    else:
        st.sidebar.error("Usuário ou senha inválidos")

if st.session_state.get("logado"):

    with st.sidebar:
        selecionado = option_menu("Menu Principal", [
            "Início", "Processos", "Movimentações", "Despachos", "Jurisprudência",
            "Agenda", "Relatórios", "Histórico", "Usuários"
        ], icons=['house', 'folder', 'repeat', 'file-earmark-text', 'book', 
                  'calendar3', 'bar-chart', 'clock-history', 'person-badge'], menu_icon="cast")

    st.markdown(f"### Bem-vindo, {st.session_state['usuario']}")

    # --- Início ---
    if selecionado == "Início":
        st.subheader("Painel Geral")
        st.write("Resumo dos processos, movimentações, prazos e eventos.")
        st.metric("Total de Processos", len(dados["processos"]))
        st.metric("Movimentações", len(dados["movimentacoes"]))
        st.metric("Despachos", len(dados["despachos"]))
        st.metric("Eventos na Agenda", len(dados["agenda"]))

    # --- Processos ---
    if selecionado == "Processos":
        st.subheader("Cadastro de Processos")
        with st.form("cadastro_processo"):
            numero = st.text_input("Número do Processo")
            autor = st.text_input("Autor")
            reu = st.text_input("Réu")
            vara = st.text_input("Vara")
            data = st.date_input("Data de Distribuição", format="DD/MM/YYYY")
            btn = st.form_submit_button("Salvar")
            if btn:
                novo = {"numero": numero, "autor": autor, "reu": reu, "vara": vara, "data": data.strftime("%d/%m/%Y")}
                dados["processos"].append(novo)
                salvar_dados(ARQUIVOS["processos"], dados["processos"])
                st.success("Processo cadastrado!")

        st.dataframe(pd.DataFrame(dados["processos"]))

    # --- Movimentações ---
    if selecionado == "Movimentações":
        st.subheader("Registro de Movimentações")
        with st.form("form_movimentacao"):
            numero = st.text_input("Número do Processo")
            descricao = st.text_area("Descrição")
            prazo = st.date_input("Prazo", format="DD/MM/YYYY")
            btn = st.form_submit_button("Registrar")
            if btn:
                nova = {"numero": numero, "descricao": descricao, "prazo": prazo.strftime("%d/%m/%Y")}
                dados["movimentacoes"].append(nova)
                salvar_dados(ARQUIVOS["movimentacoes"], dados["movimentacoes"])
                st.success("Movimentação registrada!")

        st.dataframe(pd.DataFrame(dados["movimentacoes"]))

    # --- Despachos ---
    if selecionado == "Despachos":
        st.subheader("Despachos")
        with st.form("form_despacho"):
            numero = st.text_input("Número do Processo")
            texto = st.text_area("Texto do Despacho")
            providencias = st.text_input("Providências")
            btn = st.form_submit_button("Salvar Despacho")
            if btn:
                novo = {"numero": numero, "texto": texto, "providencias": providencias, "data": datetime.now().strftime("%d/%m/%Y %H:%M")}
                dados["despachos"].append(novo)
                salvar_dados(ARQUIVOS["despachos"], dados["despachos"])
                st.success("Despacho salvo!")

        st.dataframe(pd.DataFrame(dados["despachos"]))

    # --- Jurisprudência ---
    if selecionado == "Jurisprudência":
        st.subheader("Cadastro de Jurisprudência")
        with st.form("form_juris"):
            tribunal = st.selectbox("Tribunal", ["JF", "TRF"])
            tema = st.text_input("Tema")
            ementa = st.text_area("Ementa")
            btn = st.form_submit_button("Salvar Jurisprudência")
            if btn:
                novo = {"tribunal": tribunal, "tema": tema, "ementa": ementa}
                dados["jurisprudencia"].append(novo)
                salvar_dados(ARQUIVOS["jurisprudencia"], dados["jurisprudencia"])
                st.success("Jurisprudência cadastrada!")

        st.dataframe(pd.DataFrame(dados["jurisprudencia"]))

    # --- Agenda ---
    if selecionado == "Agenda":
        st.subheader("Agenda de Compromissos")
        with st.form("form_agenda"):
            data = st.date_input("Data")
            hora = st.time_input("Hora")
            local = st.text_input("Local")
            representante = st.text_input("Advogado/Representante")
            descricao = st.text_area("Descrição")
            btn = st.form_submit_button("Agendar")
            if btn:
                novo = {"data": data.strftime("%d/%m/%Y"), "hora": hora.strftime("%H:%M"),
                        "local": local, "representante": representante, "descricao": descricao}
                dados["agenda"].append(novo)
                salvar_dados(ARQUIVOS["agenda"], dados["agenda"])
                st.success("Evento agendado!")

        st.dataframe(pd.DataFrame(dados["agenda"]))

    # --- Relatórios ---
    if selecionado == "Relatórios":
        st.subheader("Relatórios Gerais")
        st.write("Relatórios por tipo, data, vara etc. (exemplo a seguir)")
        df = pd.DataFrame(dados["processos"])
        st.bar_chart(df['vara'].value_counts())

    # --- Histórico ---
    if selecionado == "Histórico":
        st.subheader("Histórico do Processo")
        numero = st.text_input("Informe o número do processo:")
        if numero:
            historico = []
            for aba in ["processos", "movimentacoes", "despachos"]:
                historico += [f"{aba.title()}: {d}" for d in dados[aba] if d.get("numero") == numero]
            st.write("\n\n".join(historico) if historico else "Nenhum histórico encontrado.")

    # --- Usuários (somente se master) ---
    if selecionado == "Usuários":
        st.subheader("Gerenciar Usuários")
        with st.form("form_usuario"):
            novo_usuario = st.text_input("Novo Usuário")
            nova_senha = st.text_input("Senha", type="password")
            btn = st.form_submit_button("Cadastrar Usuário")
            if btn:
                dados["usuarios"].append({"usuario": novo_usuario, "senha": nova_senha})
                salvar_dados(ARQUIVOS["usuarios"], dados["usuarios"])
                st.success("Usuário cadastrado!")

        st.write(pd.DataFrame(dados["usuarios"]))

    # Rodapé
    st.markdown("<hr><center><sub>Desenvolvido por Igor Sansone - Setor de Secretaria</sub></center>", unsafe_allow_html=True)

else:
    st.warning("Faça login para acessar o sistema.")
