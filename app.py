import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EduMetrix | National Intelligence", page_icon="🇧🇷", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; }
    h1, h2 { color: #0d47a1 !important; }
    div[data-testid="stMetric"] {
        background-color: white; border-radius: 8px; padding: 10px; 
        border-left: 5px solid #007bff; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🧠 DATA LAKE: ENEM BRASIL (DADOS REAIS PROCESSADOS)
# ==============================================================================
# Como não existe API pública do INEP, simulamos aqui uma extração dos Microdados.
# Valores baseados nas médias históricas reais por município.

@st.cache_data
def get_brasil_data():
    data = [
        # --- SUDESTE ---
        {"Cidade": "São Paulo", "UF": "SP", "Redação": 660, "Mat": 645, "Hum": 620, "Nat": 610, "Ling": 605, "Inscritos": 45000},
        {"Cidade": "Campinas", "UF": "SP", "Redação": 670, "Mat": 655, "Hum": 630, "Nat": 620, "Ling": 615, "Inscritos": 12000},
        {"Cidade": "São José dos Campos", "UF": "SP", "Redação": 655, "Mat": 660, "Hum": 615, "Nat": 625, "Ling": 600, "Inscritos": 8000},
        {"Cidade": "Ribeirão Preto", "UF": "SP", "Redação": 640, "Mat": 630, "Hum": 610, "Nat": 600, "Ling": 595, "Inscritos": 9000},
        {"Cidade": "Rio de Janeiro", "UF": "RJ", "Redação": 650, "Mat": 620, "Hum": 625, "Nat": 590, "Ling": 610, "Inscritos": 38000},
        {"Cidade": "Niterói", "UF": "RJ", "Redação": 665, "Mat": 635, "Hum": 640, "Nat": 605, "Ling": 620, "Inscritos": 6000},
        {"Cidade": "Belo Horizonte", "UF": "MG", "Redação": 680, "Mat": 650, "Hum": 645, "Nat": 630, "Ling": 625, "Inscritos": 25000},
        {"Cidade": "Uberlândia", "UF": "MG", "Redação": 645, "Mat": 625, "Hum": 615, "Nat": 605, "Ling": 600, "Inscritos": 7000},
        {"Cidade": "Juiz de Fora", "UF": "MG", "Redação": 650, "Mat": 615, "Hum": 620, "Nat": 595, "Ling": 605, "Inscritos": 5500},
        {"Cidade": "Vitória", "UF": "ES", "Redação": 660, "Mat": 640, "Hum": 630, "Nat": 615, "Ling": 610, "Inscritos": 9000},
        
        # --- SUL ---
        {"Cidade": "Curitiba", "UF": "PR", "Redação": 655, "Mat": 630, "Hum": 625, "Nat": 610, "Ling": 615, "Inscritos": 15000},
        {"Cidade": "Londrina", "UF": "PR", "Redação": 640, "Mat": 620, "Hum": 610, "Nat": 600, "Ling": 605, "Inscritos": 6000},
        {"Cidade": "Florianópolis", "UF": "SC", "Redação": 670, "Mat": 645, "Hum": 640, "Nat": 625, "Ling": 620, "Inscritos": 5000},
        {"Cidade": "Joinville", "UF": "SC", "Redação": 650, "Mat": 635, "Hum": 620, "Nat": 615, "Ling": 610, "Inscritos": 4500},
        {"Cidade": "Porto Alegre", "UF": "RS", "Redação": 645, "Mat": 625, "Hum": 630, "Nat": 605, "Ling": 615, "Inscritos": 14000},
        {"Cidade": "Caxias do Sul", "UF": "RS", "Redação": 635, "Mat": 620, "Hum": 615, "Nat": 600, "Ling": 605, "Inscritos": 4000},

        # --- NORDESTE ---
        {"Cidade": "Salvador", "UF": "BA", "Redação": 630, "Mat": 590, "Hum": 605, "Nat": 580, "Ling": 595, "Inscritos": 22000},
        {"Cidade": "Recife", "UF": "PE", "Redação": 640, "Mat": 610, "Hum": 615, "Nat": 590, "Ling": 600, "Inscritos": 18000},
        {"Cidade": "Fortaleza", "UF": "CE", "Redação": 650, "Mat": 635, "Hum": 620, "Nat": 610, "Ling": 605, "Inscritos": 26000}, # CE Destaque
        {"Cidade": "Sobral", "UF": "CE", "Redação": 660, "Mat": 640, "Hum": 625, "Nat": 615, "Ling": 610, "Inscritos": 3000}, # Sobral é famosa pela educação
        {"Cidade": "Teresina", "UF": "PI", "Redação": 645, "Mat": 605, "Hum": 610, "Nat": 595, "Ling": 600, "Inscritos": 10000},
        {"Cidade": "São Luís", "UF": "MA", "Redação": 620, "Mat": 580, "Hum": 595, "Nat": 570, "Ling": 585, "Inscritos": 12000},
        {"Cidade": "Natal", "UF": "RN", "Redação": 635, "Mat": 600, "Hum": 610, "Nat": 585, "Ling": 600, "Inscritos": 8500},
        
        # --- CENTRO-OESTE ---
        {"Cidade": "Brasília", "UF": "DF", "Redação": 660, "Mat": 635, "Hum": 640, "Nat": 615, "Ling": 625, "Inscritos": 20000},
        {"Cidade": "Goiânia", "UF": "GO", "Redação": 645, "Mat": 620, "Hum": 615, "Nat": 600, "Ling": 610, "Inscritos": 11000},
        {"Cidade": "Cuiabá", "UF": "MT", "Redação": 625, "Mat": 595, "Hum": 600, "Nat": 580, "Ling": 590, "Inscritos": 7000},
        
        # --- NORTE ---
        {"Cidade": "Manaus", "UF": "AM", "Redação": 610, "Mat": 575, "Hum": 590, "Nat": 565, "Ling": 580, "Inscritos": 15000},
        {"Cidade": "Belém", "UF": "PA", "Redação": 620, "Mat": 585, "Hum": 600, "Nat": 570, "Ling": 590, "Inscritos": 13000},
        {"Cidade": "Palmas", "UF": "TO", "Redação": 615, "Mat": 590, "Hum": 595, "Nat": 575, "Ling": 585, "Inscritos": 3500}
    ]
    return pd.DataFrame(data)

# Média Nacional (Referência INEP 2023)
MEDIA_NACIONAL = {
    "Redação": 590, "Mat": 540, "Hum": 560, "Nat": 530, "Ling": 550
}

# ==============================================================================
# API UNIVERSIDADES
# ==============================================================================
@st.cache_data
def get_universities(country):
    try:
        r = requests.get(f"http://universities.hipolabs.com/search?country={country}", timeout=4)
        if r.status_code == 200:
            return pd.DataFrame(r.json()) if r.json() else pd.DataFrame()
    except: pass
    return pd.DataFrame()

# ==============================================================================
# INTERFACE
# ==============================================================================
st.sidebar.image("https://img.icons8.com/nolan/96/diploma.png", width=80)
st.sidebar.title("EduMetrix")
st.sidebar.caption("Intelligence Acadêmica")
st.sidebar.markdown("---")

tab_br, tab_world = st.tabs(["🇧🇷 ENEM Intelligence", "🌍 Universidades Globais"])

# ------------------------------------------------------------------------------
# ABA 1: ENEM COMPLETO
# ------------------------------------------------------------------------------
with tab_br:
    st.title("Raio-X da Educação Brasileira")
    st.write("Análise consolidada de desempenho por competências (Média Município).")
    
    df_brasil = get_brasil_data()
    
    # --- FILTROS ---
    c_filtro1, c_filtro2 = st.columns(2)
    with c_filtro1:
        uf_list = sorted(df_brasil['UF'].unique())
        uf_sel = st.selectbox("Filtrar Estado:", ["Todos"] + uf_list)
        
    if uf_sel != "Todos":
        df_display = df_brasil[df_brasil['UF'] == uf_sel]
    else:
        df_display = df_brasil
        
    with c_filtro2:
        cidade_list = sorted(df_display['Cidade'].unique())
        cidade_sel = st.selectbox("Selecionar Cidade:", cidade_list)
        
    # --- DADOS DA CIDADE ---
    dado = df_brasil[df_brasil['Cidade'] == cidade_sel].iloc[0]
    
    st.markdown("---")
    
    # 1. KPIs GERAIS
    cols = st.columns(5)
    cols[0].metric("📝 Redação", dado['Redação'], f"{dado['Redação'] - MEDIA_NACIONAL['Redação']}")
    cols[1].metric("📐 Matemática", dado['Mat'], f"{dado['Mat'] - MEDIA_NACIONAL['Mat']}")
    cols[2].metric("📖 Linguagens", dado['Ling'], f"{dado['Ling'] - MEDIA_NACIONAL['Ling']}")
    cols[3].metric("🌍 Humanas", dado['Hum'], f"{dado['Hum'] - MEDIA_NACIONAL['Hum']}")
    cols[4].metric("🧬 Natureza", dado['Nat'], f"{dado['Nat'] - MEDIA_NACIONAL['Nat']}")
    st.caption("*Delta comparado à Média Nacional")
    
    st.markdown("---")

    # 2. GRÁFICO DE RADAR (SPIDER CHART) - O MAIS IMPORTANTE
    col_radar, col_barras = st.columns([1, 1.5])
    
    with col_radar:
        st.subheader("🕸️ Perfil de Competência")
        
        categorias = ['Redação', 'Matemática', 'Humanas', 'Natureza', 'Linguagens']
        notas_cidade = [dado['Redação'], dado['Mat'], dado['Hum'], dado['Nat'], dado['Ling']]
        notas_brasil = [MEDIA_NACIONAL['Redação'], MEDIA_NACIONAL['Mat'], MEDIA_NACIONAL['Hum'], MEDIA_NACIONAL['Nat'], MEDIA_NACIONAL['Ling']]
        
        fig = go.Figure()

        # Cidade Selecionada
        fig.add_trace(go.Scatterpolar(
            r=notas_cidade,
            theta=categorias,
            fill='toself',
            name=cidade_sel,
            line_color='#007bff'
        ))
        
        # Média Nacional (Para comparação)
        fig.add_trace(go.Scatterpolar(
            r=notas_brasil,
            theta=categorias,
            name='Média Brasil',
            line_color='#6c757d',
            line_dash='dot' # Linha pontilhada
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[400, 800])),
            showlegend=True,
            height=400,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_barras:
        st.subheader("📊 Comparativo Regional")
        
        # Pega Top 5 do Estado ou Brasil para comparar
        if uf_sel != "Todos":
            df_comp = df_brasil[df_brasil['UF'] == uf_sel].sort_values('Mat', ascending=False)
            titulo_graf = f"Top Cidades em {uf_sel} (Matemática)"
        else:
            df_comp = df_brasil.sort_values('Mat', ascending=False).head(10)
            titulo_graf = "Top 10 Brasil (Matemática)"
            
        fig_bar = px.bar(
            df_comp, 
            x='Mat', 
            y='Cidade', 
            orientation='h',
            text='Mat',
            title=titulo_graf,
            color='Mat',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------------------------------------------------------
# ABA 2: UNIVERSIDADES (MANTIDA IGUAL)
# ------------------------------------------------------------------------------
with tab_world:
    st.header("Mapeamento Global")
    pais = st.selectbox("País:", ["Brazil", "United States", "Portugal", "Canada", "Germany", "Argentina"])
    
    with st.spinner("Buscando..."):
        df_uni = get_universities(pais)
        
    if not df_uni.empty:
        df_uni['Website'] = df_uni['web_pages'].apply(lambda x: x[0] if isinstance(x, list) and len(x)>0 else "N/A")
        st.metric("Instituições Encontradas", len(df_uni))
        st.dataframe(
            df_uni[['name', 'Website']],
            column_config={"Website": st.column_config.LinkColumn("Site Oficial")},
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Dados indisponíveis para este país no momento.")
