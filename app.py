import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EduMetrix | Global Intelligence", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #333; }
    h1 { color: #4b0082 !important; font-family: 'Arial', sans-serif; }
    div[data-testid="stMetric"] {
        background-color: white; border-radius: 10px; padding: 15px;
        border-left: 5px solid #4b0082; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE COLETA (API REAL) ---
@st.cache_data
def get_universities(country_name):
    """
    Busca lista real de universidades na API Hipolabs.
    Não requer chave de API.
    """
    # URL da API Pública
    url = f"http://universities.hipolabs.com/search?country={country_name}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Se não achar nada (ex: digitou país errado)
            if not data: return pd.DataFrame()
            
            # Tratamento de Dados (ETL)
            lista_limpa = []
            for uni in data:
                # A API retorna domínios e sites como listas, pegamos o primeiro item
                site = uni['web_pages'][0] if uni.get('web_pages') else "N/A"
                dominio = uni['domains'][0] if uni.get('domains') else "N/A"
                
                lista_limpa.append({
                    "Instituição": uni['name'],
                    "País": uni['country'],
                    "Sigla_País": uni['alpha_two_code'],
                    "Website": site,
                    "Domínio": dominio,
                    "Estado/Província": uni.get('state-province') # Nem sempre preenchido pela API
                })
            
            return pd.DataFrame(lista_limpa)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return pd.DataFrame()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/university.png", width=80)
    st.title("EduMetrix")
    st.caption("Intelligence Acadêmica")
    st.markdown("---")
    
    # Filtro de País (Com sugestões)
    pais_selecionado = st.selectbox(
        "🌍 Selecione o País:",
        ["Brazil", "United States", "Portugal", "United Kingdom", "Canada", "Germany", "Argentina", "Japan"],
        index=0
    )
    
    st.info("Fonte: Hipolabs University Data")

# --- DASHBOARD ---
st.title(f"Mapeamento Acadêmico: {pais_selecionado}")

with st.spinner(f"Buscando instituições em {pais_selecionado}..."):
    df = get_universities(pais_selecionado)

if not df.empty:
    
    # 1. KPIs
    col1, col2, col3 = st.columns(3)
    
    total_unis = len(df)
    total_sites = df[df['Website'] != "N/A"].shape[0]
    # Conta quantos domínios terminam em .edu ou .br (Exemplo de análise)
    sufixo_comum = df['Domínio'].apply(lambda x: x.split('.')[-1]).mode()[0]
    
    col1.metric("Instituições Mapeadas", total_unis)
    col2.metric("Presença Digital (Sites)", f"{total_sites}", f"{(total_sites/total_unis)*100:.0f}% Cobertura")
    col3.metric("Sufixo de Domínio Comum", f".{sufixo_comum}")
    
    st.markdown("---")
    
    # 2. GRÁFICOS E ANÁLISE
    c_chart, c_table = st.columns([1, 2])
    
    with c_chart:
        st.subheader("📊 Distribuição")
        
        # Se o país tiver dados de Estado/Província preenchidos (EUA/Brasil costumam ter)
        # Vamos contar por estado. Se tudo for None, mostramos aviso.
        
        # Limpeza para gráfico: Troca None por "Não Informado"
        df_chart = df.copy()
        df_chart['Estado/Província'] = df_chart['Estado/Província'].fillna("Geral / Não Informado")
        
        contagem_estados = df_chart['Estado/Província'].value_counts().reset_index()
        contagem_estados.columns = ['Região', 'Qtd']
        
        # Só mostra gráfico se tivermos mais de 1 região diferente
        if len(contagem_estados) > 1:
            fig = px.pie(contagem_estados.head(10), values='Qtd', names='Região', title="Top 10 Regiões", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Dados de regionalização (Estados) não disponíveis para este país na API.")
            st.caption("Analisando apenas lista federal.")

    with c_table:
        st.subheader("🏫 Diretório de Universidades")
        
        # Campo de busca textual
        busca = st.text_input("🔍 Buscar Instituição:", placeholder="Ex: Federal, Harvard, Tecnológica...")
        
        if busca:
            df_display = df[df['Instituição'].str.contains(busca, case=False)]
        else:
            df_display = df
            
        # Tabela Interativa com Links
        st.dataframe(
            df_display[['Instituição', 'Estado/Província', 'Website']],
            column_config={
                "Website": st.column_config.LinkColumn("Portal Oficial"),
                "Instituição": st.column_config.TextColumn("Nome", width="medium")
            },
            hide_index=True,
            use_container_width=True,
            height=400
        )

    # 3. DOWNLOAD
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Relatório (CSV)", csv, f"universities_{pais_selecionado}.csv", "text/csv")

else:
    st.error("Nenhuma universidade encontrada ou erro na API. Tente outro país (em inglês).")
