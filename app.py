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
    }
    .mobile-menu .nav-link {
        font-size: 20px !important;
        padding: 15px 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)
aplicar_css()

# Detecta dispositivo para eventuais ajustes (opcional)
def detectar_dispositivo():
    if "dispositivo" not in st.session_state:
        dispositivo = st.text_input("dispositivo_input", value="", key="dispositivo_input", label_visibility="hidden")
        js_code = """
        <script>
        const input = window.parent.document.querySelector('input#dispositivo_input');
        function getDeviceType() {
            const ua = navigator.userAgent;
            if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)){
                return "mobile";
            }
            return "desktop";
        }
        input.value = getDeviceType();
        input.dispatchEvent(new Event('input'));
        </script>
        """
        components.html(js_code, height=0)
        if dispositivo in ("mobile", "desktop"):
            st.session_state.dispositivo = dispositivo
            st.experimental_rerun()

detectar_dispositivo()

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
        enviar = st.form_submit_button("Salvar Processo")

    if enviar:
        novo_processo = {
            "Número": numero,
            "Parte Autora": st.session_state.autores,
            "Parte Ré": st.session_state.reus,
            "Assunto": assunto,
            "Data de Distribuição": data_distribuicao.strftime("%d/%m/%Y"),
            "Tipo de Ação": tipo_acao,
            "Recurso": recurso,
            "Local Ajuizamento": local_ajuizamento,
            "Turma/Vara/Plenário": turma_vara_plenario,
            "Nome Magistrado": nome_magistrado,
            "Telefone Gabinete": telefone_gabinete
        }
        st.session_state.processos.append(novo_processo)
        st.success("Processo cadastrado com sucesso!")
        st.session_state.autores = [{"nome": "", "cpf_cnpj": ""}]
        st.session_state.reus = [{"nome": "", "cpf_cnpj": ""}]

def cadastro_jurisprudencia():
    st.title("📚 Cadastro de Jurisprudência")

    # Campo para cadastro
    with st.form("form_jurisprudencia"):
        numero = st.text_input("Número")
        descricao = st.text_area("Descrição")
        palavras_chave = st.text_input("Palavras-chave (separadas por vírgula)")
        enviar = st.form_submit_button("Salvar Jurisprudência")

    if enviar:
        # Limpar espaços das palavras-chave e salvar como lista
        lista_palavras = [p.strip().lower() for p in palavras_chave.split(",") if p.strip()]
        st.session_state.jurisprudencias.append({
            "Número": numero,
            "Descrição": descricao,
            "Palavras-chave": lista_palavras
        })
        st.success("Jurisprudência cadastrada com sucesso!")

    st.markdown("---")
    st.subheader("🔎 Buscar Jurisprudências")

    termo_pesquisa = st.text_input("Digite termo para busca (número, descrição ou palavra-chave)")
    botao_pesquisar = st.button("Pesquisar")

    # Inicializa lista para exibir resultados
    resultados = []

    if botao_pesquisar and termo_pesquisa.strip():
        termo = termo_pesquisa.strip().lower()
        for jur in st.session_state.jurisprudencias:
            numero = jur.get("Número", "").lower()
            descricao = jur.get("Descrição", "").lower()
            palavras = jur.get("Palavras-chave", [])
            if (termo in numero) or (termo in descricao) or (any(termo in p for p in palavras)):
                resultados.append(jur)
        if not resultados:
            st.info("Nenhuma jurisprudência encontrada para o termo pesquisado.")
    else:
        # Se não pesquisou, mostra todas cadastradas
        resultados = st.session_state.jurisprudencias

    if resultados:
        for i, jur in enumerate(resultados):
            st.markdown(f"### Jurisprudência {i+1}")
            st.write(f"**Número:** {jur.get('Número', '')}")
            st.write(f"**Descrição:** {jur.get('Descrição', '')}")
            st.write(f"**Palavras-chave:** {', '.join(jur.get('Palavras-chave', []))}")
            st.markdown("---")


def despachos():
    st.title("🗂️ Despachos")
    with st.form("form_despachos"):
        numero = st.text_input("Número do Processo")
        descricao = st.text_area("Descrição do Despacho")
        enviado_por = st.session_state.usuario_logado
        enviar = st.form_submit_button("Cadastrar Despacho")
    if enviar:
        st.session_state.despachos.append({
            "Número": numero,
            "Descrição": descricao,
            "Enviado Por": enviado_por,
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })
        st.success("Despacho cadastrado com sucesso!")

def movimentacoes():
    st.title("🔄 Movimentações")

    menu = st.radio("Escolha uma opção:", ["Cadastrar Movimentação", "Visualizar / Editar Movimentações"], index=0)

    if menu == "Cadastrar Movimentação":
        with st.form("form_movimentacao"):
            numero = st.text_input("Número do Processo")
            descricao = st.text_area("Descrição da Movimentação")
            prazo = st.date_input("Prazo", value=datetime.today())
            enviar = st.form_submit_button("Salvar Movimentação")

        if enviar:
            nova_movimentacao = {
                "Número": numero,
                "Descrição": descricao,
                "Prazo": prazo.strftime("%d/%m/%Y"),
                "Usuário": st.session_state.usuario_logado
            }
            st.session_state.movimentacoes.append(nova_movimentacao)
            st.success("Movimentação cadastrada com sucesso!")
            rerun()

    else:  # Visualizar / Editar
        if not st.session_state.movimentacoes:
            st.info("Nenhuma movimentação cadastrada.")
            return

        # Mostrar lista de movimentações para selecionar e editar
        movs = st.session_state.movimentacoes
        opcoes = [f"{m['Número']} - {m['Descrição'][:30]}... - Prazo: {m['Prazo']}" for m in movs]
        escolha = st.selectbox("Selecione uma movimentação para editar ou excluir", [""] + opcoes)

        if escolha:
            idx = opcoes.index(escolha)
            mov_sel = movs[idx]

            with st.form("form_editar_movimentacao"):
                numero = st.text_input("Número do Processo", value=mov_sel["Número"])
                descricao = st.text_area("Descrição da Movimentação", value=mov_sel["Descrição"])
                try:
                    prazo_val = datetime.strptime(mov_sel["Prazo"], "%d/%m/%Y").date()
                except:
                    prazo_val = datetime.today().date()
                prazo = st.date_input("Prazo", value=prazo_val)
                enviar = st.form_submit_button("Salvar Alterações")
                excluir = st.form_submit_button("Excluir Movimentação")

            if enviar:
                st.session_state.movimentacoes[idx] = {
                    "Número": numero,
                    "Descrição": descricao,
                    "Prazo": prazo.strftime("%d/%m/%Y"),
                    "Usuário": mov_sel.get("Usuário", st.session_state.usuario_logado)
                }
                st.success("Movimentação atualizada com sucesso!")
                rerun()

            if excluir:
                st.session_state.movimentacoes.pop(idx)
                st.success("Movimentação excluída com sucesso!")
                rerun()

def agenda():
    st.title("📅 Agenda de Eventos")

    modo = st.radio("Escolha a ação:", ["Adicionar Evento", "Editar/Excluir Evento"])

    if modo == "Adicionar Evento":
        with st.form("form_agenda"):
            data = st.date_input("Data do Evento")
            evento = st.text_input("Evento")
            descricao = st.text_area("Descrição")
            horario_texto = st.text_input("Horário do Evento (ex: 14:30)")
            local = st.text_input("Local da Reunião")
            representante = st.text_input("Advogado/Representante no Ato")

            def validar_hora(hora_str):
                import re
                return bool(re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", hora_str))

            enviar = st.form_submit_button("Adicionar Evento")

        if enviar:
            if horario_texto and not validar_hora(horario_texto):
                st.error("Formato do horário inválido. Use HH:MM (ex: 14:30).")
                return
            novo_evento = {
                "Data": data.strftime("%d/%m/%Y"),
                "Evento": evento,
                "Descrição": descricao,
                "Horário": horario_texto,
                "Local": local,
                "Representante": representante
            }
            st.session_state.agenda.append(novo_evento)
            st.success("Evento adicionado com sucesso!")

    elif modo == "Editar/Excluir Evento":
        if not st.session_state.agenda:
            st.info("Nenhum evento cadastrado.")
            return

        eventos = st.session_state.agenda
        opcoes = [f"{e['Data']} - {e['Evento']} às {e.get('Horário', '')}" for e in eventos]
        selecao = st.selectbox("Selecione o evento", [""] + opcoes)

        if selecao:
            idx = opcoes.index(selecao)
            evento_sel = eventos[idx]

            with st.form("form_editar_evento"):
                data = st.date_input("Data do Evento", value=datetime.strptime(evento_sel["Data"], "%d/%m/%Y"))
                evento = st.text_input("Evento", value=evento_sel["Evento"])
                descricao = st.text_area("Descrição", value=evento_sel["Descrição"])
                horario = st.text_input("Horário (HH:MM)", value=evento_sel.get("Horário", ""))
                local = st.text_input("Local da Reunião", value=evento_sel.get("Local", ""))
                representante = st.text_input("Advogado/Representante no Ato", value=evento_sel.get("Representante", ""))
                salvar = st.form_submit_button("Salvar Alterações")
                excluir = st.form_submit_button("Excluir Evento")

            if salvar:
                if horario and not validar_hora(horario):
                    st.error("Formato do horário inválido. Use HH:MM.")
                    return
                eventos[idx] = {
                    "Data": data.strftime("%d/%m/%Y"),
                    "Evento": evento,
                    "Descrição": descricao,
                    "Horário": horario,
                    "Local": local,
                    "Representante": representante
                }
                st.success("Evento atualizado com sucesso!")
                st.experimental_rerun()

            if excluir:
                eventos.pop(idx)
                st.success("Evento excluído com sucesso!")
                st.experimental_rerun()


def gerenciar_usuarios():
    if not usuario_eh_master():
        st.warning("Você não tem permissão para acessar essa área.")
        return
    st.title("👥 Gerenciamento de Usuários")

    with st.form("form_cadastrar_usuario"):
        nome = st.text_input("Nome")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        permissao = st.selectbox("Permissão", ["normal", "master"])
        enviar = st.form_submit_button("Cadastrar Usuário")
    if enviar:
        novo_usuario = {
            "nome": nome,
            "usuario": usuario,
            "senha": senha,
            "permissao": permissao
        }
        st.session_state.usuarios.append(novo_usuario)
        st.success("Usuário cadastrado com sucesso!")

    st.markdown("---")

    st.subheader("Usuários Cadastrados")
    for u in st.session_state.usuarios:
        st.write(f"Nome: {u['nome']} - Usuário: {u['usuario']} - Permissão: {u['permissao']}")

def main():
    if not st.session_state.logado:
        tela_login()
        return

    with st.sidebar:
        escolha = option_menu(
            menu_title="Menu Principal",
            options=["Início", "Cadastro Processo", "Cadastro Jurisprudência", "Despachos", "Movimentações", "Agenda", "Gerenciar Usuários", "Logout"],
            icons=["house", "file-earmark-text", "book", "file-text", "arrow-repeat", "calendar", "people", "box-arrow-right"],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {"padding": "5px"},
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
    elif escolha == "Gerenciar Usuários":
        gerenciar_usuarios()
    elif escolha == "Logout":
        st.session_state.logado = False
        st.session_state.usuario_logado = None
        st.experimental_rerun()

    # Rodapé fixo
    st.markdown("""
    <div class="footer">
        Desenvolvido por Igor Sansone - Setor de Secretaria
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
