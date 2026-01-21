import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import numpy as np

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EduMetrix | Full Suite", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    h1, h2 { color: #2c3e50 !important; }
    div[data-testid="stMetric"] {
        background-color: white; border-radius: 8px; padding: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-top: 4px solid #4b0082;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🧠 MÓDULO 1: UNIVERSIDADES (API HIPOLABS)
# ==============================================================================
@st.cache_data
def get_universities(country_name):
    url = f"http://universities.hipolabs.com/search?country={country_name}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if not data: return pd.DataFrame()
            
            lista = []
            for uni in data:
                site = uni['web_pages'][0] if uni.get('web_pages') else "N/A"
                lista.append({
                    "Instituição": uni['name'],
                    "Estado": uni.get('state-province'),
                    "Website": site
                })
            return pd.DataFrame(lista)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# ==============================================================================
# 🇧🇷 MÓDULO 2: ENEM INTEL (SIMULADOR DE DADOS REAIS)
# ==============================================================================
@st.cache_data
def get_enem_data():
    """
    Gera um dataset representativo das médias do ENEM por cidade.
    Na vida real, isso viria de um arquivo .csv tratado do INEP.
    """
    # Lista de Cidades Chave para o Case
    cidades_base = [
        ("São Paulo", "SP", 620, 580, 640, 45000),
        ("Campinas", "SP", 645, 600, 660, 12000),
        ("São José dos Campos", "SP", 630, 590, 650, 8000),
        ("Rio de Janeiro", "RJ", 610, 570, 630, 38000),
        ("Niterói", "RJ", 625, 595, 645, 6000),
        ("Belo Horizonte", "MG", 635, 610, 655, 25000),
        ("Uberlândia", "MG", 615, 580, 620, 7000),
        ("Curitiba", "PR", 618, 585, 625, 15000),
        ("Florianópolis", "SC", 628, 590, 640, 5000),
        ("Porto Alegre", "RS", 612, 575, 610, 14000),
        ("Salvador", "BA", 590, 550, 600, 22000),
        ("Recife", "PE", 605, 565, 620, 18000),
        ("Fortaleza", "CE", 615, 590, 630, 26000), # Ceará forte em exatas
        ("Manaus", "AM", 570, 540, 580, 15000),
        ("Brasília", "DF", 630, 595, 650, 20000)
    ]
    
    dados = []
    np.random.seed(42) # Para manter consistência
    
    for cidade, uf, red, mat, hum, inscritos in cidades_base:
        # Adicionamos uma pequena variação aleatória para cada "ano" simulado
        dados.append({
            "Cidade": cidade,
            "Estado": uf,
            "Média Redação": red,
            "Média Matemática": mat,
            "Média Humanas": hum,
            "Inscritos": inscritos,
            "Taxa Aprovação": np.random.uniform(70, 95)
        })
        
    return pd.DataFrame(dados)

# ==============================================================================
# 🖥️ INTERFACE PRINCIPAL
# ==============================================================================

st.sidebar.image("https://img.icons8.com/nolan/96/diploma.png", width=80)
st.sidebar.title("EduMetrix")
st.sidebar.markdown("---")
st.sidebar.info("Plataforma de Inteligência Educacional Global & Local.")

st.title("EduMetrix: Education Intelligence")

# CRIAÇÃO DAS ABAS
tab1, tab2 = st.tabs(["🌍 Universidades (Mundo)", "🇧🇷 Desempenho ENEM (Brasil)"])

# ------------------------------------------------------------------------------
# ABA 1: UNIVERSIDADES (O que já tínhamos)
# ------------------------------------------------------------------------------
with tab1:
    st.header("Mapeamento Global de Instituições")
    pais = st.selectbox("Selecione o País:", ["Brazil", "United States", "Portugal", "Canada", "Germany"], index=0)
    
    with st.spinner("Consultando API Hipolabs..."):
        df_uni = get_universities(pais)
    
    if not df_uni.empty:
        c1, c2 = st.columns(2)
        c1.metric("Universidades Encontradas", len(df_uni))
        c2.metric("Cobertura de Sites", f"{(len(df_uni[df_uni['Website']!='N/A'])/len(df_uni)*100):.0f}%")
        
        st.dataframe(
            df_uni,
            column_config={"Website": st.column_config.LinkColumn("Site Oficial")},
            use_container_width=True,
            hide_index=True,
            height=400
        )
    else:
        st.warning("Nenhum dado encontrado.")

# ------------------------------------------------------------------------------
# ABA 2: ENEM POR CIDADES (A Novidade!)
# ------------------------------------------------------------------------------
with tab2:
    st.header("Análise de Talentos: ENEM 2024/25 (Base Curada)")
    st.caption("Filtre cidades para encontrar onde estão os alunos com melhores notas.")
    
    df_enem = get_enem_data()
    
    # Filtros
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        uf_sel = st.selectbox("Filtrar Estado:", ["Todos"] + list(df_enem['Estado'].unique()))
    
    # Lógica de Filtro em Cascata
    if uf_sel != "Todos":
        df_filtrado = df_enem[df_enem['Estado'] == uf_sel]
    else:
        df_filtrado = df_enem
        
    with col_filtro2:
        cidade_sel = st.selectbox("Selecionar Cidade:", df_filtrado['Cidade'].unique())
    
    # Dados da Cidade Escolhida
    cidade_data = df_enem[df_enem['Cidade'] == cidade_sel].iloc[0]
    
    st.markdown("---")
    
    # 1. KPIs da Cidade
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📍 Cidade", cidade_data['Cidade'])
    k2.metric("📝 Média Redação", f"{cidade_data['Média Redação']} pts")
    k3.metric("📐 Média Matemática", f"{cidade_data['Média Matemática']} pts")
    k4.metric("👥 Total Inscritos", f"{cidade_data['Inscritos']:,}".replace(",", "."))
    
    # 2. Gráficos Comparativos
    st.subheader("📊 Raio-X de Desempenho")
    
    col_g1, col_g2 = st.columns([1, 1])
    
    with col_g1:
        # Gráfico Radar (Spider Chart) - Muito usado em educação
        notas = pd.DataFrame({
            'Matéria': ['Redação', 'Matemática', 'Humanas'],
            'Nota': [cidade_data['Média Redação'], cidade_data['Média Matemática'], cidade_data['Média Humanas']]
        })
        
        fig_radar = px.line_polar(notas, r='Nota', theta='Matéria', line_close=True, 
                                  range_r=[0, 1000], title=f"Perfil do Aluno: {cidade_sel}")
        fig_radar.update_traces(fill='toself', line_color='#4b0082')
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col_g2:
        # Comparativo com Média Nacional (Fictícia para referência)
        media_nacional = 550
        delta = cidade_data['Média Matemática'] - media_nacional
        cor = "green" if delta > 0 else "red"
        
        st.write(f"### Comparativo Nacional (Matemática)")
        st.markdown(f"""
        A média de **{cidade_sel}** em Matemática é **{cidade_data['Média Matemática']}**.
        Isso é <span style='color:{cor}; font-weight:bold'>{abs(delta)} pontos {'acima' if delta > 0 else 'abaixo'}</span> da média nacional (550).
        """, unsafe_allow_html=True)
        
        st.progress(cidade_data['Média Matemática'] / 1000)
        st.caption("Escala de 0 a 1000")

    # 3. Tabela de Ranking (Mostra todas para comparação)
    st.markdown("---")
    st.subheader("🏆 Ranking das Cidades Mapeadas")
    st.dataframe(
        df_enem.sort_values("Média Redação", ascending=False),
        column_config={
            "Média Redação": st.column_config.ProgressColumn("Redação", format="%d", min_value=0, max_value=1000),
            "Média Matemática": st.column_config.NumberColumn("Matemática", format="%d pts")
        },
        hide_index=True,
        use_container_width=True
    )
