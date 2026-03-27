import streamlit as st
import google.generativeai as genai
import time
import re

# ─── CONFIGURAÇÃO DA API ──────────────────────────────────────────────────────
genai.configure(api_key=st.secrets["general"]["api_key"])
model = genai.GenerativeModel("gemini-3-flash-preview")

# ─── CONFIGURAÇÃO DA PÁGINA ───────────────────────────────────────────────────
st.set_page_config(
    page_title="CineIA",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS GLOBAL ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

    /* ── Reset & Base ───────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0c0c0f !important;
    }
    [data-testid="stAppViewContainer"] > .main {
        background-color: #0c0c0f;
    }
    [data-testid="block-container"] {
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    * { font-family: 'DM Sans', sans-serif; color: #e8e0d0; }

    /* ── Sidebar ────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #16151a 0%, #1a1219 100%) !important;
        border-right: 1px solid #2a2030;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 3px;
        color: #f5c842;
        font-size: 1.4rem;
    }

    /* Slider */
    [data-testid="stSlider"] > div > div > div {
        background: #f5c842 !important;
    }

    /* Multiselect tags */
    span[data-baseweb="tag"] {
        background-color: #f5c842 !important;
        border: none !important;
        border-radius: 4px !important;
    }
    span[data-baseweb="tag"] span { color: #0c0c0f !important; font-weight: 600; }

    /* Inputs */
    textarea, input[type="text"] {
        background: #1e1c24 !important;
        border: 1px solid #2e2b38 !important;
        border-radius: 8px !important;
        color: #e8e0d0 !important;
    }
    textarea:focus, input:focus {
        border-color: #f5c842 !important;
        box-shadow: 0 0 0 2px rgba(245,200,66,0.15) !important;
    }

    /* ── Botão principal ────────────────────────────── */
    [data-testid="stButton"] > button {
        background: linear-gradient(135deg, #f5c842, #e8a020) !important;
        color: #0c0c0f !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: 1.1rem !important;
        letter-spacing: 2px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        width: 100% !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 20px rgba(245,200,66,0.25) !important;
    }
    [data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(245,200,66,0.4) !important;
    }

    /* ── Header hero ────────────────────────────────── */
    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(245,200,66,0.12), transparent);
        border-bottom: 1px solid #1f1d27;
        margin-bottom: 2rem;
    }
    .hero-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 5rem;
        letter-spacing: 8px;
        line-height: 1;
        background: linear-gradient(135deg, #f5c842 30%, #ff9b42 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
        margin: 0;
    }
    .hero-sub {
        font-size: 1rem;
        color: #7a7288;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 0.5rem;
        font-weight: 300;
    }

    /* ── Popcorn Loader ─────────────────────────────── */
    @keyframes jump {
        0%, 100% { transform: translateY(0) scale(1); }
        40%       { transform: translateY(-28px) scale(1.15); }
        60%       { transform: translateY(-18px) scale(1.05); }
    }
    @keyframes shadow-pulse {
        0%, 100% { transform: scaleX(1); opacity: 0.5; }
        40%       { transform: scaleX(0.5); opacity: 0.2; }
    }
    @keyframes grain {
        0%, 100% { background-position: 0 0; }
        50%       { background-position: 100px 50px; }
    }
    @keyframes fade-in-msg {
        from { opacity: 0; transform: translateY(6px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .loader-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3.5rem 1rem;
    }
    .popcorn-stage {
        position: relative;
        width: 80px;
        height: 90px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
    }
    .popcorn-emoji {
        font-size: 3.8rem;
        display: inline-block;
        animation: jump 0.85s cubic-bezier(0.36, 0.07, 0.19, 0.97) infinite;
        filter: drop-shadow(0 0 12px rgba(245,200,66,0.6));
    }
    .popcorn-shadow {
        position: absolute;
        bottom: -6px;
        width: 44px;
        height: 10px;
        background: rgba(245,200,66,0.2);
        border-radius: 50%;
        animation: shadow-pulse 0.85s cubic-bezier(0.36, 0.07, 0.19, 0.97) infinite;
    }
    .loader-text {
        margin-top: 1.6rem;
        font-size: 0.85rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #7a7288;
        animation: fade-in-msg 0.5s ease both;
    }
    .loader-dots span {
        display: inline-block;
        animation: jump 1s ease infinite;
    }
    .loader-dots span:nth-child(2) { animation-delay: 0.15s; }
    .loader-dots span:nth-child(3) { animation-delay: 0.30s; }

    /* ── Cards de filme ─────────────────────────────── */
    .results-header {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2rem;
        letter-spacing: 5px;
        color: #f5c842;
        margin-bottom: 1.4rem;
        text-align: center;
    }
    .movie-card {
        background: linear-gradient(135deg, #1a1820 0%, #15131c 100%);
        border: 1px solid #2a2538;
        border-radius: 14px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.25s ease, transform 0.25s ease;
    }
    .movie-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #f5c842, #ff9b42);
        border-radius: 14px 14px 0 0;
    }
    .movie-card:hover {
        border-color: #f5c842;
        transform: translateY(-3px);
    }
    .movie-number {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 3.5rem;
        line-height: 1;
        color: #2a2538;
        position: absolute;
        right: 1.2rem;
        top: 0.8rem;
        letter-spacing: 2px;
    }
    .movie-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.6rem;
        letter-spacing: 2px;
        color: #ffffff;
        margin: 0 0 0.2rem;
        padding-right: 3rem;
    }
    .movie-year {
        display: inline-block;
        background: rgba(245,200,66,0.12);
        color: #f5c842;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 2px;
        padding: 2px 10px;
        border-radius: 20px;
        margin-bottom: 0.8rem;
    }
    .movie-reason {
        color: #9e97b0;
        font-size: 0.95rem;
        line-height: 1.6;
        border-left: 2px solid #f5c842;
        padding-left: 0.9rem;
        margin-top: 0.6rem;
    }

    /* ── Feedback ───────────────────────────────────── */
    .feedback-bar {
        display: flex;
        align-items: center;
        gap: 1rem;
        background: #161420;
        border: 1px solid #2a2538;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-top: 1.5rem;
    }
    .feedback-label {
        font-size: 0.85rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #7a7288;
        flex: 1;
    }

    /* Feedback buttons override */
    .feedback-col [data-testid="stButton"] > button {
        background: #1e1c28 !important;
        color: #e8e0d0 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.95rem !important;
        letter-spacing: 1px !important;
        border: 1px solid #2a2538 !important;
        box-shadow: none !important;
        padding: 0.5rem 1rem !important;
    }
    .feedback-col [data-testid="stButton"] > button:hover {
        border-color: #f5c842 !important;
        color: #f5c842 !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* ── Alert overrides ────────────────────────────── */
    [data-testid="stAlert"] {
        background: #1a1620 !important;
        border: 1px solid #2e2840 !important;
        border-radius: 10px !important;
    }

    /* ── Divider ────────────────────────────────────── */
    hr { border-color: #1f1d27 !important; }

    /* ── Caption ────────────────────────────────────── */
    [data-testid="stCaptionContainer"] p {
        color: #3a3548 !important;
        text-align: center;
        font-size: 0.78rem;
        letter-spacing: 1px;
    }

    /* ── Hide Streamlit chrome ──────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── HERO HEADER ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <p class="hero-title">🍿 CineIA</p>
        <p class="hero-sub">Seu próximo filme está a um clique</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Preferências")
    st.markdown("---")

    generos_opcoes = ["Ação", "Drama", "Sci-Fi", "Comédia", "Terror",
                      "Documentário", "Suspense", "Romance", "Animação", "Faroeste"]
    genero = st.multiselect(
        "🎬 Gêneros favoritos",
        generos_opcoes,
        placeholder="Escolha um ou mais..."
    )

    tempo = st.slider("⏱ Duração máxima (minutos)", 60, 240, 120, step=10)

    idioma = st.selectbox(
        "🌍 Idioma de preferência",
        ["Qualquer", "Inglês", "Português", "Espanhol", "Francês", "Japonês"]
    )

    decada = st.select_slider(
        "📅 Época do filme",
        options=["Qualquer", "Clássico (antes de 1980)", "Anos 80/90", "Anos 2000/10", "Recente (2020+)"],
        value="Qualquer"
    )

    st.markdown("---")
    mood = st.text_area(
        "💭 Como você está se sentindo?",
        placeholder="Ex: Quero algo que me faça pensar, com reviravoltas inesperadas e uma trilha sonora marcante.",
        height=120,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    botao_recomendar = st.button("🎬 Buscar Recomendações", use_container_width=True)

# ─── FUNÇÃO: PARSEAR FILMES ────────────────────────────────────────────────────
def parse_filmes(texto: str):
    """
    Tenta extrair blocos de filmes do texto retornado pela IA.
    Retorna lista de dicts {titulo, ano, motivo} ou None se não parsear.
    """
    filmes = []
    # Divide por numeração (1., 2., 3. ou **1., etc.)
    blocos = re.split(r'\n(?=\*{0,2}\d+[\.\)])', texto.strip())
    for bloco in blocos:
        bloco = bloco.strip()
        if not bloco:
            continue
        # Título (linha que pode ter **Título (Ano)** ou Título - Ano)
        titulo_match = re.search(
            r'(?:\*{1,2})?(?:\d+[\.\)]\s*)?(?:\*{1,2})?\*{0,2}([^\n\(\*]+?)(?:\s*[\(\-–]\s*(\d{4})\s*[\)\-–]?)?\*{0,2}\n',
            bloco + "\n"
        )
        ano_match = re.search(r'[\(\-–]\s*(\d{4})\s*[\)\-–]', bloco)
        # Motivo: linha após traço ou "motivo:"
        motivo_match = re.search(
            r'(?:motivo|why|porque|por que|combina|por ser|pois)[:\s\-–]+(.+)',
            bloco, re.IGNORECASE
        )
        if not motivo_match:
            linhas = [l.strip() for l in bloco.split('\n') if l.strip()]
            motivo_texto = linhas[-1] if len(linhas) > 1 else bloco
            motivo_texto = re.sub(r'[\*_`#]', '', motivo_texto).strip()
        else:
            motivo_texto = re.sub(r'[\*_`#]', '', motivo_match.group(1)).strip()

        titulo_texto = "Filme"
        if titulo_match:
            titulo_texto = re.sub(r'[\*_`#\d\.\)]', '', titulo_match.group(1)).strip()
        else:
            primeira_linha = bloco.split('\n')[0]
            titulo_texto = re.sub(r'[\*_`#\d\.\)\(\-–\d]', '', primeira_linha).strip()

        ano_texto = ano_match.group(1) if ano_match else "—"

        if titulo_texto and len(titulo_texto) > 1:
            filmes.append({"titulo": titulo_texto, "ano": ano_texto, "motivo": motivo_texto})

    return filmes if len(filmes) >= 2 else None


def render_card(i, titulo, ano, motivo):
    return f"""
    <div class="movie-card">
        <span class="movie-number">0{i}</span>
        <p class="movie-title">{titulo}</p>
        <span class="movie-year">✦ {ano}</span>
        <p class="movie-reason">{motivo}</p>
    </div>
    """


# ─── LÓGICA PRINCIPAL ─────────────────────────────────────────────────────────
if botao_recomendar:
    if not mood.strip():
        st.warning("✦ Descreva como você está se sentindo para receber sugestões personalizadas.")
    else:
        # Animação de loading customizada
        loader_placeholder = st.empty()
        loader_placeholder.markdown(
            """
            <div class="loader-wrapper">
                <div class="popcorn-stage">
                    <span class="popcorn-emoji">🍿</span>
                    <div class="popcorn-shadow"></div>
                </div>
                <p class="loader-text">Consultando o catálogo cinematográfico
                    <span class="loader-dots">
                        <span>.</span><span>.</span><span>.</span>
                    </span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        generos_str = ", ".join(genero) if genero else "qualquer gênero"
        idioma_str = "" if idioma == "Qualquer" else f" Prefira filmes em {idioma}."
        decada_str = "" if decada == "Qualquer" else f" Época preferida: {decada}."

        prompt = f"""
        Você é um cinéfilo apaixonado e especialista em cinema mundial.

        Recomende exatamente 3 filmes para alguém com as seguintes preferências:
        - Gêneros: {generos_str}
        - Duração máxima: {tempo} minutos{idioma_str}{decada_str}
        - Humor/desejo: "{mood}"

        Para CADA filme, siga este formato exato (sem markdown extra):

        1. Título do Filme (Ano)
        Motivo: Uma frase curta e envolvente explicando por que esse filme combina perfeitamente com o pedido.

        2. Título do Filme (Ano)
        Motivo: Uma frase curta e envolvente explicando por que esse filme combina perfeitamente com o pedido.

        3. Título do Filme (Ano)
        Motivo: Uma frase curta e envolvente explicando por que esse filme combina perfeitamente com o pedido.

        Seja criativo e vá além do óbvio. Considere filmes menos conhecidos se fizerem mais sentido.
        """

        try:
            response = model.generate_content(prompt)
            loader_placeholder.empty()

            st.markdown('<p class="results-header">✦ Sugestões para Você</p>', unsafe_allow_html=True)

            filmes = parse_filmes(response.text)

            if filmes:
                for i, f in enumerate(filmes, 1):
                    st.markdown(render_card(i, f["titulo"], f["ano"], f["motivo"]), unsafe_allow_html=True)
            else:
                # Fallback: exibe o texto original formatado
                st.markdown(
                    f'<div class="movie-card"><p style="line-height:1.8;">{response.text}</p></div>',
                    unsafe_allow_html=True,
                )

            # ── Feedback ──────────────────────────────────────────────────────
            st.markdown(
                '<div class="feedback-label" style="margin-top:2rem; letter-spacing:3px; '
                'text-transform:uppercase; font-size:0.8rem; color:#7a7288;">As sugestões foram úteis?</div>',
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns([1, 1, 4])

            with col1:
                st.markdown('<div class="feedback-col">', unsafe_allow_html=True)
                if st.button("👍  Gostei", key="like"):
                    with open("feedback.csv", "a") as f:
                        f.write(f'"{mood}","{genero}",{tempo},Gostei\n')
                    st.success("Obrigado! 🎬")
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="feedback-col">', unsafe_allow_html=True)
                if st.button("👎  Não curti", key="dislike"):
                    with open("feedback.csv", "a") as f:
                        f.write(f'"{mood}","{genero}",{tempo},Não gostei\n')
                    st.info("Registrado! Vamos melhorar 🙏")
                st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            loader_placeholder.empty()
            st.error(f"⚠️ Erro ao conectar com a IA: {e}")

else:
    # Estado inicial — dica central
    st.markdown(
        """
        <div style="text-align:center; padding: 4rem 2rem; color:#3a3548;">
            <p style="font-size:3.5rem; margin-bottom:1rem;">🎞</p>
            <p style="font-family:'Bebas Neue',sans-serif; font-size:1.3rem; letter-spacing:4px; color:#2e2b3a;">
                PREENCHA SUAS PREFERÊNCIAS AO LADO
            </p>
            <p style="font-size:0.85rem; color:#2a2538; letter-spacing:1px;">
                e descubra o filme perfeito para o seu momento
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─── RODAPÉ ───────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Desenvolvido na disciplina de IHC · Graduação em IA e Ciência de Dados · Universidade Franciscana (UFN)")
