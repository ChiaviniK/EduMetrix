import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EduMetrix | Gov Data", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    h1, h2 { color: #2c3e50 !important; }
    .stButton>button { width: 100%; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. API REAL (IBGE) - DADOS GOVERNAMENTAIS AO VIVO
# ==============================================================================
@st.cache_data
def get_ibge_cidades(uf_sigla):
    """
    Conecta na API de Dados do Governo Federal (IBGE).
    Retorna a lista oficial de municípios e códigos.
    """
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_sigla}/municipios"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Tratamento JSON -> DataFrame
            lista_cidades = []
            for item in data:
                lista_cidades.append({
                    "ID_IBGE": item['id'],
                    "Cidade": item['nome'],
                    "Microrregião": item['microrregiao']['nome'],
                    "UF": uf_sigla
                })
            return pd.DataFrame(lista_cidades)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# ==============================================================================
# 2. DADOS CURADOS (ENEM) - BASE DE INTELIGÊNCIA
# ==============================================================================
@st.cache_data
def get_enem_analytics():
    # Dados estratégicos simulados para o Case
    data = [
        {"Cidade": "São Paulo", "UF": "SP", "Redação": 660, "Mat": 645, "Hum": 620, "Nat": 610, "Inscritos": 45000},
        {"Cidade": "Campinas", "UF": "SP", "Redação": 670, "Mat": 655, "Hum": 630, "Nat": 620, "Inscritos": 12000},
        {"Cidade": "Rio de Janeiro", "UF": "RJ", "Redação": 650, "Mat": 620, "Hum": 625, "Nat": 590, "Inscritos": 38000},
        {"Cidade": "Belo Horizonte", "UF": "MG", "Redação": 680, "Mat": 650, "Hum": 645, "Nat": 630, "Inscritos": 25000},
        {"Cidade": "Fortaleza", "UF": "CE", "Redação": 650, "Mat": 635, "Hum": 620, "Nat": 610, "Inscritos": 26000},
        {"Cidade": "Sobral", "UF": "CE", "Redação": 660, "Mat": 640, "Hum": 625, "Nat": 615, "Inscritos": 3000},
        {"Cidade": "Recife", "UF": "PE", "Redação": 640, "Mat": 610, "Hum": 615, "Nat": 590, "Inscritos": 18000},
        {"Cidade": "Curitiba", "UF": "PR", "Redação": 655, "Mat": 630, "Hum": 625, "Nat": 610, "Inscritos": 15000},
        {"Cidade": "Porto Alegre", "UF": "RS", "Redação": 645, "Mat": 625, "Hum": 630, "Nat": 605, "Inscritos": 14000},
        {"Cidade": "Brasília", "UF": "DF", "Redação": 660, "Mat": 635, "Hum": 640, "Nat": 615, "Inscritos": 20000},
        {"Cidade": "Manaus", "UF": "AM", "Redação": 610, "Mat": 575, "Hum": 590, "Nat": 565, "Inscritos": 15000}
    ]
    return pd.DataFrame(data)

MEDIA_BR = {"Red": 590, "Mat": 540, "Hum": 560, "Nat": 530}

# ==============================================================================
# INTERFACE
# ==============================================================================
st.sidebar.image("https://img.icons8.com/nolan/96/diploma.png", width=80)
st.sidebar.title("EduMetrix")
st.sidebar.markdown("---")
st.sidebar.info("Plataforma Híbrida:\n1. Dados Curados (Analytics)\n2. API Governo (Oficial)")

st.title("EduMetrix: Education Intelligence")

# 3 ABAS AGORA
tab_enem, tab_ibge, tab_sobre = st.tabs(["📊 ENEM Analytics", "📥 Extrator IBGE (API)", "ℹ️ Sobre"])

# --- TAB 1: ENEM ANALYTICS (VISUALIZAÇÃO) ---
with tab_enem:
    st.header("Inteligência de Desempenho")
    df_enem = get_enem_analytics()
    
    # Filtros
    c1, c2 = st.columns(2)
    with c1:
        uf_sel = st.selectbox("Filtrar Estado:", ["Todos"] + sorted(df_enem['UF'].unique()))
    
    if uf_sel != "Todos":
        df_display = df_enem[df_enem['UF'] == uf_sel]
    else:
        df_display = df_enem
        
    with c2:
        cidade_sel = st.selectbox("Cidade:", sorted(df_display['Cidade'].unique()))
        
    # Dados
    dado = df_enem[df_enem['Cidade'] == cidade_sel].iloc[0]
    
    # Radar Chart
    col_kpi, col_radar = st.columns([1, 2])
    
    with col_kpi:
        st.metric("Matemática", dado['Mat'], f"{dado['Mat'] - MEDIA_BR['Mat']}")
        st.metric("Redação", dado['Redação'], f"{dado['Redação'] - MEDIA_BR['Red']}")
        st.metric("Natureza", dado['Nat'], f"{dado['Nat'] - MEDIA_BR['Nat']}")
        st.caption("Comparação vs Média Brasil")
        
    with col_radar:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[dado['Mat'], dado['Redação'], dado['Nat'], dado['Hum']],
            theta=['Matemática', 'Redação', 'Natureza', 'Humanas'],
            fill='toself', name=cidade_sel, line_color='#4b0082'
        ))
        fig.add_trace(go.Scatterpolar(
            r=[MEDIA_BR['Mat'], MEDIA_BR['Red'], MEDIA_BR['Nat'], MEDIA_BR['Hum']],
            theta=['Matemática', 'Redação', 'Natureza', 'Humanas'],
            name='Média Nacional', line_dash='dot', line_color='gray'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[400, 800])), height=350)
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: EXTRATOR IBGE (API REAL) ---
with tab_ibge:
    st.header("Conexão Governamental (IBGE)")
    st.markdown("""
    Esta guia conecta diretamente à **API de Localidades do Governo Federal**. 
    Use para baixar a lista oficial de cidades atualizada para cadastro no sistema.
    """)
    
    col_input, col_status = st.columns([1, 2])
    
    with col_input:
        uf_api = st.selectbox("Selecione a UF para Extração:", 
                             ["SP", "RJ", "MG", "ES", "RS", "PR", "SC", "BA", "PE", "CE", "AM"])
        
        btn_carregar = st.button("📡 BUSCAR NA API IBGE")
    
    if btn_carregar:
        with st.spinner(f"Conectando a servicodados.ibge.gov.br para {uf_api}..."):
            df_ibge = get_ibge_cidades(uf_api)
            
        if not df_ibge.empty:
            with col_status:
                st.success(f"✅ Conexão Estabelecida! {len(df_ibge)} municípios encontrados.")
            
            st.markdown("---")
            st.subheader(f"Lista Oficial: {uf_api}")
            
            # Mostra a tabela real que veio da API
            st.dataframe(df_ibge, use_container_width=True, height=400)
            
            # DOWNLOAD CSV (O que você queria!)
            csv = df_ibge.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Baixar Lista Oficial ({uf_api}) .CSV",
                data=csv,
                file_name=f"ibge_municipios_{uf_api}.csv",
                mime="text/csv"
            )
        else:
            st.error("Erro ao conectar com API do Governo. Tente novamente.")

# --- TAB 3: SOBRE ---
with tab_sobre:
    st.subheader("Arquitetura do Sistema")
    st.image("https://img.icons8.com/clouds/200/server.png", width=150)
    st.markdown("""
    **EduMetrix v5.0** opera com arquitetura híbrida:
    
    1.  **Módulo Analytics:** Utiliza *Data Lake Curado* (Python) para performance de visualização de notas.
    2.  **Módulo Extrator:** Utiliza *API REST (GET)* para consultar a base `servicodados.ibge.gov.br` em tempo real.
    
    **Tech Stack:**
    * Python / Streamlit
    * Plotly (Visualização)
    * Requests (Conectividade API)
    """)
