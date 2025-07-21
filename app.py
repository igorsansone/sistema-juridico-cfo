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
        st.success("Jurisprudência cadastrada com sucesso.")

def despachos():
    st.title("📄 Cadastro de Despachos")

    # Puxar lista de processos cadastrados para usar no selectbox
    opcoes_processos = [p["Número"] for p in st.session_state.processos]
    if not opcoes_processos:
        st.info("Cadastre um processo antes de inserir despachos.")
        return

    with st.form("form_despacho"):
        numero_processo = st.selectbox("Número do Processo", opcoes_processos)
        data_despacho = st.date_input("Data do Despacho", value=datetime.today())
        texto_despacho = st.text_area("Texto do Despacho")
        submit = st.form_submit_button("Salvar Despacho")

    if submit:
        if texto_despacho.strip() == "":
            st.error("O texto do despacho não pode ficar vazio.")
            return
        st.session_state.despachos.append({
            "Número": numero_processo,
            "Data": data_despacho.strftime("%d/%m/%Y"),
            "Texto": texto_despacho
        })
        st.success("Despacho cadastrado com sucesso.")

def movimentacoes():
    st.title("📑 Cadastro de Movimentações")

    opcoes_processos = [p["Número"] for p in st.session_state.processos]
    if not opcoes_processos:
        st.info("Cadastre um processo antes de inserir movimentações.")
        return

    with st.form("form_movimentacao"):
        numero_processo = st.selectbox("Número do Processo", opcoes_processos)
        data_movimentacao = st.date_input("Data da Movimentação", value=datetime.today())
        descricao_movimentacao = st.text_input("Descrição da Movimentação")
        prazo_movimentacao = st.text_input("Prazo (dd/mm/aaaa)")
        submit = st.form_submit_button("Salvar Movimentação")

    if submit:
        if descricao_movimentacao.strip() == "":
            st.error("A descrição da movimentação não pode ficar vazia.")
            return
        # Validar prazo
        try:
            prazo_dt = datetime.strptime(prazo_movimentacao, "%d/%m/%Y")
            prazo_str = prazo_dt.strftime("%d/%m/%Y")
        except:
            st.error("Data de prazo inválida, use o formato dd/mm/aaaa.")
            return
        st.session_state.movimentacoes.append({
            "Número": numero_processo,
            "Data": data_movimentacao.strftime("%d/%m/%Y"),
            "Descrição": descricao_movimentacao,
            "Prazo": prazo_str
        })
        st.success("Movimentação cadastrada com sucesso.")

def agenda():
    st.title("📆 Agenda")

    # Formulário para cadastro/edição de evento
    with st.form("form_agenda"):
        data_evento = st.date_input("Data do Evento", value=datetime.today())
        hora_evento = st.text_input("Hora (HH:MM)", max_chars=5, help="Formato 24h, ex: 14:30")
        evento = st.text_input("Evento")
        descricao = st.text_area("Descrição")
        local = st.text_input("Local da Reunião")
        advogado_representante = st.text_input("Advogado/Representante no Ato")
        modalidade = st.selectbox("Modalidade", ["Presencial", "Online"])
        concluido = st.checkbox("Evento Concluído")
        submit = st.form_submit_button("Salvar Evento")

    if submit:
        # Validar formato da hora (opcional)
        try:
            if hora_evento:
                datetime.strptime(hora_evento, "%H:%M")
        except:
            st.error("Formato de hora inválido. Use HH:MM no formato 24h.")
            return
        
        novo_evento = {
            "Data": data_evento.strftime("%d/%m/%Y"),
            "Hora": hora_evento,
            "Evento": evento,
            "Descrição": descricao,
            "Local": local,
            "Advogado/Representante": advogado_representante,
            "Modalidade": modalidade,
            "Concluído": concluido
        }
        st.session_state.agenda.append(novo_evento)
        st.success("Evento adicionado à agenda.")
        st.experimental_rerun()

    # Mostrar lista de eventos cadastrados
    if st.session_state.agenda:
        st.markdown("### Eventos Cadastrados")

        # Criar DataFrame com os dados da agenda
        df = pd.DataFrame(st.session_state.agenda)

        # Para facilitar edição e exclusão, vamos iterar pelos eventos
        for idx, evento in df.iterrows():
            st.markdown(f"**{evento['Data']} {evento['Hora']} - {evento['Evento']}**")
            st.write(f"**Descrição:** {evento['Descrição']}")
            st.write(f"**Local:** {evento['Local']}")
            st.write(f"**Advogado/Representante:** {evento['Advogado/Representante']}")
            st.write(f"**Modalidade:** {evento['Modalidade']}")
            st.write(f"**Concluído:** {'✅' if evento['Concluído'] else '❌'}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Editar {idx}", key=f"editar_{idx}"):
                    # Carregar evento para edição - preenche campos do formulário
                    st.session_state.evento_editando = idx
                    st.experimental_rerun()
            with col2:
                if st.button(f"Excluir {idx}", key=f"excluir_{idx}"):
                    st.session_state.agenda.pop(idx)
                    st.success("Evento excluído.")
                    st.experimental_rerun()

    # Se estiver editando um evento, carregar dados no formulário
    if "evento_editando" in st.session_state:
        idx = st.session_state.evento_editando
        if 0 <= idx < len(st.session_state.agenda):
            evento_edit = st.session_state.agenda[idx]

            with st.form("form_edicao_agenda"):
                data_evento = st.date_input("Data do Evento", value=datetime.strptime(evento_edit["Data"], "%d/%m/%Y"))
                hora_evento = st.text_input("Hora (HH:MM)", value=evento_edit["Hora"], max_chars=5)
                evento = st.text_input("Evento", value=evento_edit["Evento"])
                descricao = st.text_area("Descrição", value=evento_edit["Descrição"])
                local = st.text_input("Local da Reunião", value=evento_edit["Local"])
                advogado_representante = st.text_input("Advogado/Representante no Ato", value=evento_edit["Advogado/Representante"])
                modalidade = st.selectbox("Modalidade", ["Presencial", "Online"], index=0 if evento_edit["Modalidade"]=="Presencial" else 1)
                concluido = st.checkbox("Evento Concluído", value=evento_edit["Concluído"])

                submit_edit = st.form_submit_button("Salvar Alterações")

            if submit_edit:
                # Validação da hora
                try:
                    if hora_evento:
                        datetime.strptime(hora_evento, "%H:%M")
                except:
                    st.error("Formato de hora inválido. Use HH:MM no formato 24h.")
                    return
                
                st.session_state.agenda[idx] = {
                    "Data": data_evento.strftime("%d/%m/%Y"),
                    "Hora": hora_evento,
                    "Evento": evento,
                    "Descrição": descricao,
                    "Local": local,
                    "Advogado/Representante": advogado_representante,
                    "Modalidade": modalidade,
                    "Concluído": concluido
                }
                st.success("Evento atualizado com sucesso.")
                del st.session_state.evento_editando
                st.experimental_rerun()


def historico():
    st.title("📜 Histórico do Processo")

    opcoes_processos = [p["Número"] for p in st.session_state.processos]
    if not opcoes_processos:
        st.info("Nenhum processo cadastrado.")
        return

    numero = st.selectbox("Selecione o número do processo", opcoes_processos)

    if numero:
        hist = []
        # Buscar movimentações
        for m in st.session_state.movimentacoes:
            if m["Número"] == numero:
                hist.append({
                    "Data": m.get("Data", ""),
                    "Evento": "Movimentação",
                    "Detalhes": m.get("Descrição", "")
                })
        # Buscar despachos
        for d in st.session_state.despachos:
            if d["Número"] == numero:
                hist.append({
                    "Data": d.get("Data", ""),
                    "Evento": "Despacho",
                    "Detalhes": d.get("Texto", "")
                })
        # Ordenar cronologicamente
        hist_sorted = sorted(hist, key=lambda x: datetime.strptime(x["Data"], "%d/%m/%Y") if x["Data"] else datetime.min)
        if hist_sorted:
            df = pd.DataFrame(hist_sorted)
            st.dataframe(df)
        else:
            st.info("Nenhuma movimentação ou despacho encontrado para esse processo.")

# Menu lateral e roteamento
def main():
    if not st.session_state.logado:
        tela_login()
    else:
        escolha = option_menu(
            menu_title="Menu",
            options=["Início", "Cadastro Processo", "Jurisprudência", "Despachos", "Movimentações", "Agenda", "Histórico", "Sair"],
            icons=["house", "file-earmark-text", "book", "file-text", "list-task", "calendar", "clock-history", "box-arrow-right"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )

        if escolha == "Início":
            inicio()
        elif escolha == "Cadastro Processo":
            cadastro_processo()
        elif escolha == "Jurisprudência":
            cadastro_jurisprudencia()
        elif escolha == "Despachos":
            despachos()
        elif escolha == "Movimentações":
            movimentacoes()
        elif escolha == "Agenda":
            agenda()
        elif escolha == "Histórico":
            historico()
        elif escolha == "Sair":
            st.session_state.logado = False
            st.session_state.usuario_logado = None
            st.experimental_rerun()

        st.markdown("""<div class="footer">Desenvolvido por Igor Sansone - Setor de Secretaria - Para uso CFO</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
