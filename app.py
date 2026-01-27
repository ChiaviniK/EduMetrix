import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EduMetrix | Full Data", page_icon="🎓", layout="wide")

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
# ATUALIZAÇÃO: GERADOR DE MICRODADOS COM GEOLOCALIZAÇÃO
# ==============================================================================
@st.cache_data
def generate_microdados_socioeconomicos():
    """
    Gera microdados simulados do ENEM contendo:
    1. ID único
    2. Localização (Cidade/UF)
    3. Respostas Socioeconômicas
    """
    np.random.seed(42)
    n_alunos = 3000 # Aumentei um pouco a amostra
    
    # Lista de Cidades para distribuir os alunos
    # (Pesos simulam que cidades maiores têm mais inscritos)
    locais = [
        {"Cidade": "São Paulo", "UF": "SP", "Peso": 0.35},
        {"Cidade": "Rio de Janeiro", "UF": "RJ", "Peso": 0.25},
        {"Cidade": "Belo Horizonte", "UF": "MG", "Peso": 0.15},
        {"Cidade": "Fortaleza", "UF": "CE", "Peso": 0.10},
        {"Cidade": "Porto Alegre", "UF": "RS", "Peso": 0.05},
        {"Cidade": "Manaus", "UF": "AM", "Peso": 0.05},
        {"Cidade": "Brasília", "UF": "DF", "Peso": 0.05}
    ]
    
    cidades_nomes = [l['Cidade'] for l in locais]
    cidades_pesos = [l['Peso'] for l in locais]
    
    dados = []
    
    for _ in range(n_alunos):
        # 1. Sorteia a Cidade do Aluno
        cidade_escolhida = np.random.choice(cidades_nomes, p=cidades_pesos)
        # Pega a UF correspondente
        uf_escolhida = next(item['UF'] for item in locais if item['Cidade'] == cidade_escolhida)
        
        # 2. Sorteia o Perfil Socioeconômico (Renda/Mãe)
        # Adicionei variação regional: SP e DF tendem a ter renda levemente maior na simulação
        chance_rico = 0.3 if uf_escolhida in ['SP', 'DF'] else 0.15
        perfil = np.random.choice(['Baixo', 'Medio', 'Alto'], p=[0.5, 0.5-chance_rico, chance_rico])
        
        if perfil == 'Baixo':
            renda = np.random.choice(['A', 'B', 'C'])
            mae = np.random.choice(['A', 'B', 'D'])
            internet = np.random.choice(['Não', 'Sim'], p=[0.4, 0.6])
            nota_base = 480
        elif perfil == 'Medio':
            renda = np.random.choice(['C', 'D'])
            mae = np.random.choice(['D', 'F'])
            internet = 'Sim'
            nota_base = 620
        else: # Alto
            renda = np.random.choice(['E', 'Q'])
            mae = np.random.choice(['F', 'G'])
            internet = 'Sim'
            nota_base = 740
            
        # Ruído na nota
        nota_final = int(np.random.normal(nota_base, 70))
        nota_final = max(0, min(1000, nota_final))
        
        dados.append({
            "ID_Inscricao": np.random.randint(100000000000, 999999999999), # ID Longo padrão INEP
            "SG_UF_RESIDENCIA": uf_escolhida,  # Nome oficial da coluna no INEP
            "NO_MUNICIPIO_RESIDENCIA": cidade_escolhida, # Nome oficial da coluna no INEP
            "Q006_Renda": renda,
            "Q002_Escolaridade_Mae": mae,
            "Q025_Tem_Internet": internet,
            "NU_NOTA_GERAL": nota_final
        })
        
    return pd.DataFrame(dados)

# ... (O resto das funções get_ibge_cidades e get_enem_analytics mantêm-se iguais) ...

# ==============================================================================
# INTERFACE (Aba Equidade Atualizada)
# ==============================================================================

# ... (Código da Tab 1 e Tab 2 igual) ...

# --- TAB 3: PROJETO EQUIDADE ---
# Copie e cole isso dentro da estrutura 'with tab_equidade:'
    
    st.header("⚖️ Projeto Equidade: Dados Georreferenciados")
    st.markdown("""
    **Atualização v7.0:** Agora os microdados incluem a cidade de residência do aluno.
    Isso permite cruzar **Desigualdade Social** com **Localização Geográfica**.
    """)
    
    # 1. GERAÇÃO
    df_raw = generate_microdados_socioeconomicos()
    
    with st.expander("👀 Visualizar Microdados (Com Cidade)", expanded=True):
        # Mostra as novas colunas
        st.dataframe(df_raw[['ID_Inscricao', 'NO_MUNICIPIO_RESIDENCIA', 'Q006_Renda', 'NU_NOTA_GERAL']].head(10), use_container_width=True)
        
        csv_raw = df_raw.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Microdados Completos (.CSV)", csv_raw, "microdados_enem_geo.csv", "text/csv")

    st.markdown("---")

    # 2. TRANSFORMADOR (ETL)
    if st.checkbox("🔄 Executar ETL e Análise Regional"):
        # Pipeline de Transformação (Igual ao anterior)
        df_processed = df_raw.copy()
        mapa_renda = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'Q': 5}
        mapa_esc = {'A': 0, 'B': 1, 'D': 2, 'F': 3, 'G': 4}
        
        df_processed['ISE'] = df_processed['Q006_Renda'].map(mapa_renda) + \
                              df_processed['Q002_Escolaridade_Mae'].map(mapa_esc) + \
                              df_processed['Q025_Tem_Internet'].apply(lambda x: 1 if x=='Sim' else 0)
        
        # 3. ANÁLISE REGIONAL (A NOVIDADE)
        st.subheader("3. Comparativo de Equidade por Cidade")
        
        # Agrupa por Cidade para ver a média de ISE e Nota
        df_agrupado = df_processed.groupby("NO_MUNICIPIO_RESIDENCIA")[['ISE', 'NU_NOTA_GERAL']].mean().reset_index()
        df_agrupado['ISE'] = df_agrupado['ISE'].round(2)
        df_agrupado['NU_NOTA_GERAL'] = df_agrupado['NU_NOTA_GERAL'].round(0)
        
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.caption("Média de Índice Socioeconômico (ISE) por Cidade")
            fig_bar = px.bar(
                df_agrupado.sort_values('ISE', ascending=True), 
                x='ISE', y='NO_MUNICIPIO_RESIDENCIA', orientation='h',
                color='ISE', title="Ranking de Privilégio (ISE Médio)",
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_graf2:
            st.caption("Correlação: Riqueza da Cidade vs Nota")
            fig_scat = px.scatter(
                df_agrupado, x='ISE', y='NU_NOTA_GERAL',
                size='NU_NOTA_GERAL', text='NO_MUNICIPIO_RESIDENCIA',
                title="Desempenho vs ISE (Média Municipal)"
            )
            st.plotly_chart(fig_scat, use_container_width=True)
            
        st.success("✅ Dados cruzados com sucesso! Agora sabemos não só QUEM tem ISE baixo, mas ONDE eles moram.")
