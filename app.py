import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu
import altair as alt
import streamlit.components.v1 as components

# Função para forçar rerun (usar se precisar)
def forcar_rerun():
    params = st.experimental_get_query_params()
    count = int(params["count"][0]) if "count" in params else 0
    st.experimental_set_query_params(count=str(count + 1))

st.set_page_config(layout="wide", page_title="Processos Eleição CROS 2025 - CFO")

# CSS customizado (mantém o seu estilo)
def aplicar_css():
    st.markdown("""
    <style>
    body {
        font-family: 'Segoe UI', sans-serif;
    }
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #0B3D91;
        color: white;
        text-align: center;
        padding: 6px 0;
        font-weight: 600;
        font-size: 14px;
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)
aplicar_css()

# Listas fixas para selectboxes
tipos_acao = [
    "", "Ação Civil Pública", "Ação Popular", "Ação de Improbidade Administrativa", "Mandado de Segurança",
    "Ação Declaratória de Nulidade de Ato Administrativo", "Ação Anulatória de Ato Administrativo",
    "Ação de Cobrança contra a Administração Pública", "Ação de Obrigação de Fazer contra o Poder Público",
    "Ação Indenizatória por Atos da Administração", "Ação de Responsabilidade por Dano ao Erário",
    "Ação de Responsabilização Ética de Servidor Público", "Ação Ética contra Órgão da Administração",
    "Ação Ética sobre Conduta Funcional de Agente Público", "Ação de Controle de Constitucionalidade",
    "Ação Direta de Inconstitucionalidade", "Ação Declaratória de Constitucionalidade",
    "Ação Direta de Inconstitucionalidade por Omissão", "Ação Rescisória contra Decisões Administrativas",
    "Ação Cautelar em Face da Administração", "Ação de Intervenção Federal",
    "Ação sobre Licitações e Contratos Administrativos", "Ação sobre Concurso Público",
    "Ação sobre Servidores Públicos Federais", "Ação Previdenciária contra o INSS",
    "Ação sobre Saúde Pública (fornecimento de medicamentos etc.)", "Ação sobre Direito à Educação Pública",
    "Ação Coletiva sobre Políticas Públicas", "Outras"
]

recursos = [
    "", "Apelação", "Agravo de Instrumento", "Embargos de Declaração", "Recurso Especial",
    "Recurso Extraordinário", "Mandado de Segurança", "Habeas Corpus", "Recurso Ordinário",
    "Agravo Interno", "Embargos Infringentes", "Embargos à Execução", "Revisão Criminal",
    "Correição Parcial", "Recurso em Sentido Estrito", "Conflito de Competência", "Recurso Adesivo",
    "Agravo Regimental", "Outros"
]

locais_ajuizamento = ["", "JF", "TRF1", "TRF2", "TRF3", "TRF4", "TRF5", "TRF6", "STJ", "STF"]

# Inicialização das session states usados
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "usuarios" not in st.session_state:
    st.session_state.usuarios = [
        {"nome": "Admin", "usuario": "admin", "senha": "admin123", "permissao": "master"},
        {"nome": "Usuário", "usuario": "user", "senha": "123", "permissao": "normal"}
    ]
if "processos" not in st.session_state:
    st.session_state.processos = []
if "jurisprudencias" not in st.session_state:
    st.session_state.jurisprudencias = []
if "despachos" not in st.session_state:
    st.session_state.despachos = []
if "movimentacoes" not in st.session_state:
    st.session_state.movimentacoes = []
if "agenda" not in st.session_state:
    st.session_state.agenda = []
if "autores" not in st.session_state:
    st.session_state.autores = [{"nome": "", "cpf_cnpj": ""}]
if "reus" not in st.session_state:
    st.session_state.reus = [{"nome": "", "cpf_cnpj": ""}]

# Funções básicas
def validar_login(usuario, senha):
    for u in st.session_state.usuarios:
        if u["usuario"] == usuario and u["senha"] == senha:
            return u
    return None

def usuario_eh_master():
    user = st.session_state.usuario_logado
    for u in st.session_state.usuarios:
        if u["usuario"] == user:
            return u["permissao"] == "master"
    return False

def rerun():
    st.experimental_rerun()

# --- Telas ---

def tela_login():
    st.title("🔐 Login - Sistema Jurídico CFO")
    with st.form("form_login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
    if submit:
        user = validar_login(usuario, senha)
        if user:
            st.session_state.logado = True
            st.session_state.usuario_logado = usuario
            st.success(f"Bem-vindo, {user['nome']}!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos.")

def inicio():
    st.title("🏠 Painel Inicial - CFO Jurídico")

    processos = st.session_state.processos
    agenda = st.session_state.agenda
    movs = st.session_state.movimentacoes

    hoje = pd.Timestamp(datetime.today().date())

    # --- FILTROS ---
    st.sidebar.subheader("Filtros - Página Inicial")

    prazo_filtro = st.sidebar.slider("Prazos a vencer nos próximos dias:", min_value=1, max_value=60, value=30)

    tribunais_oficiais = ["JF", "TRF1", "TRF2", "TRF3", "TRF4", "TRF5", "TRF6"]
    tribunais_selecionados = st.sidebar.multiselect("Tribunais para o quantitativo:", options=tribunais_oficiais, default=tribunais_oficiais)

    st.sidebar.markdown("---")
    st.sidebar.write(f"Usuário logado: **{st.session_state.usuario_logado}**")

    st.subheader("📅 Próximas Reuniões")

    if agenda:
        df_agenda = pd.DataFrame(agenda)
        df_agenda["Data"] = pd.to_datetime(df_agenda["Data"], format="%d/%m/%Y", errors='coerce')
        proximas = df_agenda[df_agenda["Data"] >= hoje].sort_values("Data")

        if proximas.empty:
            st.info("Nenhuma reunião agendada para os próximos dias.")
        else:
            prox_reuniao = proximas.iloc[0]
            dias_para_reuniao = (prox_reuniao["Data"] - hoje).days
            st.markdown(f"**Próxima reunião:** {prox_reuniao['Evento']} em {prox_reuniao['Data'].strftime('%d/%m/%Y')} ({dias_para_reuniao} dias restantes)")
            st.write(prox_reuniao["Descrição"])

            if len(proximas) > 1:
                st.table(proximas.iloc[1:][["Data", "Evento", "Descrição"]].reset_index(drop=True))
    else:
        st.info("Nenhuma reunião cadastrada.")

    st.markdown("---")

    st.subheader("⏳ Prazos a Vencer")

    if movs and processos:
        df_movs = pd.DataFrame(movs)
        df_movs["Prazo"] = pd.to_datetime(df_movs["Prazo"], format="%d/%m/%Y", errors='coerce')

        filtro_prazo_final = hoje + pd.Timedelta(days=prazo_filtro)
        prazos_abertos = df_movs[(df_movs["Prazo"].notnull()) & (df_movs["Prazo"] >= hoje) & (df_movs["Prazo"] <= filtro_prazo_final)].copy()

        if prazos_abertos.empty:
            st.info(f"Nenhum prazo vencendo nos próximos {prazo_filtro} dias.")
        else:
            df_proc = pd.DataFrame(processos)
            df_proc["Número"] = df_proc["Número"].astype(str)
            prazos_abertos["Número"] = prazos_abertos["Número"].astype(str)
            df_join = prazos_abertos.merge(df_proc, on="Número", how="left", suffixes=("_mov", "_proc"))

            df_join = df_join.sort_values("Prazo")
            df_join["Dias Restantes"] = (df_join["Prazo"] - hoje).dt.days

            def cor_prazo(dias):
                if dias > 15:
                    return "background-color: #d4edda"  # verde claro
                elif 10 <= dias <= 15:
                    return "background-color: #fff3cd"  # amarelo claro
                else:
                    return "background-color: #f8d7da"  # vermelho claro

            st.dataframe(
                df_join[["Número", "Assunto", "Prazo", "Descrição", "Dias Restantes"]]
                .style.applymap(lambda v: cor_prazo(v), subset=["Dias Restantes"])
            )
    else:
        st.info("Nenhuma movimentação ou processo cadastrado.")

    st.markdown("---")

    st.subheader("📊 Quantitativo de Processos por Tribunal")

    if processos:
        df = pd.DataFrame(processos)
        if "Local Ajuizamento" in df.columns:
            df_filtrado = df[df["Local Ajuizamento"].isin(tribunais_selecionados)]
            contagem = df_filtrado["Local Ajuizamento"].value_counts().reindex(tribunais_selecionados, fill_value=0)
            contagem_df = contagem.reset_index()
            contagem_df.columns = ["Tribunal", "Quantidade"]

            cols = st.columns(len(contagem_df))
            cores = ["#007BFF", "#28A745", "#FFC107", "#DC3545", "#17A2B8", "#6F42C1", "#FD7E14"]

            for i, row in contagem_df.iterrows():
                with cols[i]:
                    st.markdown(f"""
                        <div style="background-color: {cores[i % len(cores)]}; padding: 20px; border-radius: 10px; text-align: center; color: white;">
                            <h3>{row['Quantidade']}</h3>
                            <p>{row['Tribunal']}</p>
                        </div>
                    """, unsafe_allow_html=True)

            chart = alt.Chart(contagem_df).mark_bar().encode(
                x=alt.X("Tribunal", sort=tribunais_selecionados),
                y="Quantidade",
                tooltip=["Tribunal", "Quantidade"],
                color=alt.Color("Quantidade", scale=alt.Scale(scheme="blues"))
            ).properties(width=600, height=300)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Coluna 'Local Ajuizamento' não encontrada nos processos.")
    else:
        st.info("Nenhum processo cadastrado.")

def cadastro_processo():
    st.title("📝 Cadastro / Edição de Processo")

    if "autores" not in st.session_state:
        st.session_state.autores = [{"nome": "", "cpf_cnpj": ""}]
    if "reus" not in st.session_state:
        st.session_state.reus = [{"nome": "", "cpf_cnpj": ""}]

    st.write("### Parte Autora")
    for i in range(len(st.session_state.autores)):
        st.session_state.autores[i]["nome"] = st.text_input(f"Nome do Autor {i+1}", value=st.session_state.autores[i]["nome"], key=f"autor_nome_{i}")
        st.session_state.autores[i]["cpf_cnpj"] = st.text_input(f"CPF/CNPJ do Autor {i+1}", value=st.session_state.autores[i]["cpf_cnpj"], key=f"autor_cpf_{i}")
    if st.button("Adicionar Autor"):
        st.session_state.autores.append({"nome": "", "cpf_cnpj": ""})

    st.write("### Parte Ré")
    for i in range(len(st.session_state.reus)):
        st.session_state.reus[i]["nome"] = st.text_input(f"Nome do Réu {i+1}", value=st.session_state.reus[i]["nome"], key=f"reu_nome_{i}")
        st.session_state.reus[i]["cpf_cnpj"] = st.text_input(f"CPF/CNPJ do Réu {i+1}", value=st.session_state.reus[i]["cpf_cnpj"], key=f"reu_cpf_{i}")
    if st.button("Adicionar Réu"):
        st.session_state.reus.append({"nome": "", "cpf_cnpj": ""})

    numero_default = st.session_state.get("numero_processo", "")
    assunto_default = st.session_state.get("assunto", "")
    data_distribuicao_default = st.session_state.get("data_distribuicao", datetime.today())
    tipo_acao_default = st.session_state.get("tipo_acao", tipos_acao[0])
    recurso_default = st.session_state.get("recurso", recursos[0])
    local_ajuizamento_default = st.session_state.get("local_ajuizamento", locais_ajuizamento[0])
    turma_vara_plenario_default = st.session_state.get("turma_vara_plenario", "")
    nome_magistrado_default = st.session_state.get("nome_magistrado", "")
    telefone_gabinete_default = st.session_state.get("telefone_gabinete", "")

    with st.form("form_processo"):
        numero = st.text_input("Número do Processo", value=numero_default)
        assunto = st.text_input("Assunto", value=assunto_default)
        data_distribuicao = st.date_input("Data de Distribuição", value=data_distribuicao_default)
        tipo_acao = st.selectbox("Tipo de Ação", tipos_acao, index=tipos_acao.index(tipo_acao_default) if tipo_acao_default in tipos_acao else 0)
        recurso = st.selectbox("Recurso", recursos, index=recursos.index(recurso_default) if recurso_default in recursos else 0)
        local_ajuizamento = st.selectbox("Local onde foi ajuizado", locais_ajuizamento, index=locais_ajuizamento.index(local_ajuizamento_default) if local_ajuizamento_default in locais_ajuizamento else 0)
        turma_vara_plenario = st.text_input("Turma / Vara / Plenário", value=turma_vara_plenario_default)
        nome_magistrado = st.text_input("Nome do Magistrado ou Ministro", value=nome_magistrado_default)
        telefone_gabinete = st.text_input("Telefone do Gabinete", value=telefone_gabinete_default)

        submit = st.form_submit_button("Salvar Processo")

    if submit:
        if numero.strip() == "":
            st.error("O número do processo é obrigatório.")
            return
        # Verificar se já existe
        achou = False
        for i, p in enumerate(st.session_state.processos):
            if p["Número"] == numero:
                # Atualizar processo existente
                st.session_state.processos[i] = {
                    "Número": numero,
                    "Assunto": assunto,
                    "Data Distribuição": data_distribuicao.strftime("%d/%m/%Y"),
                    "Tipo de Ação": tipo_acao,
                    "Recurso": recurso,
                    "Local Ajuizamento": local_ajuizamento,
                    "Turma / Vara / Plenário": turma_vara_plenario,
                    "Nome Magistrado": nome_magistrado,
                    "Telefone Gabinete": telefone_gabinete,
                    "Autores": st.session_state.autores.copy(),
                    "Réus": st.session_state.reus.copy()
                }
                achou = True
                st.success(f"Processo {numero} atualizado com sucesso.")
                break
        if not achou:
            st.session_state.processos.append({
                "Número": numero,
                "Assunto": assunto,
                "Data Distribuição": data_distribuicao.strftime("%d/%m/%Y"),
                "Tipo de Ação": tipo_acao,
                "Recurso": recurso,
                "Local Ajuizamento": local_ajuizamento,
                "Turma / Vara / Plenário": turma_vara_plenario,
                "Nome Magistrado": nome_magistrado,
                "Telefone Gabinete": telefone_gabinete,
                "Autores": st.session_state.autores.copy(),
                "Réus": st.session_state.reus.copy()
            })
            st.success(f"Processo {numero} cadastrado com sucesso.")

def cadastro_jurisprudencia():
    st.title("📚 Cadastro de Jurisprudência")

    with st.form("form_jurisprudencia"):
        tribunal = st.selectbox("Tribunal", ["", "TRF1", "TRF2", "TRF3", "TRF4", "TRF5", "STJ", "STF"])
        processo_referencia = st.text_input("Número do Processo de Referência")
        data_decisao = st.date_input("Data da Decisão", value=datetime.today())
        ementa = st.text_area("Ementa")
        link_decisao = st.text_input("Link da Decisão")
        submit = st.form_submit_button("Salvar Jurisprudência")

    if submit:
        if processo_referencia.strip() == "":
            st.error("Número do processo de referência é obrigatório.")
            return
        st.session_state.jurisprudencias.append({
            "Tribunal": tribunal,
            "Processo Referência": processo_referencia,
            "Data Decisão": data_decisao.strftime("%d/%m/%Y"),
            "Ementa": ementa,
            "Link": link_decisao
        })
        st.success("Jurisprudência cadastrada.")

    # Busca básica
    st.subheader("🔎 Buscar Jurisprudência")
    busca = st.text_input("Digite termo para busca na ementa ou número do processo:")
    if busca:
        df_juris = pd.DataFrame(st.session_state.jurisprudencias)
        filtro = df_juris["Ementa"].str.contains(busca, case=False, na=False) | df_juris["Processo Referência"].str.contains(busca, case=False, na=False)
        resultados = df_juris[filtro]
        st.write(resultados)

def despachos():
    st.title("📄 Cadastro de Despachos")

    with st.form("form_despacho"):
        numero_processo = st.text_input("Número do Processo")
        texto_despacho = st.text_area("Texto do Despacho")
        data_despacho = st.date_input("Data do Despacho", value=datetime.today())
        submit = st.form_submit_button("Salvar Despacho")

    if submit:
        if numero_processo.strip() == "":
            st.error("Número do processo é obrigatório.")
            return
        st.session_state.despachos.append({
            "Número": numero_processo,
            "Texto": texto_despacho,
            "Data": data_despacho.strftime("%d/%m/%Y"),
            "Cadastrado por": st.session_state.usuario_logado
        })
        st.success("Despacho cadastrado.")

def movimentacoes():
    st.title("↪️ Cadastro de Movimentações")

    # Listar movimentações existentes
    df_movs = pd.DataFrame(st.session_state.movimentacoes)
    st.subheader("Movimentações Cadastradas")

    if df_movs.empty:
        st.info("Nenhuma movimentação cadastrada.")
    else:
        # Botões editar e excluir
        for idx, row in df_movs.iterrows():
            with st.expander(f"Movimentação #{idx+1} - Processo {row['Número']}"):
                st.write(f"Prazo: {row['Prazo']}")
                st.write(f"Descrição: {row['Descrição']}")
                editar = st.button(f"Editar {idx}", key=f"editar_{idx}")
                excluir = st.button(f"Excluir {idx}", key=f"excluir_{idx}")

                if excluir:
                    st.session_state.movimentacoes.pop(idx)
                    st.success("Movimentação excluída.")
                    forcar_rerun()
                if editar:
                    st.session_state.mov_edit_index = idx
                    forcar_rerun()

    # Cadastro / edição
    editando = "mov_edit_index" in st.session_state
    if editando:
        idx = st.session_state.mov_edit_index
        mov = st.session_state.movimentacoes[idx]
    else:
        mov = {"Número": "", "Prazo": "", "Descrição": ""}

    with st.form("form_movimentacao"):
        numero = st.text_input("Número do Processo", value=mov.get("Número", ""))
        prazo = st.text_input("Prazo (dd/mm/aaaa)", value=mov.get("Prazo", ""))
        descricao = st.text_area("Descrição", value=mov.get("Descrição", ""))
        submit = st.form_submit_button("Salvar Movimentação")

    if submit:
        if numero.strip() == "" or prazo.strip() == "":
            st.error("Número do processo e prazo são obrigatórios.")
            return
        # Validar data prazo
        try:
            dt_prazo = datetime.strptime(prazo, "%d/%m/%Y")
        except:
            st.error("Formato da data do prazo inválido. Use dd/mm/aaaa.")
            return

        nova_mov = {"Número": numero, "Prazo": prazo, "Descrição": descricao}
        if editando:
            st.session_state.movimentacoes[idx] = nova_mov
            st.success("Movimentação atualizada.")
            del st.session_state["mov_edit_index"]
        else:
            st.session_state.movimentacoes.append(nova_mov)
            st.success("Movimentação cadastrada.")
        forcar_rerun()

def agenda():
    st.title("📅 Agenda de Eventos")

    # Listar eventos agendados
    df_agenda = pd.DataFrame(st.session_state.agenda)
    st.subheader("Eventos Agendados")

    if df_agenda.empty:
        st.info("Nenhum evento cadastrado.")
    else:
        for idx, row in df_agenda.iterrows():
            with st.expander(f"{row['Data']} - {row['Evento']}"):
                st.write(f"Descrição: {row['Descrição']}")
                st.write(f"Local: {row.get('Local', '')}")
                st.write(f"Participantes: {row.get('Participantes', '')}")
                editar = st.button(f"Editar {idx}", key=f"editar_agenda_{idx}")
                excluir = st.button(f"Excluir {idx}", key=f"excluir_agenda_{idx}")

                if excluir:
                    st.session_state.agenda.pop(idx)
                    st.success("Evento excluído.")
                    forcar_rerun()
                if editar:
                    st.session_state.agenda_edit_index = idx
                    forcar_rerun()

    # Cadastro / edição
    editando = "agenda_edit_index" in st.session_state
    if editando:
        idx = st.session_state.agenda_edit_index
        evento = st.session_state.agenda[idx]
    else:
        evento = {"Data": "", "Evento": "", "Descrição": "", "Local": "", "Participantes": "", "Online": False}

    with st.form("form_agenda"):
        data_evento = st.date_input("Data do Evento", value=datetime.today() if evento["Data"] == "" else datetime.strptime(evento["Data"], "%d/%m/%Y"))
        nome_evento = st.text_input("Evento", value=evento.get("Evento", ""))
        descricao_evento = st.text_area("Descrição", value=evento.get("Descrição", ""))
        local_evento = st.text_input("Local", value=evento.get("Local", ""))
        participantes_evento = st.text_input("Participantes", value=evento.get("Participantes", ""))
        modalidade_online = st.checkbox("Evento Online?", value=evento.get("Online", False))
        submit = st.form_submit_button("Salvar Evento")

    if submit:
        data_str = data_evento.strftime("%d/%m/%Y")
        novo_evento = {
            "Data": data_str,
            "Evento": nome_evento,
            "Descrição": descricao_evento,
            "Local": local_evento,
            "Participantes": participantes_evento,
            "Online": modalidade_online
        }
        if editando:
            st.session_state.agenda[idx] = novo_evento
            st.success("Evento atualizado.")
            del st.session_state["agenda_edit_index"]
        else:
            st.session_state.agenda.append(novo_evento)
            st.success("Evento cadastrado.")
        forcar_rerun()

def historico():
    st.title("📜 Histórico Completo do Processo")

    num_proc = st.text_input("Digite o número do processo para ver o histórico")
    if num_proc:
        processos = st.session_state.processos
        movs = st.session_state.movimentacoes
        despachos = st.session_state.despachos
        juris = st.session_state.jurisprudencias

        proc = next((p for p in processos if p["Número"] == num_proc), None)
        if not proc:
            st.warning("Processo não encontrado.")
            return

        st.subheader("Dados do Processo")
        st.write(proc)

        st.subheader("Autores")
        for a in proc.get("Autores", []):
            st.write(f"Nome: {a.get('nome')}, CPF/CNPJ: {a.get('cpf_cnpj')}")

        st.subheader("Réus")
        for r in proc.get("Réus", []):
            st.write(f"Nome: {r.get('nome')}, CPF/CNPJ: {r.get('cpf_cnpj')}")

        st.subheader("Movimentações")
        mov_proc = [m for m in movs if m["Número"] == num_proc]
        if mov_proc:
            df_mov = pd.DataFrame(mov_proc)
            df_mov["Prazo"] = pd.to_datetime(df_mov["Prazo"], format="%d/%m/%Y", errors="coerce")
            df_mov = df_mov.sort_values("Prazo")
            st.dataframe(df_mov)
        else:
            st.info("Nenhuma movimentação cadastrada para este processo.")

        st.subheader("Despachos")
        desp_proc = [d for d in despachos if d["Número"] == num_proc]
        if desp_proc:
            df_desp = pd.DataFrame(desp_proc)
            df_desp["Data"] = pd.to_datetime(df_desp["Data"], format="%d/%m/%Y", errors="coerce")
            df_desp = df_desp.sort_values("Data")
            st.dataframe(df_desp[["Data", "Texto", "Cadastrado por"]])
        else:
            st.info("Nenhum despacho cadastrado para este processo.")

        st.subheader("Jurisprudências Relacionadas")
        juris_proc = [j for j in juris if j["Processo Referência"] == num_proc]
        if juris_proc:
            df_juris = pd.DataFrame(juris_proc)
            df_juris["Data Decisão"] = pd.to_datetime(df_juris["Data Decisão"], format="%d/%m/%Y", errors="coerce")
            df_juris = df_juris.sort_values("Data Decisão")
            st.dataframe(df_juris[["Tribunal", "Data Decisão", "Ementa", "Link"]])
        else:
            st.info("Nenhuma jurisprudência relacionada a este processo.")

def gerenciar_usuarios():
    if not usuario_eh_master():
        st.warning("Acesso restrito para usuários master.")
        return

    st.title("👥 Gerenciamento de Usuários")

    df_users = pd.DataFrame(st.session_state.usuarios)
    st.dataframe(df_users)

    with st.form("form_add_user"):
        st.write("Adicionar Novo Usuário")
        nome = st.text_input("Nome")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        permissao = st.selectbox("Permissão", ["normal", "master"])
        submit = st.form_submit_button("Adicionar Usuário")

    if submit:
        if not nome or not usuario or not senha:
            st.error("Preencha todos os campos.")
        else:
            existe = any(u["usuario"] == usuario for u in st.session_state.usuarios)
            if existe:
                st.error("Usuário já existe.")
            else:
                st.session_state.usuarios.append({
                    "nome": nome,
                    "usuario": usuario,
                    "senha": senha,
                    "permissao": permissao
                })
                st.success("Usuário adicionado.")
                forcar_rerun()

    # Excluir usuário
    usuario_excluir = st.text_input("Digite o usuário para excluir")
    if st.button("Excluir Usuário"):
        if usuario_excluir == st.session_state.usuario_logado:
            st.error("Você não pode excluir o usuário logado.")
        else:
            st.session_state.usuarios = [u for u in st.session_state.usuarios if u["usuario"] != usuario_excluir]
            st.success(f"Usuário {usuario_excluir} excluído.")
            forcar_rerun()

# --- Main ---

def main():
    if not st.session_state.logado:
        tela_login()
        return

    with st.sidebar:
        escolha = option_menu(
            menu_title="Menu Principal",
            options=["Início", "Cadastro Processo", "Cadastro Jurisprudência", "Despachos", "Movimentações", "Agenda", "Histórico", "Gerenciar Usuários", "Logout"],
            icons=["house", "file-earmark-text", "book", "file-text", "arrow-repeat", "calendar", "clock-history", "people", "box-arrow-right"],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "icon": {"color": "blue", "font-size": "20px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#0B3D91", "color": "white"},
            }
        )

    if escolha == "Início":
        inicio()
    elif escolha == "Cadastro Processo":
        cadastro_processo()
    elif escolha == "Cadastro Jurisprudência":
        cadastro_jurisprudencia()
    elif escolha == "Despachos":
        despachos()
    elif escolha == "Movimentações":
        movimentacoes()
    elif escolha == "Agenda":
        agenda()
    elif escolha == "Histórico":
        historico()
    elif escolha == "Gerenciar Usuários":
        gerenciar_usuarios()
    elif escolha == "Logout":
        st.session_state.logado = False
        st.session_state.usuario_logado = None
        st.experimental_rerun()

if __name__ == "__main__":
    main()

# Rodapé fixo
st.markdown("""
<div class="footer">
Desenvolvido por Igor Sansone - Setor de Secretaria - Sistema para uso do CFO
</div>
""", unsafe_allow_html=True)
