import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EduMetrix | Equidade", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    h1, h2 { color: #2c3e50 !important; }
    div[data-testid="stMetric"] {
        background-color: white; border-radius: 8px; padding: 10px; 
        border-left: 5px solid #6f42c1; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. GERADOR DE MICRODADOS (PROJETO EQUIDADE)
# ==============================================================================
@st.cache_data
def generate_microdados_socioeconomicos():
    """
    Simula o arquivo 'MICRODADOS_ENEM.csv' com viés estatístico real.
    Gera dados qualitativos que precisam ser transformados em números.
    """
    np.random.seed(42)
    n_alunos = 2000
    
    # Dicionários baseados no Q. Socioeconômico do ENEM
    # Q006: Renda Familiar
    renda_map = {
        'A': 'Nenhuma Renda', 
        'B': 'Até R$ 1.320', 
        'C': 'Até R$ 1.320 a R$ 2.640',
        'D': 'R$ 2.640 a R$ 6.600',
        'E': 'R$ 6.600 a R$ 13.200',
        'Q': 'Acima de R$ 20.000'
    }
    
    # Q002: Escolaridade Mãe
    escola_mae_map = {
        'A': 'Nunca estudou',
        'B': 'Ensino Fundamental incompleto',
        'D': 'Ensino Médio completo',
        'F': 'Ensino Superior completo',
        'G': 'Pós-graduação'
    }
    
    dados = []
    
    for _ in range(n_alunos):
        # Sorteia um perfil socioeconômico (Peso estatístico para classes C/D)
        perfil = np.random.choice(['Baixo', 'Medio', 'Alto'], p=[0.4, 0.4, 0.2])
        
        if perfil == 'Baixo':
            renda = np.random.choice(['A', 'B', 'C'])
            mae = np.random.choice(['A', 'B', 'D'])
            internet = np.random.choice(['Não', 'Sim'], p=[0.3, 0.7])
            nota_base = 450
        elif perfil == 'Medio':
            renda = np.random.choice(['C', 'D'])
            mae = np.random.choice(['D', 'F'])
            internet = 'Sim'
            nota_base = 600
        else: # Alto
            renda = np.random.choice(['E', 'Q'])
            mae = np.random.choice(['F', 'G'])
            internet = 'Sim'
            nota_base = 720
            
        # Adiciona ruído na nota (Aluno rico pode ir mal, pobre pode ir bem)
        nota_final = int(np.random.normal(nota_base, 80))
        nota_final = max(0, min(1000, nota_final)) # Limita entre 0 e 1000
        
        dados.append({
            "ID_Inscricao": np.random.randint(20000000, 99999999),
            "Q006_Renda": renda,
            "Q002_Escolaridade_Mae": mae,
            "Q025_Tem_Internet": internet,
            "NU_NOTA_GERAL": nota_final
        })
        
    return pd.DataFrame(dados)

# ==============================================================================
# 2. FUNÇÕES ANTERIORES (IBGE + ANALYTICS)
# ==============================================================================
@st.cache_data
def get_ibge_cidades(uf_sigla):
    try:
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_sigla}/municipios"
        r = requests.get(url, timeout=5)
        return pd.DataFrame([{ 'ID': i['id'], 'Nome': i['nome'], 'UF': uf_sigla } for i in r.json()])
    except: return pd.DataFrame()

@st.cache_data
def get_enem_analytics():
    data = [
        {"Cidade": "São Paulo", "UF": "SP", "Redação": 660, "Mat": 645, "Hum": 620, "Nat": 610},
        {"Cidade": "Fortaleza", "UF": "CE", "Redação": 650, "Mat": 635, "Hum": 620, "Nat": 610},
        {"Cidade": "Manaus", "UF": "AM", "Redação": 610, "Mat": 575, "Hum": 590, "Nat": 565},
        {"Cidade": "Porto Alegre", "UF": "RS", "Redação": 645, "Mat": 625, "Hum": 630, "Nat": 605},
        {"Cidade": "Brasília", "UF": "DF", "Redação": 660, "Mat": 635, "Hum": 640, "Nat": 615},
    ]
    return pd.DataFrame(data)

MEDIA_BR = {"Red": 590, "Mat": 540, "Hum": 560, "Nat": 530}

# ==============================================================================
# INTERFACE
# ==============================================================================
st.sidebar.image("https://img.icons8.com/nolan/96/diploma.png", width=80)
st.sidebar.title("EduMetrix")
st.sidebar.info("Módulos Ativos:\n1. ENEM Analytics\n2. Extrator IBGE\n3. Projeto Equidade (Novo)")

st.title("EduMetrix: Education Intelligence")

# 4 ABAS AGORA
tab_enem, tab_ibge, tab_equidade, tab_sobre = st.tabs([
    "📊 ENEM Analytics", 
    "📥 Extrator IBGE", 
    "⚖️ Projeto Equidade (ETL)", 
    "ℹ️ Sobre"
])

# --- TAB 1: ENEM ANALYTICS ---
with tab_enem:
    st.header("Analytics: Performance por Município")
    df_enem = get_enem_analytics()
    cidade_sel = st.selectbox("Cidade:", df_enem['Cidade'].unique())
    dado = df_enem[df_enem['Cidade'] == cidade_sel].iloc[0]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Matemática", dado['Mat'], f"{dado['Mat'] - MEDIA_BR['Mat']}")
    c2.metric("Redação", dado['Redação'], f"{dado['Redação'] - MEDIA_BR['Red']}")
    c3.metric("Natureza", dado['Nat'], f"{dado['Nat'] - MEDIA_BR['Nat']}")
    
    fig = go.Figure(go.Scatterpolar(
        r=[dado['Mat'], dado['Redação'], dado['Nat'], dado['Hum']],
        theta=['Matemática', 'Redação', 'Natureza', 'Humanas'],
        fill='toself', name=cidade_sel
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[400, 800])), height=300)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: IBGE ---
with tab_ibge:
    st.header("Conexão Governamental (IBGE)")
    uf_api = st.selectbox("UF:", ["SP", "RJ", "MG", "BA", "CE"])
    if st.button("📡 Buscar API IBGE"):
        df_ibge = get_ibge_cidades(uf_api)
        if not df_ibge.empty:
            st.dataframe(df_ibge, use_container_width=True)
            st.download_button("📥 Baixar Lista", df_ibge.to_csv().encode('utf-8'), f"ibge_{uf_api}.csv")

# --- TAB 3: PROJETO EQUIDADE (O CASE DO ALUNO) ---
with tab_equidade:
    st.header("⚖️ Projeto Equidade: O Desafio ETL")
    st.markdown("""
    **Contexto:** O governo quer criar um índice único (0 a 10) para medir a vulnerabilidade social dos alunos, 
    mas os dados originais vêm em formato de texto (Qualitativo).
    
    **Sua Missão:** Baixar os microdados brutos e converter as letras em números para análise.
    """)
    
    # 1. GERAÇÃO DOS DADOS BRUTOS
    st.subheader("1. Extração (Data Lake)")
    df_raw = generate_microdados_socioeconomicos()
    
    with st.expander("👀 Visualizar Microdados Brutos (Amostra)", expanded=True):
        st.dataframe(df_raw.head(10), use_container_width=True)
        
        csv_raw = df_raw.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Microdados Brutos (.CSV)",
            data=csv_raw,
            file_name="microdados_enem_bruto.csv",
            mime="text/csv",
            help="Use este arquivo para o exercício de ETL"
        )

    st.markdown("---")

    # 2. SOLUÇÃO DO PROFESSOR (ETL AUTOMATIZADO)
    st.subheader("2. Transformação (Pipeline ETL)")
    
    if st.checkbox("🔄 Executar Pipeline de Transformação (Mostrar Solução)"):
        with st.spinner("Calculando Índice Socioeconômico (ISE)..."):
            
            # CÓPIA PARA NÃO ALTERAR O ORIGINAL
            df_processed = df_raw.copy()
            
            # --- A LÓGICA DO ETL (O que o aluno deve aprender) ---
            
            # 1. Mapear Renda (A=0 ... Q=5)
            mapa_renda = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'Q': 5}
            df_processed['Score_Renda'] = df_processed['Q006_Renda'].map(mapa_renda)
            
            # 2. Mapear Escolaridade Mãe (A=0 ... G=5)
            mapa_esc = {'A': 0, 'B': 1, 'D': 2, 'F': 3, 'G': 4}
            df_processed['Score_Mae'] = df_processed['Q002_Escolaridade_Mae'].map(mapa_esc).fillna(0)
            
            # 3. Mapear Internet (Não=0, Sim=1)
            df_processed['Score_Internet'] = df_processed['Q025_Tem_Internet'].apply(lambda x: 1 if x == 'Sim' else 0)
            
            # 4. Fórmula do ISE (Normalizado de 0 a 10)
            # Soma máxima possível: 5 (Renda) + 4 (Mãe) + 1 (Internet) = 10 pontos
            df_processed['ISE_Calculado'] = df_processed['Score_Renda'] + df_processed['Score_Mae'] + df_processed['Score_Internet']
            
            # ----------------------------------------------------
            
            st.success("✅ ETL Concluído! Dados Transformados:")
            st.dataframe(df_processed[['ID_Inscricao', 'Q006_Renda', 'Score_Renda', 'ISE_Calculado', 'NU_NOTA_GERAL']].head(), use_container_width=True)
            
            # 3. ANÁLISE DE CORRELAÇÃO (O FINAL DO CASE)
            st.subheader("3. Análise de Correlação (Insight)")
            st.markdown("Existe relação entre **Condição Socioeconômica (ISE)** e a **Nota do Aluno**?")
            
            # Gráfico de Dispersão com Linha de Tendência
            fig_corr = px.scatter(
                df_processed, 
                x="ISE_Calculado", 
                y="NU_NOTA_GERAL",
                color="ISE_Calculado",
                title="Impacto do Índice Socioeconômico na Nota Geral",
                labels={"ISE_Calculado": "Índice Socioeconômico (0=Baixo, 10=Alto)", "NU_NOTA_GERAL": "Nota ENEM"},
                trendline="ols" # Linha de tendência (Regressão)
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            
            st.info("💡 **Conclusão:** Observe a linha de tendência. Se ela sobe, prova que alunos com ISE maior tendem a ter notas maiores, evidenciando a desigualdade.")

# --- TAB 4: SOBRE ---
with tab_sobre:
    st.write("EduMetrix v6.0 - Plataforma Educacional Integrada.")
