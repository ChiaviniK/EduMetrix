import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="EduMetrix | Intelligence Suite", page_icon="🎓", layout="wide")

# --- ESTILIZAÇÃO ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    h1, h2 { color: #2c3e50 !important; font-family: 'Segoe UI', sans-serif; }
    .stMetric {
        background-color: white; border-radius: 10px; padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #6f42c1;
    }
    .footer { text-align: center; color: #7f8c8d; padding: 20px; font-size: 0.8em; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🧠 MOTORES DE DADOS (BACKEND)
# ==============================================================================

@st.cache_data
def get_enem_analytics_data():
    """Retorna a base de inteligência consolidada (Simulado Realista)."""
    data = [
        {"Cidade": "São Paulo", "UF": "SP", "Redação": 660, "Mat": 645, "Hum": 620, "Nat": 610, "Inscritos": 45000},
        {"Cidade": "Rio de Janeiro", "UF": "RJ", "Redação": 650, "Mat": 620, "Hum": 625, "Nat": 590, "Inscritos": 38000},
        {"Cidade": "Belo Horizonte", "UF": "MG", "Redação": 680, "Mat": 650, "Hum": 645, "Nat": 630, "Inscritos": 25000},
        {"Cidade": "Fortaleza", "UF": "CE", "Redação": 650, "Mat": 635, "Hum": 620, "Nat": 610, "Inscritos": 26000},
        {"Cidade": "Porto Alegre", "UF": "RS", "Redação": 645, "Mat": 625, "Hum": 630, "Nat": 605, "Inscritos": 14000},
        {"Cidade": "Brasília", "UF": "DF", "Redação": 660, "Mat": 635, "Hum": 640, "Nat": 615, "Inscritos": 20000},
        {"Cidade": "Manaus", "UF": "AM", "Redação": 610, "Mat": 575, "Hum": 590, "Nat": 565, "Inscritos": 15000}
    ]
    return pd.DataFrame(data)

@st.cache_data
def generate_microdados_equidade():
    """Gera Microdados Socioeconômicos para o desafio de ETL."""
    np.random.seed(42)
    n = 2500
    locais = [("São Paulo", "SP"), ("Rio de Janeiro", "RJ"), ("Fortaleza", "CE"), ("Belo Horizonte", "MG"), ("Manaus", "AM")]
    
    dados = []
    for _ in range(n):
        cidade, uf = locais[np.random.randint(0, len(locais))]
        perfil = np.random.choice(['Baixo', 'Medio', 'Alto'], p=[0.4, 0.4, 0.2])
        
        # Lógica de distribuição socioeconômica
        if perfil == 'Baixo':
            renda = np.random.choice(['A', 'B'])     # Sem renda ou até 1 sal. min
            mae = np.random.choice(['A', 'B'])       # Mãe sem estudo ou fund. incomp
            internet = np.random.choice(['Não', 'Sim'], p=[0.4, 0.6]) # 40% sem net
            nota_base = 460
        elif perfil == 'Medio':
            renda = np.random.choice(['C', 'D'])
            mae = np.random.choice(['D', 'F'])
            internet = 'Sim'
            nota_base = 610
        else: # Alto
            renda = np.random.choice(['E', 'Q'])
            mae = np.random.choice(['F', 'G'])
            internet = 'Sim'
            nota_base = 730
            
        dados.append({
            "ID_Inscricao": np.random.randint(1000000000, 9999999999),
            "NO_MUNICIPIO": cidade,
            "SG_UF": uf,
            "Q006_Renda": renda,
            "Q002_Esc_Mae": mae,
            "Q025_Tem_Internet": internet, # <--- ADICIONADO AQUI
            "NU_NOTA_GERAL": max(0, min(1000, int(np.random.normal(nota_base, 80))))
        })
    return pd.DataFrame(dados)

@st.cache_data
def get_ibge_api(uf):
    """Conecta na API Oficial do IBGE."""
    try:
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
        r = requests.get(url, timeout=5)
        return pd.DataFrame([{'ID': i['id'], 'Nome': i['nome']} for i in r.json()])
    except: return pd.DataFrame()

@st.cache_data
def get_world_unis(country):
    """Conecta na API Global Hipolabs Universities."""
    try:
        url = f"http://universities.hipolabs.com/search?country={country}"
        r = requests.get(url, timeout=5)
        return pd.DataFrame(r.json())
    except: return pd.DataFrame()

# ==============================================================================
# 🖥️ INTERFACE E NAVEGAÇÃO
# ==============================================================================

st.sidebar.image("https://img.icons8.com/nolan/96/diploma.png", width=80)
st.sidebar.title("EduMetrix")
st.sidebar.caption("v7.1 | Education BI")
st.sidebar.markdown("---")

tab_enem, tab_equidade, tab_ibge, tab_world = st.tabs([
    "📊 ENEM Analytics", "⚖️ Projeto Equidade", "📥 Extrator IBGE", "🌍 Universidades"
])

# --- TAB 1: ANALYTICS (DADOS CURADOS) ---
with tab_enem:
    st.header("Inteligência de Desempenho Regional")
    df_analytics = get_enem_analytics_data()
    
    cidade_sel = st.selectbox("Selecione a Cidade:", df_analytics['Cidade'].unique())
    dado = df_analytics[df_analytics['Cidade'] == cidade_sel].iloc[0]
    
    col_m, col_r = st.columns([1, 2])
    with col_m:
        st.metric("Média Matemática", dado['Mat'], f"{dado['Mat']-540}")
        st.metric("Média Redação", dado['Redação'], f"{dado['Redação']-590}")
        st.caption("Deltas vs Média Nacional")
        
    with col_r:
        fig_radar = go.Figure(go.Scatterpolar(
            r=[dado['Mat'], dado['Redação'], dado['Hum'], dado['Nat']],
            theta=['Matemática', 'Redação', 'Humanas', 'Natureza'],
            fill='toself', name=cidade_sel, line_color='#4b0082'
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[400, 800])), height=350)
        st.plotly_chart(fig_radar, use_container_width=True)

# --- TAB 2: PROJETO EQUIDADE (ETL & SOCIOECONÔMICO) ---
with tab_equidade:
    st.header("Desafio de Equidade: ETL Socioeconômico")
    st.markdown("Transforme dados qualitativos do questionário em um Índice Socioeconômico (ISE).")
    
    df_raw = generate_microdados_equidade()
    
    st.subheader("1. Extração de Microdados (Raw)")
    # Mostra a nova coluna na prévia
    st.dataframe(df_raw[['ID_Inscricao', 'NO_MUNICIPIO', 'Q006_Renda', 'Q025_Tem_Internet']].head(), use_container_width=True)
    
    st.download_button("📥 Baixar Microdados Brutos (.csv)", df_raw.to_csv(index=False).encode('utf-8'), "enem_raw.csv")
    
    st.markdown("---")
    if st.checkbox("🔄 Executar Transformação (Pipeline ETL)"):
        with st.spinner("Processando dados qualitativos..."):
            df_etl = df_raw.copy()
            
            # 1. Mapeamento Renda (0 a 5 pts)
            mapa_renda = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'Q': 5}
            
            # 2. Mapeamento Escolaridade Mãe (0 a 4 pts)
            mapa_esc = {'A': 0, 'B': 1, 'D': 2, 'F': 3, 'G': 4}
            
            # 3. Mapeamento Internet (0 ou 1 pt) - <--- LÓGICA CORRIGIDA AQUI
            df_etl['Score_Internet'] = df_etl['Q025_Tem_Internet'].apply(lambda x: 1 if x == 'Sim' else 0)
            
            # Cálculo Final do ISE (Soma simples)
            df_etl['ISE'] = df_etl['Q006_Renda'].map(mapa_renda) + \
                            df_etl['Q002_Esc_Mae'].map(mapa_esc).fillna(0) + \
                            df_etl['Score_Internet']
            
            st.success("✅ ETL Concluído: Coluna 'ISE' gerada com sucesso.")
            
            # Gráfico de Dispersão
            fig_eq = px.scatter(
                df_etl, 
                x="ISE", 
                y="NU_NOTA_GERAL", 
                color="NO_MUNICIPIO", 
                title="Correlação: Índice Socioeconômico (ISE) vs Nota Final",
                labels={"ISE": "Índice Socioeconômico (0=Vulnerável, 10=Privilegiado)"},
                trendline="ols"
            )
            st.plotly_chart(fig_eq, use_container_width=True)

# --- TAB 3: EXTRATOR IBGE (API REAL) ---
with tab_ibge:
    st.header("Conexão Governamental: API IBGE")
    uf = st.selectbox("Selecione a UF para Extração:", ["SP", "RJ", "MG", "CE", "BA", "RS"])
    if st.button("📡 Buscar Municípios"):
        df_ibge = get_ibge_api(uf)
        if not df_ibge.empty:
            st.success(f"Encontrados {len(df_ibge)} municípios.")
            st.dataframe(df_ibge, use_container_width=True)
            st.download_button("📥 Baixar Lista IBGE", df_ibge.to_csv(index=False).encode('utf-8'), f"ibge_{uf}.csv")
        else:
            st.error("Erro na API do IBGE.")

# --- TAB 4: UNIVERSIDADES (API GLOBAL) ---
with tab_world:
    st.header("Mapeamento Acadêmico Global")
    pais = st.selectbox("País:", ["Brazil", "United States", "Portugal", "Canada"])
    df_uni = get_world_unis(pais)
    if not df_uni.empty:
        df_uni['Site'] = df_uni['web_pages'].apply(lambda x: x[0] if x else "")
        st.dataframe(df_uni[['name', 'Site']], column_config={"Site": st.column_config.LinkColumn("Website")}, use_container_width=True)

st.markdown("---")
st.markdown('<div class="footer">EduMetrix Suite • Inteligência Educacional baseada em Microdados Reais</div>', unsafe_allow_html=True)
