"""
BananaSys - Aplicação Pública de Rastreabilidade
Aplicação Streamlit dedicada APENAS para consulta pública via QR code
Este arquivo será publicado na web (não requer autenticação)
"""

import streamlit as st
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Rastreabilidade de Banana - Bananas Prata Ouro",
    page_icon="🍌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar menu e rodapé do Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Importar página pública
from ui.rastreabilidade_publica_arquivo import (
    pagina_consulta_publica_arquivo,
    pagina_consulta_publica_landing_arquivo
)

# Verificar query parameter
query_params = st.query_params

# Obter código do palete
codigo_palete = None

# Tentar obter o parâmetro 'palete'
try:
    if "palete" in query_params:
        codigo_palete = str(query_params.get("palete", "")).strip()
        if not codigo_palete:
            codigo_palete = None
except Exception:
    codigo_palete = None

# Se encontrou código do palete, mostrar página completa
if codigo_palete:
    pagina_consulta_publica_arquivo(codigo_palete)
else:
    # Página inicial (landing page)
    pagina_consulta_publica_landing_arquivo()

