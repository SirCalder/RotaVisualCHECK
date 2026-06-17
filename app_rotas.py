import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import time

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(page_title="SysPlan | Smart Route", page_icon="🧭", layout="wide", initial_sidebar_state="collapsed")

# =============================================================================
# CSS INJETADO: PALETA TECH (Azul Elétrico + Ciano + Coral)
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Fundo Gelo (Slate 50) - Deixa o azul saltar aos olhos */
    .stApp {
        background-color: #f8fafc; 
    }
    
    #MainMenu, header, footer {visibility: hidden;}
    
    .block-container {
        padding-top: 2rem !important;
        max-width: 1200px;
    }

    /* O Botão Principal - Azul Elétrico com Sombra Marinho */
    .stButton>button {
        background-color: #385aff;
        color: #ffffff;
        border-radius: 12px;
        padding: 16px 24px;
        font-weight: 700;
        font-size: 16px;
        border: none;
        width: 100%;
        transition: all 0.2s ease;
        box-shadow: 0 4px 0px #1e3a8a; 
        margin-top: 16px;
    }
    .stButton>button:hover {
        background-color: #2548e8;
        transform: translateY(2px);
        box-shadow: 0 2px 0px #1e3a8a;
        color: white;
    }

    /* Campos de Entrada */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #ffffff;
        border: 2px solid #cbd5e1;
        border-radius: 12px;
        color: #0f172a;
        font-weight: 500;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: #385aff;
        box-shadow: 0 0 0 4px rgba(56, 90, 255, 0.15); 
    }
    
    /* Títulos dos campos */
    .stTextInput label, .stSelectbox label {
        font-weight: 700;
        color: #1e293b;
        font-size: 14px;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Cartão Branco de Formulário */
    .form-card {
        background-color: #ffffff;
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.08); 
        border: 1px solid #e2e8f0;
    }

    /* Painel Azul Criativo (Esquerda) */
    .left-panel {
        background-color: #385aff;
        border-radius: 24px;
        padding: 48px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px -15px rgba(56, 90, 255, 0.4);
    }
    .left-panel h1 {
        color: #ffffff;
        font-size: 52px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 24px;
        z-index: 2;
    }
    .left-panel p {
        color: #e0e7ff;
        font-size: 18px;
        font-weight: 400;
        line-height: 1.6;
        z-index: 2;
    }
    
    /* Decorações Geométricas - A Nova Paleta Harmonizada */
    .geo-shape-1 {
        position: absolute; top: -30px; right: -30px;
        width: 180px; height: 180px;
        background-color: #00d4ff; /* Ciano Neon - Combina perfeitamente com Azul */
        border-radius: 50%; z-index: 1;
    }
    .geo-shape-2 {
        position: absolute; bottom: 30px; left: -30px;
        width: 120px; height: 120px;
        background-color: #0f172a; /* Azul Marinho Super Escuro - Dá profundidade */
        border-radius: 30px;
        transform: rotate(25deg); z-index: 1;
    }
    .geo-shape-3 {
        position: absolute; top: 40%; right: 25%;
        width: 30px; height: 30px;
        background-color: #ff6b35; /* Laranja Coral - Contraste agressivo e moderno */
        border-radius: 50%; z-index: 1;
    }
    
    /* Customização das Métricas do Streamlit */
    [data-testid="stMetricValue"] {
        font-weight: 800;
        font-size: 28px;
        color: #385aff;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        font-size: 14px;
        color: #64748b;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MÁQUINA DE ESTADOS E CONFIGURAÇÃO DA API
# =============================================================================
if 'tela_atual' not in st.session_state:
    st.session_state.tela_atual = 1

def ir_para_tela_2():
    st.session_state.tela_atual = 2

def voltar_tela_1():
    st.session_state.tela_atual = 1

API_URL = "http://137.131.134.108/alocar-aluno"
HEADERS_API = {"x-api-key": "ChallengeUDESC"}

# =============================================================================
# FUNÇÃO DE RENDERIZAÇÃO DO MAPA
# =============================================================================
def render_mapa_clean(coordinates, lat_center, lon_center, label_escola):
    coords_json = json.dumps(coordinates)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      body {{ background: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; overflow:hidden; }}
      #map {{ width:100%; height:550px; position:relative; border-radius: 24px; border: 4px solid #ffffff; box-shadow: 0 10px 30px -10px rgba(15,23,42,0.1); }}
    </style>
    </head>
    <body>
    <div id="map"></div>
    <script src="https://unpkg.com/deck.gl@latest/dist.min.js"></script>
    <script src="https://unpkg.com/maplibre-gl@3/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl@3/dist/maplibre-gl.css" rel="stylesheet">
    <script>
    const {{ DeckGL, PathLayer, TripsLayer }} = deck;
    const COORDINATES = {coords_json};
    
    const map = new maplibregl.Map({{
      container: 'map',
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [{lon_center}, {lat_center}],
      zoom: 13.5, pitch: 45, bearing: 15
    }});

    map.on('load', () => {{
      const segmentedPath = [];
      const timestamps = [];
      for(let i = 0; i < COORDINATES.length - 1; i++) {{
          segmentedPath.push({{
              path: [COORDINATES[i], COORDINATES[i+1]],
              color: [56, 90, 255, 255] // Azul Elétrico
          }});
          timestamps.push(i * 10);
      }}
      timestamps.push((COORDINATES.length - 1) * 10);
      const maxTime = timestamps[timestamps.length - 1];
      const tripData = [{{ path: COORDINATES, timestamps: timestamps }}];

      function createMarker(color, label, icon) {{
          const el = document.createElement('div');
          el.innerHTML = `
            <div style="
                background: white; 
                color: #0f172a; 
                padding: 8px 16px; 
                border-radius: 100px; 
                font-size: 13px; 
                font-weight: 700; 
                border: 3px solid rgb(${{color}}); 
                box-shadow: 0 8px 16px rgba(15,23,42,0.12);
                display: flex;
                align-items: center;
                gap: 6px;
            ">
                <span style="font-size: 16px;">${{icon}}</span> ${{label}}
            </div>`;
          return el;
      }}

      // Marcadores agora respeitam a nova paleta: Azul para casa, Coral para escola
      new maplibregl.Marker({{element: createMarker('56, 90, 255', 'Residência', '📍'), anchor: 'bottom'}})
          .setLngLat(COORDINATES[0]).addTo(map);
      new maplibregl.Marker({{element: createMarker('255, 107, 53', '{label_escola}', '🏫'), anchor: 'bottom'}})
          .setLngLat(COORDINATES[COORDINATES.length - 1]).addTo(map);

      const deckOverlay = new deck.MapboxOverlay({{ interleaved: false, layers: [] }});
      map.addControl(deckOverlay);

      let currentTime = 0;
      function animate() {{
          currentTime = (currentTime + 2) % maxTime;
          deckOverlay.setProps({{
            layers: [
              new PathLayer({{
                id: 'route-core', data: segmentedPath, getPath: d => d.path,
                getColor: d => d.color, getWidth: 8, widthUnits: 'pixels',
                capRounded: true, jointRounded: true
              }}),
              new TripsLayer({{
                id: 'route-pulse', data: tripData, getPath: d => d.path, getTimestamps: d => d.timestamps,
                getColor: [0, 212, 255, 255], // Pulso agora é Ciano Neon!
                opacity: 1, widthMinPixels: 4, trailLength: maxTime * 0.4, currentTime: currentTime,
                capRounded: true, jointRounded: true
              }})
            ]
          }});
          requestAnimationFrame(animate);
      }}
      animate();
    }});
    </script>
    </body>
    </html>
    """
    components.html(html, height=600, scrolling=False)


# =============================================================================
# TELA 1: FORMULÁRIO DE ENTRADA
# =============================================================================
if st.session_state.tela_atual == 1:
    
    col_left, col_spacer, col_right = st.columns([1.1, 0.1, 1.2])

    # --- LADO ESQUERDO ---
    with col_left:
        st.markdown("""
        <div class="left-panel">
            <div class="geo-shape-1"></div>
            <div class="geo-shape-2"></div>
            <div class="geo-shape-3"></div>
            <h1>Logística<br>Inteligente.</h1>
            <p>Otimização matemática em tempo real para a gestão educacional. Insira os dados para calcular a rota mais eficiente utilizando o motor CBC/PuLP.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- LADO DIREITO ---
    with col_right:
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h2 style="font-size: 28px; font-weight: 800; color: #0f172a; margin-bottom: 8px;">Nova Matrícula</h2>
            <p style="color: #64748b; font-size: 15px; margin-bottom: 0;">Preencha as informações para acionar o otimizador.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        nome_crianca = st.text_input("Identificação do Aluno", placeholder="Ex: Guilherme Cardoso")
        endereco = st.text_input("Logradouro (Rua, Número, Bairro)", placeholder="Ex: Rua XV de Novembro, 100")
            
        c_turma, c_turno = st.columns(2)
        with c_turma:
            turma = st.selectbox("Ano Escolar", options=[1,2,3,4,5,6,7,8,9], index=3)
        with c_turno:
            turno = st.selectbox("Turno Letivo", options=[("Matutino", 1), ("Vespertino", 2), ("Noturno", 3)], format_func=lambda x: x[0])
            
        if st.button("Executar Simulação Matemática"):
            if nome_crianca == "" or endereco == "":
                st.error("⚠️ É obrigatório preencher a Identificação e o Logradouro.")
            else:
                with st.spinner("🤖 Processando Pesquisa Operacional e Geocodificação..."):
                    try:
                        from geopy.geocoders import Nominatim
                        geolocator = Nominatim(user_agent="nexus_route_udesc")
                        
                        busca_completa = f"{endereco}, Ibirama, SC, Brasil"
                        location = geolocator.geocode(busca_completa, timeout=5)
                        
                        if location:
                            lat_final = location.latitude
                            lon_final = location.longitude
                        else:
                            st.toast("Geocodificação imprecisa. Assumindo marco zero da região.", icon="🧭")
                            lat_final = -27.057617
                            lon_final = -49.522895
                            time.sleep(1)
                            
                        st.session_state.payload = {
                            "id_aluno": nome_crianca,
                            "lat": lat_final,
                            "lon": lon_final,
                            "turma": turma,
                            "turno": turno[1]
                        }
                        ir_para_tela_2()
                        st.rerun() 
                        
                    except Exception as e:
                        st.error("Erro na API de conversão de endereços.")
                        
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TELA 2: PROCESSAMENTO E RESULTADO
# =============================================================================
elif st.session_state.tela_atual == 2:
    
    st.button("← Nova Simulação", on_click=voltar_tela_1)

    with st.spinner("Conectando ao OSRM e renderizando topologia..."):
        try:
            response = requests.post(API_URL, json=st.session_state.payload, headers=HEADERS_API, timeout=15)

            if response.status_code == 200:
                dados = response.json()
                
                # Banner de Sucesso com Azul Elétrico e Ciano
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, #385aff 0%, #00d4ff 100%); border-radius: 12px; padding: 16px 24px; margin-bottom: 24px; color: #ffffff; font-weight: 700; display: flex; align-items: center; gap: 12px; box-shadow: 0 10px 20px -5px rgba(56,90,255,0.3);">
                    <span style="font-size: 20px;">✓</span> Alocação Ótima: O aluno {dados['aluno_id']} foi direcionado com sucesso.
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="form-card" style="padding: 24px; margin-bottom: 24px;">', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Setor Demográfico", f"ZONA {dados['zona_identificada']}")
                c2.metric("Instituição Alocada", dados['escola_alocada'])
                c3.metric("Extensão da Rota", f"{dados['distancia_km']} km")
                c4.metric("Deslocamento", f"{dados['tempo_min']} min")
                st.markdown('</div>', unsafe_allow_html=True)
                
                coords = dados['rota_geojson']['coordinates']
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                lat_center = (min(lats) + max(lats)) / 2
                lon_center = (min(lons) + max(lons)) / 2

                render_mapa_clean(coords, lat_center, lon_center, dados['escola_alocada'].upper())

            else:
                st.error(f"Falha de cálculo no servidor. Código: {response.status_code}")

        except requests.exceptions.RequestException:
            st.error("Servidor Offline. Verifique a porta 80 da Oracle.")
