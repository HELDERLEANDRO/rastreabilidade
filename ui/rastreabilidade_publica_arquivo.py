"""
BananaSys - Consulta Pública de Rastreabilidade via Arquivo
Versão que lê dados de arquivo JSON/TXT (sem banco de dados)
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
from pathlib import Path


@st.cache_data(ttl=300)  # Cache de 5 minutos
def carregar_dados_arquivo():
    """
    Carrega dados de rastreabilidade do arquivo JSON/TXT
    """
    projeto_root = Path(__file__).parent.parent
    
    # Tentar carregar JSON primeiro
    arquivo_json = projeto_root / "dados_rastreabilidade.json"
    if arquivo_json.exists():
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            return dados, 'json'
        except Exception as e:
            st.error(f"Erro ao ler arquivo JSON: {e}")
    
    # Tentar carregar TXT como fallback
    arquivo_txt = projeto_root / "dados_rastreabilidade.txt"
    if arquivo_txt.exists():
        try:
            dados = _ler_arquivo_txt(arquivo_txt)
            return dados, 'txt'
        except Exception as e:
            st.error(f"Erro ao ler arquivo TXT: {e}")
    
    return None, None


def _ler_arquivo_txt(arquivo_txt):
    """Lê arquivo TXT e converte para formato estruturado"""
    dados_estruturados = {
        'paletes': {}
    }
    
    with open(arquivo_txt, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    palete_atual = None
    dados_palete = {}
    
    for linha in linhas:
        linha = linha.strip()
        
        # Ignorar comentários e linhas vazias
        if not linha or linha.startswith('#'):
            continue
        
        # Processar linha
        if linha.startswith('PALETE:'):
            # Salvar palete anterior
            if palete_atual and dados_palete:
                dados_estruturados['paletes'][palete_atual] = dados_palete
            
            # Novo palete
            palete_atual = linha.split(':', 1)[1].upper().strip()
            dados_palete = {}
        
        elif ':' in linha and palete_atual:
            chave, valor = linha.split(':', 1)
            chave = chave.strip().lower()
            valor = valor.strip()
            
            # Converter tipos
            if chave in ['latitude', 'longitude']:
                try:
                    valor = float(valor)
                except:
                    valor = None
            
            dados_palete[chave] = valor
    
    # Salvar último palete
    if palete_atual and dados_palete:
        dados_estruturados['paletes'][palete_atual] = dados_palete
    
    return dados_estruturados


@st.cache_data(ttl=300)
def buscar_palete_por_codigo(codigo_palete: str):
    """
    Busca dados do palete no arquivo
    """
    dados_arquivo, formato = carregar_dados_arquivo()
    
    if not dados_arquivo:
        return None
    
    codigo_normalizado = codigo_palete.strip().upper()
    
    return dados_arquivo['paletes'].get(codigo_normalizado)


def formatar_data(data_str):
    """Formata data de forma simples"""
    try:
        if isinstance(data_str, str):
            # Tentar diferentes formatos
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    data = datetime.strptime(data_str.split('T')[0], fmt.split('T')[0])
                    return data.strftime("%d/%m/%Y")
                except:
                    continue
        return str(data_str)
    except:
        return str(data_str)


def pagina_consulta_publica_arquivo(codigo_palete: str):
    """
    Página pública que lê dados de arquivo (sem banco de dados)
    Layout compacto e organizado
    """
    
    # Ocultar menu e rodapé do Streamlit + Estilos compactos
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    /* Reduzir espaçamento geral - colar no topo */
    .main .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0.3rem !important;
        max-width: 1200px;
    }
    /* Reduzir espaçamento entre elementos */
    .element-container {
        margin-bottom: 0.2rem !important;
    }
    /* Reduzir tamanho de títulos */
    h3 {
        font-size: 14px !important;
        margin-bottom: 5px !important;
    }
    /* Reduzir espaçamento de imagens */
    .stImage {
        margin-bottom: 0.2rem !important;
    }
    /* Reduzir espaçamento de markdown */
    .stMarkdown {
        margin-bottom: 0.2rem !important;
    }
    /* Alinhar colunas no topo */
    [data-testid="column"] {
        align-items: flex-start !important;
    }
    [data-testid="column"] > div {
        padding-top: 0 !important;
    }
    /* Garantir que textos do header sejam grandes */
    #header-texto-empresa {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #2d8659 !important;
        margin-bottom: 8px !important;
        line-height: 1.3 !important;
    }
    #header-texto-rastreabilidade {
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #333 !important;
        margin-bottom: 6px !important;
        line-height: 1.3 !important;
    }
    #header-texto-origem {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #666 !important;
        line-height: 1.4 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Buscar dados do arquivo
    dados = buscar_palete_por_codigo(codigo_palete)
    
    if not dados:
        st.error("❌ Palete não encontrado")
        return
    
    # Preparar dados para exibição
    codigo_palete_display = dados.get('palete_codigo', codigo_palete.upper())
    data_criacao_formatada = formatar_data(dados.get('data_criacao', '')) if dados.get('data_criacao') else 'N/A'
    lote_codigo = dados.get('lote_codigo', 'N/A')
    data_corte_formatada = formatar_data(dados.get('data_corte', '')) if dados.get('data_corte') else 'N/A'
    variedade = dados.get('variedade_nome_unificado', 'N/A')
    talhao_nome = dados.get('talhao_nome', 'N/A')
    talhao_codigo = dados.get('talhao_codigo', 'N/A')
    talhao_descricao = dados.get('talhao_descricao', '')
    empresa_nome = dados.get('empresa_nome', 'N/A')
    empresa_cidade = dados.get('empresa_cidade', '')
    empresa_estado = dados.get('empresa_estado', '')
    
    # Logo e nome da empresa no topo - Logo à esquerda, retângulo vermelho à direita
    projeto_root = Path(__file__).parent.parent
    logo_path = projeto_root / "nova_logo_bananal.png"
    
    # Preparar logo em base64 ou HTML
    logo_html = ""
    if logo_path.exists():
        import base64
        with open(logo_path, "rb") as f:
            logo_bytes = f.read()
            logo_base64 = base64.b64encode(logo_bytes).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="width: 150px; height: auto; display: block;" alt="Logo">'
    else:
        logo_html = '<div style="font-size: 40px; margin-bottom: 2px;">🍌</div>'
    
    # Container único com flexbox para alinhar logo e retângulo no topo
    st.markdown(
        f"""
        <div style="display: flex; align-items: flex-start; gap: 15px; margin-bottom: 5px;">
            <div style="flex-shrink: 0;">
                {logo_html}
            </div>
            <div style="flex: 1; padding: 15px 20px;">
                <div id="header-texto-empresa" style="font-size: 32px !important; font-weight: 700 !important; color: #2d8659 !important; margin-bottom: 8px !important; line-height: 1.3 !important;">
                    Fazenda e Distribuidora Bananas Prata Ouro
                </div>
                <div id="header-texto-rastreabilidade" style="font-size: 26px !important; font-weight: 700 !important; color: #333 !important; margin-bottom: 6px !important; line-height: 1.3 !important;">
                    Rastreabilidade de Banana
                </div>
                <div id="header-texto-origem" style="font-size: 20px !important; font-weight: 700 !important; color: #666 !important; line-height: 1.4 !important;">
                    Origem garantida, da colheita até a gôndola do supermercado.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Preparar coordenadas para card de localização
    coordenadas_html = ''
    if dados.get('latitude') and dados.get('longitude'):
        lat = dados.get('latitude', '')
        lon = dados.get('longitude', '')
        coordenadas_html = f'<div style="font-size: 11px; color: #333; margin-top: 2px;"><strong>Coordenadas:</strong> {lat}, {lon}</div>'
    else:
        coordenadas_html = '<div style="font-size: 11px; color: #666;">Coordenadas: N/A</div>'
    
    # Cards informativos (5 colunas) - Layout compacto - Todos na mesma linha
    st.markdown(
        f"""
        <div class="cards-grid" style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin: 6px 0;">
            <!-- Card Lote -->
            <div style="background: #f0f9f4; border-left: 4px solid #4CAF50; padding: 8px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.08);">
                <div style="font-size: 18px; margin-bottom: 3px;">🌱</div>
                <div style="font-weight: bold; color: #4CAF50; font-size: 10px; margin-bottom: 3px;">Lote</div>
                <div style="font-size: 12px; font-weight: bold; color: #333; margin-bottom: 2px; word-break: break-all;">{lote_codigo}</div>
                <div style="font-size: 9px; color: #666;">Data Colheita: {data_corte_formatada}</div>
            </div>
            <!-- Card Talhão -->
            <div style="background: #f0f9f4; border-left: 4px solid #FF9800; padding: 8px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.08);">
                <div style="font-size: 18px; margin-bottom: 3px;">🌾</div>
                <div style="font-weight: bold; color: #FF9800; font-size: 10px; margin-bottom: 3px;">Talhão</div>
                <div style="font-size: 12px; font-weight: bold; color: #333; margin-bottom: 2px;">{talhao_codigo}</div>
                <div style="font-size: 9px; color: #666;">{talhao_descricao if talhao_descricao else talhao_nome}</div>
            </div>
            <!-- Card Variedade -->
            <div style="background: #f0f9f4; border-left: 4px solid #9C27B0; padding: 8px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.08);">
                <div style="font-size: 18px; margin-bottom: 3px;">🍌</div>
                <div style="font-weight: bold; color: #9C27B0; font-size: 10px; margin-bottom: 3px;">Variedade</div>
                <div style="font-size: 12px; font-weight: bold; color: #333; margin-top: 3px;">{variedade}</div>
            </div>
            <!-- Card Detalhes -->
            <div style="background: #f9f9f9; border-left: 4px solid #2d8659; padding: 8px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.08); border: 1px solid #e0e0e0;">
                <div style="font-size: 18px; margin-bottom: 3px;">📋</div>
                <div style="font-weight: bold; color: #2d8659; font-size: 10px; margin-bottom: 3px;">Detalhes</div>
                <div style="font-size: 11px; line-height: 1.4;">
                    <div style="margin-bottom: 2px;"><strong>Palete:</strong> <code style="background: #f0f0f0; padding: 1px 3px; border-radius: 2px; font-size: 9px;">{codigo_palete_display}</code></div>
                    <div style="margin-bottom: 2px;"><strong>Lote:</strong> <code style="background: #f0f0f0; padding: 1px 3px; border-radius: 2px; font-size: 9px;">{lote_codigo}</code></div>
                    <div><strong>Data Colheita:</strong> {data_corte_formatada}</div>
                </div>
            </div>
            <!-- Card Localização -->
            <div style="background: #f9f9f9; border-left: 4px solid #e91e63; padding: 8px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.08); border: 1px solid #e0e0e0;">
                <div style="font-size: 18px; margin-bottom: 3px;">📍</div>
                <div style="font-weight: bold; color: #e91e63; font-size: 10px; margin-bottom: 3px;">Localização</div>
                <div style="font-size: 11px; line-height: 1.4;">
                    {coordenadas_html}
                </div>
            </div>
        </div>
        <style>
        @media (max-width: 1200px) {{
            .cards-grid {{
                grid-template-columns: repeat(3, 1fr) !important;
            }}
        }}
        @media (max-width: 768px) {{
            .cards-grid {{
                grid-template-columns: repeat(2, 1fr) !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Mapa (altura reduzida)
    if dados.get('latitude') and dados.get('longitude'):
        try:
            latitude = float(dados['latitude'])
            longitude = float(dados['longitude'])
            
            st.markdown(
                """
                <div style="margin: 6px 0 4px 0;">
                    <h3 style="font-size: 13px; margin: 0; color: #2d8659; display: flex; align-items: center; gap: 3px;">
                        <span>🗺️</span> Localização do Talhão
                    </h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            # Google Maps embed (altura reduzida para 250px)
            google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}&t=k&z=16&output=embed"
            
            components.html(
                f"""
                <iframe
                    width="100%"
                    height="250"
                    frameborder="0"
                    style="border:0; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);"
                    src="{google_maps_url}"
                    allowfullscreen
                    loading="lazy">
                </iframe>
                """,
                height=270
            )
            
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 8px;">
                    <a href="https://www.google.com/maps?q={latitude},{longitude}" 
                       target="_blank" 
                       style="display: inline-block; padding: 8px 16px; background-color: #2d8659; 
                              color: white; text-decoration: none; border-radius: 5px; 
                              font-weight: bold; font-size: 13px; transition: background-color 0.3s;">
                        🗺️ Abrir no Google Maps
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            pass
    
    # QR Code + Compartilhar (lado a lado) - Layout compacto
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    
    col_qr, col_share = st.columns([1, 2])
    
    with col_qr:
        st.markdown("#### 🔍 QR Code")
        qr_code_url = dados.get('qr_code_url')
        qr_png_bytes = None
        
        if qr_code_url:
            try:
                st.image(qr_code_url, width=130)
                # Tentar extrair bytes do QR code para download
                if "," in qr_code_url:
                    import base64
                    qr_png_bytes = base64.b64decode(qr_code_url.split(",", 1)[1])
            except:
                st.info("QR Code disponível")
        else:
            st.info("QR Code não disponível")
        
        # Botões de download do QR (compactos)
        if qr_png_bytes:
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.download_button(
                    "📥 PNG",
                    data=qr_png_bytes,
                    file_name=f"{codigo_palete_display}_qr.png",
                    mime="image/png",
                    use_container_width=True,
                )
            with col_btn2:
                try:
                    from io import BytesIO
                    from PIL import Image
                    pdf_buffer = BytesIO()
                    Image.open(BytesIO(qr_png_bytes)).save(pdf_buffer, format="PDF", resolution=300.0)
                    pdf_buffer.seek(0)
                    st.download_button(
                        "📄 PDF",
                        data=pdf_buffer,
                        file_name=f"{codigo_palete_display}_qr.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except:
                    pass
    
    with col_share:
        st.markdown("#### 📣 Compartilhar")
        try:
            from core.config import Config
            share_url = f"{Config.get_rastreabilidade_url_base()}?palete={codigo_palete_display}"
        except:
            # Fallback: usar URL relativa se não conseguir obter URL base
            share_url = f"?palete={codigo_palete_display}"
        
        st.text_input("Link público", value=share_url, disabled=True, key="link_publico_compacto", label_visibility="collapsed")
        
        escaped_url = share_url.replace("'", "\\'")
        components.html(
            f"""
            <button onclick="navigator.clipboard.writeText('{escaped_url}'); 
                              const msg = document.getElementById('copy-status-compacto');
                              if (msg) {{ msg.innerText='Link copiado!'; msg.style.opacity=1; setTimeout(()=>msg.style.opacity=0.2, 2000); }}">
                📋 Copiar link
            </button>
            <style>
                button {{
                    background-color: #2d8659;
                    color: white;
                    border: none;
                    padding: 6px 14px;
                    border-radius: 4px;
                    font-weight: bold;
                    cursor: pointer;
                    margin-top: 3px;
                    font-size: 12px;
                    width: 100%;
                }}
                button:hover {{
                    background-color: #1e5d3f;
                }}
            </style>
            """,
            height=45,
        )
        st.caption("Copie e compartilhe o link com clientes e parceiros.")
        st.markdown("<span id='copy-status-compacto' style='color:#2d8659; font-weight:bold; opacity:0.2; font-size:11px;'></span>", unsafe_allow_html=True)
    
    # Footer compacto
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 8px; color: #2d8659; font-size: 11px;">
            <p style="margin: 0;"><strong>🍌 Banana Rastreada na Origem</strong></p>
            <p style="margin: 2px 0 0 0;">Sistema de Rastreabilidade</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pagina_consulta_publica_landing_arquivo():
    """Página inicial (quando não há código de palete)"""
    
    # Ocultar menu e rodapé
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #2d8659 0%, #1e5d3f 100%); 
                    color: white; border-radius: 10px; margin-bottom: 25px;">
            <h1 style="margin: 0; font-size: 28px;">🍌 Rastreabilidade de Banana</h1>
            <p style="margin: 5px 0 0 0; font-size: 14px;">Origem rastreada desde o talhão</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Verificar se arquivo existe
    projeto_root = Path(__file__).parent.parent
    arquivo_json = projeto_root / "dados_rastreabilidade.json"
    arquivo_txt = projeto_root / "dados_rastreabilidade.txt"
    
    if not arquivo_json.exists() and not arquivo_txt.exists():
        st.warning("⚠️ Arquivo de dados não encontrado. Execute o script de exportação primeiro.")
        st.info("Execute: `python scripts/exportar_dados_rastreabilidade.py`")
        return
    
    # Formulário de busca
    st.markdown("### 🔍 Consultar Palete")
    st.info("💡 Escaneie o QR code na etiqueta do palete ou digite o código manualmente.")
    
    codigo_palete_input = st.text_input(
        "Código do Palete:",
        placeholder="Ex: PAL-20251111-010",
        key="busca_publica_landing",
    )
    
    codigo_palete = codigo_palete_input.strip().upper() if codigo_palete_input else ""
    
    if st.button("🔍 Consultar", type="primary", use_container_width=True, key="btn_consultar_landing"):
        if codigo_palete:
            st.query_params["palete"] = codigo_palete
            st.rerun()
        else:
            st.error("❌ Por favor, informe o código do palete.")
    
    # Informações sobre o sistema
    st.markdown("---")
    st.markdown("### ℹ️ Sobre o Sistema")
    st.markdown(
        """
        Este sistema permite rastrear a origem de cada palete de banana desde o talhão de cultivo.
        
        **O que você pode verificar:**
        - 📦 Código do palete e lote
        - 🌱 Talhão de origem
        - 📅 Data de corte
        - 🍌 Variedade da banana
        - 🗺️ Localização exata do talhão no mapa
        
        **Como usar:**
        1. Escaneie o QR code na etiqueta do palete
        2. Ou digite o código do palete no campo acima
        3. Visualize todas as informações de rastreabilidade
        """
    )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; color: #2d8659; font-size: 14px;">
            <p><strong>🍌 Banana Rastreada na Origem</strong></p>
            <p>Sistema de Rastreabilidade - Fazenda Bananas Prata Ouro</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

