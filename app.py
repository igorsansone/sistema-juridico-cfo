import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from streamlit_option_menu import option_menu

# Funções de persistência
def carregar_dados(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_dados(nome_arquivo, dados):
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Carregando dados
processos = carregar_dados("dados_processos.json")
movimentacoes = carregar_dados("dados_movimentacoes.json")
despachos = carregar_dados("dados_despachos.json")
jurisprudencias = carregar_dados("dados_jurisprudencia.json")
agenda = carregar_dados("dados_agenda.json")
usuarios = carregar_dados("usuarios.json")

st.set_page_config(page_title="Sistema Judicial", layout="wide")

with st.sidebar:
    menu = option_menu("Menu", ["Início", "Processos", "Movimentações", "Despachos", "Jurisprudência", "Agenda", "Histórico", "Usuários"], icons=["house", "folder", "shuffle", "file-earmark-text", "book", "calendar", "clock-history", "people"], default_index=0)

if menu == "Início":
    st.title("📌 Sistema Judicial - Painel Principal")
    st.write("Bem-vindo ao sistema judicial.")

if menu == "Processos":
    st.header("📁 Cadastro de Processos")
    with st.form("form_processo"):
        numero = st.text_input("Número do Processo")
        autor = st.text_input("Autor")
        reu = st.text_input("Réu")
        vara = st.text_input("Vara")
        data_cadastro = datetime.now().strftime("%d/%m/%Y %H:%M")
        submitted = st.form_submit_button("Salvar Processo")
        if submitted:
            processos.append({"numero": numero, "autor": autor, "reu": reu, "vara": vara, "data": data_cadastro})
            salvar_dados("dados_processos.json", processos)
            st.success("Processo salvo com sucesso!")
    st.write("### Processos Cadastrados")
    st.dataframe(pd.DataFrame(processos))

if menu == "Movimentações":
    st.header("🔁 Movimentações")
    with st.form("form_movimentacao"):
        numero_processo = st.text_input("Número do Processo")
        descricao = st.text_area("Descrição da Movimentação")
        prazo = st.date_input("Prazo")
        submitted = st.form_submit_button("Salvar Movimentação")
        if submitted:
            movimentacoes.append({"processo": numero_processo, "descricao": descricao, "prazo": prazo.strftime("%d/%m/%Y")})
            salvar_dados("dados_movimentacoes.json", movimentacoes)
            st.success("Movimentação salva com sucesso!")
    st.write("### Movimentações Cadastradas")
    st.dataframe(pd.DataFrame(movimentacoes))

if menu == "Despachos":
    st.header("📄 Despachos")
    with st.form("form_despacho"):
        numero_processo = st.text_input("Número do Processo para Despacho")
        despacho_texto = st.text_area("Texto do Despacho")
        data_despacho = datetime.now().strftime("%d/%m/%Y %H:%M")
        submitted = st.form_submit_button("Salvar Despacho")
        if submitted:
            despachos.append({"processo": numero_processo, "texto": despacho_texto, "data": data_despacho})
            salvar_dados("dados_despachos.json", despachos)
            st.success("Despacho salvo com sucesso!")
    st.write("### Despachos Cadastrados")
    st.dataframe(pd.DataFrame(despachos))

if menu == "Jurisprudência":
    st.header("📚 Cadastro de Jurisprudência")
    with st.form("form_jurisprudencia"):
        tribunal = st.selectbox("Tribunal", ["TRF", "JF"])
        ementa = st.text_area("Ementa")
        referencia = st.text_input("Referência")
        submitted = st.form_submit_button("Salvar Jurisprudência")
        if submitted:
            jurisprudencias.append({"tribunal": tribunal, "ementa": ementa, "referencia": referencia})
            salvar_dados("dados_jurisprudencia.json", jurisprudencias)
            st.success("Jurisprudência salva com sucesso!")
    st.write("### Jurisprudências Cadastradas")
    st.dataframe(pd.DataFrame(jurisprudencias))

if menu == "Agenda":
    st.header("🗓️ Agenda de Reuniões e Eventos")
    with st.form("form_agenda"):
        titulo = st.text_input("Título")
        data_evento = st.date_input("Data")
        hora = st.text_input("Hora")
        local = st.text_input("Local")
        participante = st.text_input("Representante/Advogado")
        presencial = st.selectbox("Modalidade", ["Presencial", "Online"])
        submitted = st.form_submit_button("Salvar Evento")
        if submitted:
            agenda.append({"titulo": titulo, "data": data_evento.strftime("%d/%m/%Y"), "hora": hora, "local": local, "participante": participante, "modalidade": presencial})
            salvar_dados("dados_agenda.json", agenda)
            st.success("Evento salvo com sucesso!")
    st.write("### Eventos Agendados")
    st.dataframe(pd.DataFrame(agenda))

if menu == "Histórico":
    st.header("📜 Histórico do Processo")
    numero_busca = st.text_input("Informe o número do processo para ver histórico")
    if numero_busca:
        historico = []
        for m in movimentacoes:
            if m['processo'] == numero_busca:
                historico.append({"tipo": "Movimentação", **m})
        for d in despachos:
            if d['processo'] == numero_busca:
                historico.append({"tipo": "Despacho", **d})
        historico_ordenado = sorted(historico, key=lambda x: x.get("data", ""))
        st.write("### Histórico do Processo")
        st.dataframe(pd.DataFrame(historico_ordenado))

if menu == "Usuários":
    st.header("👤 Gerenciamento de Usuários")
    with st.form("form_usuario"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        perfil = st.selectbox("Perfil", ["Administrador", "Usuário Comum"])
        submitted = st.form_submit_button("Salvar Usuário")
        if submitted:
            usuarios.append({"nome": nome, "email": email, "perfil": perfil})
            salvar_dados("usuarios.json", usuarios)
            st.success("Usuário cadastrado com sucesso!")
    st.write("### Lista de Usuários")
    st.dataframe(pd.DataFrame(usuarios))

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido por Igor Sansone - Setor de Secretaria")
