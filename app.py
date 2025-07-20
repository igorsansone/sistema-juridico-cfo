import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu
import altair as alt
import streamlit.components.v1 as components
from io import BytesIO

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

    # Botão para exportar processos em Excel
    if processos:
        df_export = pd.DataFrame(processos)
        towrite = BytesIO()
        df_export.to_excel(towrite, index=False, sheet_name='Processos')
        towrite.seek(0)
        st.download_button(
            label="📥 Exportar Processos para Excel",
            data=towrite,
            file_name="processos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


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
    with st.form("form_jurisprudencia"):
        numero = st.text_input("Número")
        descricao = st.text_area("Descrição")
        enviar = st.form_submit_button("Salvar Jurisprudência")
    if enviar:
        st.session_state.jurisprudencias.append({
            "Número": numero,
            "Descrição": descricao
        })
        st.success("Jurisprudência cadastrada com sucesso!")

def movimentacoes():
    st.title("🔄 Movimentações Processuais")
    with st.form("form_movimentacoes"):
        numero = st.text_input("Número do Processo")
        descricao = st.text_area("Descrição da Movimentação")
        prazo = st.date_input("Prazo", value=datetime.today())
        enviar = st.form_submit_button("Registrar Movimentação")
    if enviar:
        st.session_state.movimentacoes.append({
            "Número": numero,
            "Descrição": descricao,
            "Prazo": prazo.strftime("%d/%m/%Y")
        })
        st.success("Movimentação registrada com sucesso!")

def agenda_eventos():
    st.title("📅 Agenda de Eventos")
    with st.form("form_agenda"):
        data = st.date_input("Data do Evento", value=datetime.today())
        evento = st.text_input("Evento")
        descricao = st.text_area("Descrição")
        enviar = st.form_submit_button("Salvar Evento")
    if enviar:
        st.session_state.agenda.append({
            "Data": data.strftime("%d/%m/%Y"),
            "Evento": evento,
            "Descrição": descricao
        })
        st.success("Evento cadastrado com sucesso!")

def relatorios():
    st.title("📊 Relatórios")
    st.write("Funcionalidade de relatórios a ser implementada...")

def rodape():
    st.markdown(
        """
        <div class="footer">Desenvolvido por Igor Sansone - Setor de Secretaria</div>
        """, 
        unsafe_allow_html=True
    )

def main():
    if not st.session_state.logado:
        tela_login()
    else:
        with st.sidebar:
            selected = option_menu(
                "Menu Principal",
                ["Início", "Cadastro Processo", "Cadastro Jurisprudência", "Movimentações", "Agenda", "Relatórios", "Sair"],
                icons=["house", "file-earmark-text", "book", "arrow-repeat", "calendar", "bar-chart-line", "box-arrow-right"],
                menu_icon="cast",
                default_index=0,
            )
        if selected == "Início":
            inicio()
        elif selected == "Cadastro Processo":
            cadastro_processo()
        elif selected == "Cadastro Jurisprudência":
            cadastro_jurisprudencia()
        elif selected == "Movimentações":
            movimentacoes()
        elif selected == "Agenda":
            agenda_eventos()
        elif selected == "Relatórios":
            relatorios()
        elif selected == "Sair":
            st.session_state.logado = False
            st.session_state.usuario_logado = None
            st.experimental_rerun()

        rodape()

        st.markdown('<div class="footer">Desenvolvido por Igor Sansone - Setor de Secretaria - Para uso do Conselho Federal de Odontologia</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
