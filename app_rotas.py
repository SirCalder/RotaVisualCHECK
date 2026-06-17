import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import time

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(page_title="SysPlan | Registration", page_icon="📍", layout="wide", initial_sidebar_state="collapsed")

# =============================================================================
# CSS INJETADO (Adaptando Streamlit para o seu Design Tailwind)
# =============================================================================
st.markdown("""
<style>
    /* Reset do App Streamlit e cores globais */
    .stApp {
        background-color: #faf8ff;
    }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Espaçamento do topo */
    .block-container {
        padding-top: 2rem !important;
        max-width: 1280px;
    }

    /* Estilo do Botão Principal (Baseado no seu Tailwind com #385aff) */
    .stButton>button {
        background-color: #385aff;
        color: white;
        border-radius: 8px;
        padding: 14px 24px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 16px;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(56, 90, 255, 0.2);
    }
    .stButton>button:hover {
        background-color: #2b46cc;
        transform: translateY(-1px);
        box-shadow: 0 6px 12px rgba(56, 90, 255, 0.3);
        color: white;
    }

    /* Estilo dos Inputs (Texto e Select) */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #ffffff;
        border: 2px solid #e2e1ed;
        border-radius: 8px;
        color: #1a1b23;
        font-family: 'Inter', sans-serif;
        padding: 8px 12px;
        transition: border-color 0.2s ease;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: #385aff;
        box-shadow: 0 0 0 2px rgba(56, 90, 255, 0.2);
    }
    
    /* Títulos dos campos (Labels) */
    .stTextInput label, .stSelectbox label {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1a1b23;
        font-size: 14px;
        margin-bottom: 4px;
    }

    /* O Card Branco do Formulário (Direita) */
    .wizard-card {
        background-color: #ffffff;
        border: 2px solid #e2e1ed;
        border-radius: 12px;
        padding: 32px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* Painel Azul do GovTech (Esquerda) */
    .left-panel {
        background-color: #385aff;
        border-radius: 16px;
        padding: 48px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    .left-panel h1 {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        font-size: 48px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 24px;
        z-index: 2;
    }
    .left-panel p {
        color: rgba(255, 255, 255, 0.9);
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        line-height: 1.6;
        z-index: 2;
    }
    /* Elemento decorativo de fundo do painel azul */
    .bg-shape {
        position: absolute;
        top: -10%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        z-index: 1;
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
# FUNÇÃO DE RENDERIZAÇÃO DO MAPA (Adequado para a cor #385aff)
# =============================================================================
def render_mapa_clean(coordinates, lat_center, lon_center, label_escola):
    coords_json = json.dumps(coordinates)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      body {{ background: #faf8ff; font-family: 'Inter', sans-serif; overflow:hidden; }}
      #map {{ width:100%; height:550px; position:relative; border-radius: 12px; border: 2px solid #e2e1ed; }}
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
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json', // Mapa claro
      center: [{lon_center}, {lat_center}],
      zoom: 13.5, pitch: 45, bearing: 15
    }});

    map.on('load', () => {{
      const segmentedPath = [];
      const timestamps = [];
      for(let i = 0; i < COORDINATES.length - 1; i++) {{
          segmentedPath.push({{
              path: [COORDINATES[i], COORDINATES[i+1]],
              color: [56, 90, 255, 255] // A sua cor #385aff em RGB
          }});
          timestamps.push(i * 10);
      }}
      timestamps.push((COORDINATES.length - 1) * 10);
      const maxTime = timestamps[timestamps.length - 1];
      const tripData = [{{ path: COORDINATES, timestamps: timestamps }}];

      function createSimpleMarker(color, label) {{
          const el = document.createElement('div');
          el.innerHTML = `<div style="background: white; color: #1a1b23; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: bold; border: 2px solid rgb(${{color}}); box-shadow: 0 2px 4px rgba(0,0,0,0.1);">📍 ${{label}}</div>`;
          return el;
      }}

      new maplibregl.Marker({{element: createSimpleMarker('56, 90, 255', 'RESIDÊNCIA'), anchor: 'bottom'}})
          .setLngLat(COORDINATES[0]).addTo(map);
      new maplibregl.Marker({{element: createSimpleMarker('253, 118, 26', '{label_escola}'), anchor: 'bottom'}})
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
                getColor: d => d.color, getWidth: 8, widthUnits: 'pixels'
              }}),
              new TripsLayer({{
                id: 'route-pulse', data: tripData, getPath: d => d.path, getTimestamps: d => d.timestamps,
                getColor: [255, 255, 255, 255], opacity: 1, widthMinPixels: 4, trailLength: maxTime * 0.4, currentTime: currentTime
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
    components.html(html, height=570, scrolling=False)


# =============================================================================
# TELA 1: FORMULÁRIO DE ENTRADA (O seu Split Screen Design)
# =============================================================================
if st.session_state.tela_atual == 1:
    
    col_left, col_right = st.columns([1, 1.2], gap="large")

    # --- LADO ESQUERDO (Apresentação GovTech) ---
    with col_left:
        st.markdown("""
        <div class="left-panel">
            <div class="bg-shape"></div>
            <h1>Bem-vindo ao SysPlan.</h1>
            <p>Registre os detalhes da residência de forma rápida e segura. Nosso sistema matemático avalia as vagas e traça a rota escolar automaticamente.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- LADO DIREITO (Wizard Form) ---
    with col_right:
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <div style="width: 100%; background-color: #e8e7f3; height: 8px; border-radius: 99px; margin-bottom: 24px;">
                <div style="background-color: #385aff; height: 100%; width: 33%; border-radius: 99px;"></div>
            </div>
            <h2 style="font-family: 'Inter', sans-serif; font-size: 28px; font-weight: 700; color: #1a1b23; margin-bottom: 4px;">Detalhes do Aluno</h2>
            <p style="font-family: 'Inter', sans-serif; color: #434655; font-size: 15px; margin-bottom: 0;">Forneça as informações abaixo. Nosso motor fará o cruzamento com o zoneamento.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Container com borda para o formulário
        with st.container():
            st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
            
            nome_crianca = st.text_input("Nome Completo da Criança", placeholder="Ex: Maria Clara Silva")
            endereco = st.text_input("Endereço Residencial", placeholder="Rua, Número, Bairro - Ibirama")
                
            c_turma, c_turno = st.columns(2)
            with c_turma:
                turma = st.selectbox("Ano Escolar", options=[1,2,3,4,5,6,7,8,9], index=3)
            with c_turno:
                turno = st.selectbox("Turno Desejado", options=[("Matutino", 1), ("Vespertino", 2), ("Noturno", 3)], format_func=lambda x: x[0])
                
            st.write("")
            
            # Botão de Busca
            if st.button("Continuar e Traçar Rota"):
                if nome_crianca == "" or endereco == "":
                    st.error("Por favor, preencha o nome e o endereço da criança.")
                else:
                    with st.spinner("Sincronizando com motor de alocação..."):
                        try:
                            # Geocoding invisível
                            from geopy.geocoders import Nominatim
                            geolocator = Nominatim(user_agent="nexus_route_udesc")
                            
                            busca_completa = f"{endereco}, Ibirama, SC, Brasil"
                            location = geolocator.geocode(busca_completa, timeout=5)
                            
                            if location:
                                lat_final = location.latitude
                                lon_final = location.longitude
                            else:
                                st.toast("Endereço exato não encontrado. Utilizando referência central.", icon="⚠️")
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
                            st.error("Erro no servidor de mapas global.")
                            
            st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# TELA 2: PROCESSAMENTO E RESULTADO (O Mapa e as Métricas)
# =============================================================================
elif st.session_state.tela_atual == 2:
    
    st.button("← Voltar para Nova Busca", on_click=voltar_tela_1)
    st.divider()

    with st.spinner("Calculando a melhor rota via modelo PuLP..."):
        try:
            response = requests.post(API_URL, json=st.session_state.payload, headers=HEADERS_API, timeout=15)

            if response.status_code == 200:
                dados = response.json()
                
                st.success(f"✅ **Processo Concluído:** {dados['aluno_id']} foi direcionado(a) com base no zoneamento matemático.")
                
                # Métricas
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Região Demográfica", f"Zona {dados['zona_identificada']}")
                c2.metric("Instituição Recomendada", dados['escola_alocada'])
                c3.metric("Extensão da Rota", f"{dados['distancia_km']} km")
                c4.metric("Deslocamento", f"{dados['tempo_min']} min")
                
                # Renderiza o mapa Deck.gl
                coords = dados['rota_geojson']['coordinates']
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                lat_center = (min(lats) + max(lats)) / 2
                lon_center = (min(lons) + max(lons)) / 2

                render_mapa_clean(coords, lat_center, lon_center, dados['escola_alocada'].upper())

            else:
                st.error(f"O modelo matemático retornou um erro. Código: {response.status_code}")

        except requests.exceptions.RequestException:
            st.error("Servidor OSRM / FastAPI offline.")
