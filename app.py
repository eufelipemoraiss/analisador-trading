import streamlit as st
from PIL import Image
from google import genai

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Analisador de Gráficos - Trading",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS customizado (tema escuro estilo trading)
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #fafafa; }
    .stButton>button { 
        background-color: #00c853; 
        color: white; 
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        width: 100%;
    }
    .stButton>button:hover { background-color: #00b248; }
    .result-box { 
        background-color: #1e1e1e; 
        border-left: 4px solid #00c853;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .direcao-call { color: #00c853; font-size: 1.5rem; font-weight: bold; }
    .direcao-put { color: #ff5252; font-size: 1.5rem; font-weight: bold; }
    .direcao-neutro { color: #ffd740; font-size: 1.5rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# API KEY (Cada usuário usa a sua própria)
# ============================================================
api_key = None

# ============================================================
# BARRA LATERAL
# ============================================================
with st.sidebar:
    st.title("⚙️ Configurações")
    
    api_key = st.text_input(
        "🔑 Google Gemini API Key", 
        type="password",
        help="Obtenha gratuitamente em: aistudio.google.com/app/apikey"
    )
    
    if api_key:
        st.success("🔐 API Key configurada")
    else:
        st.warning("⚠️ Insira sua API Key acima")
    
    st.divider()
    st.markdown("""
    ### 📚 Como usar
    1. Tire um print do gráfico na Stockity
    2. Faça upload da imagem aqui
    3. Preencha o ativo e tempo
    4. Clique em **Analisar**
    
    ### ⚠️ Aviso de Risco
    Esta ferramenta é **apenas para estudo**. 
    O mercado, principalmente em índices sintéticos e opções binárias, envolve alto risco de perda. Nenhuma IA garante resultados.
    """)
    
    st.divider()
    st.caption("Desenvolvido para análise técnica educacional")
    st.caption("Cada usuário utiliza sua própria API Key")

# ============================================================
# TÍTULO PRINCIPAL
# ============================================================
st.title("📊 Analisador Técnico de Gráficos")
st.caption("IA especializada em leitura de price action e indicadores visuais")

# ============================================================
# UPLOAD E CONTEXTO
# ============================================================
col1, col2 = st.columns([1, 1])

with col1:
    ativo = st.selectbox(
        "📈 Ativo",
        ["Crypto IDX", "EUR/USD", "GBP/USD", "USD/JPY", "BTC/USD", "ETH/USD", "Outro"]
    )
    
with col2:
    timeframe = st.selectbox(
        "⏱️ Timeframe",
        ["1 minuto (M1)", "5 minutos (M5)", "15 minutos (M15)", "1 hora (H1)", "Diário (D1)"]
    )

estrategia = st.selectbox(
    "🧠 Foco da Análise",
    ["Automático (geral)", "Price Action / Candlesticks", "Suporte e Resistência", "RSI + MACD", "Bandas de Bollinger", "Tendência + Médias Móveis"]
)

uploaded_file = st.file_uploader(
    "📤 Envie o print do gráfico (PNG, JPG, JPEG)", 
    type=["png", "jpg", "jpeg"]
)

# ============================================================
# FUNÇÃO DE ANÁLISE COM LISTAGEM DINÂMICA DE MODELOS
# ============================================================
def analisar_grafico(image, ativo, timeframe, estrategia, api_key):
    client = genai.Client(api_key=api_key)
    
    prompt = f"""Você é um analista técnico profissional com 15 anos de experiência em day trade, swing trade e opções binárias. 
    
Analise a imagem do gráfico de trading enviada. O ativo é **{ativo}**, no timeframe **{timeframe}**. O usuário quer foco em: **{estrategia}**.

Instruções rigorosas:
1. Identifique a tendência predominante (ALTA, BAIXA ou LATERAL)
2. Localize suportes e resistências visíveis
3. Identifique padrões de candlestick (martelo, engolfo, doji, estrela, etc.)
4. Se houver indicadores na imagem (RSI, MACD, BB, etc.), interprete-os
5. Avalie volume se visível
6. Dê uma direção clara para o PRÓXIMO MOVIMENTO IMEDIATO

Responda EXATAMENTE neste formato (em português):

**Direção Sugerida:** CALL (Alta) ou PUT (Baixa) ou NEUTRO/AGUARDAR
**Confiança:** Apenas um número entre 50% e 98%
**Análise Técnica:** Parágrafo com a leitura do gráfico
**Pontos de Entrada:** Onde seria ideal entrar (preço ou região)
**Alvo/Resistência:** Próximo alvo se mover a favor
**Suporte Chave:** Onde colocar proteção/stop
**Razão para não entrar:** Se houver sinal de alerta ou contra-indicação
**Observação Final:** Lembrete sobre gestão de risco

Seja direto, técnico e objetivo. Não use linguagem duvidosa do tipo "pode subir ou descer". Escolha um lado com base na técnica.
"""
    
    # 1º - Tenta descobrir os modelos disponíveis na conta dinamicamente
    modelos_para_tentar = []
    try:
        for m in client.models.list():
            nome = m.name  # vem como "models/gemini-..." ou "gemini-..."
            nome_limpo = nome.replace("models/", "").strip()
            if "gemini" in nome_limpo.lower():
                modelos_para_tentar.append(nome_limpo)
    except Exception:
        pass
    
    # 2º - Se não conseguiu listar, usa fallback manual expandido
    if not modelos_para_tentar:
        modelos_para_tentar = [
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash-001",
            "gemini-1.5-flash-8b",
            "gemini-1.5-flash-8b-latest",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
            "gemini-1.5-pro-001",
            "gemini-2.0-flash",
            "gemini-2.0-flash-latest",
            "gemini-2.0-flash-lite",
            "gemini-3.8-flash",
            "gemini-3.8-flash-latest",
            "gemini-3.8-flash-001"
        ]
    
    ultimo_erro = ""
    
    for modelo in modelos_para_tentar:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=[prompt, image]
            )
            return response.text
        except Exception as e:
            ultimo_erro = str(e)
            erro_lower = ultimo_erro.lower()
            # Se for indisponível ou não encontrado, tenta o próximo
            if any(x in erro_lower for x in ["503", "404", "not_found", "unavailable", "high demand", "is not found"]):
                continue
            # Se for erro de API key, quota ou formato, para imediatamente
            break
    
    # Se chegou aqui, todos falharam
    if "503" in ultimo_erro or "unavailable" in ultimo_erro.lower() or "high demand" in ultimo_erro.lower():
        raise Exception(
            "O Google Gemini está temporariamente sobrecarregado (erro 503) para todos os modelos disponíveis. "
            "Isso é um problema do lado da Google. Aguarde alguns minutos e tente novamente. "
            "Se persistir por horas, tente gerar uma nova API Key em outro projeto do Google Cloud."
        )
    else:
        raise Exception(f"Todos os modelos falharam. Último erro: {ultimo_erro}")

# ============================================================
# BOTÃO DE ANÁLISE
# ============================================================
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Gráfico carregado", use_container_width=True)
    
    if st.button("🚀 ANALISAR GRÁFICO"):
        if not api_key:
            st.error("❌ API Key não configurada!")
            st.info("👉 Insira sua API Key na barra lateral.")
        else:
            with st.spinner("🔍 Analisando padrões, suportes, resistências e indicadores... Aguarde."):
                try:
                    resultado = analisar_grafico(image, ativo, timeframe, estrategia, api_key)
                    
                    st.success("✅ Análise concluída!")
                    
                    with st.container():
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        
                        resultado_upper = resultado.upper()
                        idx_call = resultado_upper.find("CALL")
                        idx_put = resultado_upper.find("PUT")
                        
                        if idx_call != -1 and (idx_put == -1 or idx_call < idx_put):
                            st.markdown('<p class="direcao-call">📈 SINAL DE ALTA (CALL)</p>', unsafe_allow_html=True)
                        elif idx_put != -1:
                            st.markdown('<p class="direcao-put">📉 SINAL DE BAIXA (PUT)</p>', unsafe_allow_html=True)
                        else:
                            st.markdown('<p class="direcao-neutro">⚖️ NEUTRO / AGUARDAR</p>', unsafe_allow_html=True)
                        
                        st.markdown("---")
                        st.markdown(resultado)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Erro na análise: {str(e)}")
                    if "503" in str(e):
                        st.info("💡 A Google está com alta demanda no momento. Espere 2-5 minutos e clique em Analisar novamente.")
                    else:
                        st.info("Dica: Verifique se sua API Key está ativa e se o arquivo de imagem não está corrompido.")
