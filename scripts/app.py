import streamlit as st
import pandas as pd
import glob
import os

st.set_page_config(page_title="Painel de Resíduos Municipais", layout="wide")

st.title("📊 Diagnóstico de Resíduos Sólidos Municipais")
st.markdown("Dados processados via **Apache Spark** no cluster **Kubernetes**.")

# 1. Caminho correto conforme vimos no seu comando 'ls'
# Usamos o caminho da VM onde o arquivo part-*.csv realmente está
pasta_dados = "/dados-residuos/processado/resultado_residuos"
arquivos_csv = glob.glob(os.path.join(pasta_dados, "part-*.csv"))

if not arquivos_csv:
    st.error(f"Nenhum arquivo encontrado em {pasta_dados}. Verifique o caminho ou se o Spark terminou.")
else:
    @st.cache_data
    def carregar_dados(caminho):
        # Lemos o CSV gerado pelo Spark
        return pd.read_csv(caminho)
    
    df = carregar_dados(arquivos_csv[0])

    # 2. Sidebar com filtros
    st.sidebar.header("Configurações do Painel")
    
    lista_ufs = sorted(df['uf'].dropna().unique())
    uf_selecionada = st.sidebar.selectbox("Selecione o Estado (UF):", lista_ufs)

    df_uf = df[df['uf'] == uf_selecionada]
    lista_municipios = sorted(df_uf['municipio'].dropna().unique())
    municipio_selecionado = st.sidebar.selectbox("Selecione o Município:", lista_municipios)

    # Filtragem final
    dados_finais = df_uf[df_uf['municipio'] == municipio_selecionado].copy()

    # 3. Exibição
    st.subheader(f"📍 {municipio_selecionado} - {uf_selecionada}")

    if dados_finais.empty or dados_finais['total_toneladas'].sum() == 0:
        st.warning("Sem dados de massa registrados para este município.")
    else:
        # Métricas principais
        total_lixo = dados_finais['total_toneladas'].sum()
        num_categorias = dados_finais['categoria'].nunique()
        
        col1, col2 = st.columns(2)
        col1.metric("Total Declarado", f"{total_lixo:,.2f} TON")
        col2.metric("Categorias Registradas", num_categorias)

        # Gráfico de Barras
        st.write("### Massa por Categoria")
        # Preparamos os dados para o gráfico não dar erro de índice
        graf_data = dados_finais.groupby("categoria")["total_toneladas"].sum().sort_values(ascending=False)
        st.bar_chart(graf_data)

        with st.expander("👁️ Ver detalhes dos dados"):
            st.dataframe(dados_finais.sort_values("total_toneladas", ascending=False))

st.sidebar.markdown("---")
st.sidebar.info("Projeto IaaS - Gestão de Resíduos")