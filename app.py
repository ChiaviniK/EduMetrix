import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# --- Configuração GovTech ---
st.set_page_config(page_title="EduMetrix | GovTech", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    /* Estilo Governo Digital (Azul Marinho, Cinza, Branco) */
    .stApp { background-color: #f8f9fa; color: #333333; }
    h1, h2, h3 { color: #003366 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 8px;
        border-left: 5px solid #003366;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Botões */
    .stButton>button {
        background-color: #003366; color: white; border-radius: 4px; border: none;
    }
</style>
""", unsafe_allow_html=True)

# --- INTEGRAÇÃO API IBGE (REAL-TIME) ---
@st.cache_data
def get_ibge_states():
    """Busca lista de estados reais na API do IBGE"""
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    try:
        response = requests.get(url)
        df = pd.DataFrame(response.json())
        return df[['sigla', 'nome', 'id']].sort_values('nome')
    except:
        return pd.DataFrame({'sigla': ['SP', 'RJ'], 'nome': ['São Paulo', 'Rio de Janeiro']})

@st.cache_data
def get_ibge_cities(uf_id):
    """Busca cidades de um estado na API do IBGE"""
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_id}/municipios"
    try:
        response = requests.get(url)
        df = pd.DataFrame(response.json())
        return df[['nome', 'id']]
    except:
        return pd.DataFrame()

# --- GERADOR DE DADOS EDUCACIONAIS (MOCK AVANÇADO) ---
# Simula o Microdado do INEP processado (já que é inviável baixar 5GB aqui)
def generate_school_data(city_name, n_schools=50):
    np.random.seed(42)
    
    data = []
    types = ['Pública (Municipal)', 'Pública (Estadual)', 'Privada']
    
    for _ in range(n_schools):
        tipo = np.random.choice(types, p=[0.5, 0.4, 0.1])
        
        # Criação do ISE (Índice Socioeconômico) - Escala 1 a 10
        # Privadas tem ISE maior
        base_ise = 7.0 if tipo == 'Privada' else 4.0
        ise = np.clip(np.random.normal(base_ise, 1.5), 1, 10)
        
        # Nota esperada baseada no ISE (Correlação forte)
        # Nota = Base + (Fator * ISE) + Ruído
        expected_score = 400 + (30 * ise) + np.random.normal(0, 20)
        
        # ADICIONANDO OUTLIERS (O "Milagre" ou o "Desastre")
        # Eficiência = O quanto a escola performa ACIMA do esperado para o ISE dela
        efficiency = np.random.normal(0, 15) 
        
        # Algumas escolas públicas pobres com gestão excelente (Milagres)
        if tipo != 'Privada' and ise < 4 and np.random.random() > 0.9:
            efficiency += 60 # Boost enorme
            
        final_score = expected_score + efficiency
        
        data.append({
            'Escola': f"Escola {np.random.randint(100,999)} {city_name}",
            'Rede': tipo,
            'ISE_Medio': round(ise, 2), # Nível socioeconômico dos alunos
            'Nota_IDEB': round(final_score / 100, 1), # Simulando IDEB
            'Nota_ENEM': round(final_score, 0),
            'Valor_Adicionado': round(efficiency, 2) # A métrica chave
        })
    
    return pd.DataFrame(data)

# --- SIDEBAR ---
states_df = get_ibge_states()

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Brazil_State_of_S%C3%A3o_Paulo_COA.svg/1200px-Brazil_State_of_S%C3%A3o_Paulo_COA.svg.png", width=60)
    st.title("EduMetrix")
    st.caption("Sistema de Monitoramento da Eficiência Escolar")
    
    st.markdown("---")
    
    # Filtro Dinâmico via API IBGE
    uf_select = st.selectbox("Selecione o Estado (API IBGE):", states_df['sigla'])
    
    # Pega ID do estado para buscar cidades
    uf_id = states_df[states_df['sigla'] == uf_select]['id'].values[0]
    cities_df = get_ibge_cities(uf_id)
    
    if not cities_df.empty:
        city_select = st.selectbox("Selecione o Município:", cities_df['nome'])
    else:
        city_select = "Exemplo"

    st.markdown("---")
    st.info("Modelo de Valor Adicionado: Regressão Linear (ISE x Nota)")

# --- CARGA DE DADOS ---
df_schools = generate_school_data(city_select)

# --- ANÁLISE ESTATÍSTICA (O CÉREBRO) ---
# Calculando a Linha de Tendência (O Esperado)
X = df_schools[['ISE_Medio']]
y = df_schools[['Nota_ENEM']]
model = LinearRegression().fit(X, y)
df_schools['Nota_Esperada'] = model.predict(X)
df_schools['Delta_Performance'] = df_schools['Nota_ENEM'] - df_schools['Nota_Esperada']

# Classificação
def classify_school(row):
    if row['Delta_Performance'] > 40: return "💎 Superação (Outlier Positivo)"
    if row['Delta_Performance'] < -40: return "⚠️ Alerta Crítico (Ineficiente)"
    return "Dentro do Esperado"

df_schools['Status'] = df_schools.apply(classify_school, axis=1)

# --- DASHBOARD ---
st.title(f"Diagnóstico Educacional: {city_select}/{uf_select}")

# KPIs
col1, col2, col3, col4 = st.columns(4)
media_enem = df_schools['Nota_ENEM'].mean()
media_ise = df_schools['ISE_Medio'].mean()
n_superacao = len(df_schools[df_schools['Status'].str.contains("Superação")])

with col1: st.metric("Média ENEM (Geral)", f"{media_enem:.0f}")
with col2: st.metric("ISE Médio (Renda)", f"{media_ise:.1f}", help="Índice de Nível Socioeconômico (1-10)")
with col3: st.metric("Escolas 'Milagre'", n_superacao, delta="Alta Eficiência", delta_color="normal")
with col4: st.metric("Distorção IDH", f"R²: {model.score(X, y):.2f}", help="Quanto a renda explica a nota (R²)")

st.markdown("---")

# GRÁFICO AVANÇADO DE DISPERSÃO (SCATTER PLOT)
# É aqui que o especialista vê valor. Quem está ACIMA da linha é bom, quem está ABAIXO é ruim.
st.subheader("🔍 Matriz de Equidade: Renda vs. Aprendizado")
st.caption("A linha representa o desempenho esperado para cada nível de renda. Escolas acima da linha geram Valor Adicionado positivo.")

fig = px.scatter(
    df_schools, 
    x="ISE_Medio", 
    y="Nota_ENEM", 
    color="Status", 
    size="Nota_IDEB",
    hover_name="Escola",
    trendline="ols", # Adiciona a linha de regressão
    color_discrete_map={
        "💎 Superação (Outlier Positivo)": "#00cc99",
        "Dentro do Esperado": "#3366cc",
        "⚠️ Alerta Crítico (Ineficiente)": "#ff3333"
    }
)
fig.update_layout(
    xaxis_title="Nível Socioeconômico (ISE)",
    yaxis_title="Nota Média ENEM",
    template="plotly_white",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# TABELA DE GESTÃO
st.subheader("📋 Escolas Prioritárias para Intervenção")
col_tab1, col_tab2 = st.columns(2)

with col_tab1:
    st.markdown("**💎 Escolas Modelo (Benchmarking)**")
    st.dataframe(
        df_schools[df_schools['Delta_Performance'] > 0]
        .sort_values('Delta_Performance', ascending=False)
        .head(5)[['Escola', 'Rede', 'Nota_ENEM', 'Delta_Performance']],
        use_container_width=True,
        hide_index=True
    )

with col_tab2:
    st.markdown("**⚠️ Escolas em Risco (Abaixo do Esperado)**")
    st.dataframe(
        df_schools[df_schools['Delta_Performance'] < 0]
        .sort_values('Delta_Performance', ascending=True)
        .head(5)[['Escola', 'Rede', 'Nota_ENEM', 'Delta_Performance']],
        use_container_width=True,
        hide_index=True
    )

# DOWNLOAD AREA
st.markdown("---")
st.info("Microdados processados com a metodologia de Valor Adicionado (V.A.).")
csv = df_schools.to_csv().encode('utf-8')
st.download_button("📥 Baixar Relatório Técnico (CSV)", csv, "relatorio_equidade.csv", "text/csv")
