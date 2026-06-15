import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import time

# =============================================================================
# CONFIGURAÇÃO E CSS CUSTOMIZADO
# =============================================================================
st.set_page_config(page_title="EduRoute | SysPlan", page_icon="🫪", layout="wide", initial_sidebar_state="collapsed")

# Injetando um pouco do seu estilo escuro moderno e escondendo elementos nativos
st.markdown("""
<style>
    /* Esconde o menu do Streamlit e o header padrão */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Customização para dar a cara do seu Tailwind */
    .stButton>button {
        background-color: #00a3ff;
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0082cc;
        border-color: #0082cc;
    }
    
    .card-decorativo {
        background: linear-gradient(145deg, #1d2023, #111417);
        border: 1px solid #3f4852;
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MÁQUINA DE ESTADOS (Navegação de Telas)
# =============================================================================
# O sistema inicia na Tela 1. Se não existir o estado, criamos agora.
if 'tela_atual' not in st.session_state:
    st.session_state.tela_atual = 1

def ir_para_tela_2():
    st.session_state.tela_atual = 2

def voltar_tela_1():
    st.session_state.tela_atual = 1

# Configurações do Backend (Servidor 2)
API_URL = "http://137.131.134.108/alocar-aluno"
HEADERS_API = {"x-api-key": "ChallengeUDESC"}

# =============================================================================
# FUNÇÃO DE RENDERIZAÇÃO DO MAPA (Deck.gl mantido intacto)
# =============================================================================
def render_mapa_clean(coordinates, lat_center, lon_center, label_escola):
    coords_json = json.dumps(coordinates)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      body {{ background: #111417; font-family: system-ui, sans-serif; overflow:hidden; }}
      #map {{ width:100%; height:550px; position:relative; border-radius: 12px; border: 1px solid #3f4852; }}
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
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [{lon_center}, {lat_center}],
      zoom: 13.5, pitch: 50, bearing: 20
    }});

    map.on('load', () => {{
      const segmentedPath = [];
      const timestamps = [];
      for(let i = 0; i < COORDINATES.length - 1; i++) {{
          segmentedPath.push({{
              path: [COORDINATES[i], COORDINATES[i+1]],
              color: [0, 163, 255, 255] // Cor primária do seu Tailwind
          }});
          timestamps.push(i * 10);
      }}
      timestamps.push((COORDINATES.length - 1) * 10);
      const maxTime = timestamps[timestamps.length - 1];
      const tripData = [{{ path: COORDINATES, timestamps: timestamps }}];

      function createSimpleMarker(color, label) {{
          const el = document.createElement('div');
          el.innerHTML = `<div style="background: rgba(20,20,20,0.9); color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: bold; border: 2px solid rgb(${{color}});"> ${{label}}</div>`;
          return el;
      }}

      new maplibregl.Marker({{element: createSimpleMarker('0, 255, 128', 'RESIDÊNCIA'), anchor: 'bottom'}})
          .setLngLat(COORDINATES[0]).addTo(map);
      new maplibregl.Marker({{element: createSimpleMarker('255, 215, 0', '{label_escola}'), anchor: 'bottom'}})
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
                getColor: d => d.color, getWidth: 6, widthUnits: 'pixels'
              }}),
              new TripsLayer({{
                id: 'route-pulse', data: tripData, getPath: d => d.path, getTimestamps: d => d.timestamps,
                getColor: [255, 255, 255, 255], opacity: 1, widthMinPixels: 6, trailLength: maxTime * 0.3, currentTime: currentTime
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
# TELA 1: FORMULÁRIO DE ENTRADA (O seu visual 60/40)
# =============================================================================
if st.session_state.tela_atual == 1:
    
    # Topbar minimalista
    st.markdown("### 🏢 SysPlan | GovTech Initiative")
    st.divider()

    col_form, col_img = st.columns([1.2, 0.8], gap="large")

    with col_form:
        st.title("Vamos encontrar a escola mais próxima?")
        st.markdown("Preencha os dados abaixo para descobrirmos as melhores opções de ensino e rotas de transporte escolar na sua região.")
        st.write("")
        
        # UX Limpa: Apenas Nome e Endereço em texto
        nome_crianca = st.text_input("Nome da Criança", placeholder="Ex: Maria Clara")
        endereco = st.text_input("Endereço Completo", placeholder="Ex: Rua XV de Novembro, 100")
            
        c_turma, c_turno = st.columns(2)
        with c_turma:
            turma = st.selectbox("Ano Escolar", options=[1,2,3,4,5,6,7,8,9], index=3)
        with c_turno:
            turno = st.selectbox("Turno Desejado", options=[("Matutino", 1), ("Vespertino", 2), ("Noturno", 3)], format_func=lambda x: x[0])
            
        transporte = st.checkbox("Precisa de transporte escolar integrado?", value=True)
        
        st.write("")
        if st.button("🔍 Buscar Vagas e Rotas Autônomas", use_container_width=True):
            if nome_crianca == "" or endereco == "":
                st.warning("Por favor, preencha o nome e o endereço da criança.")
            else:
                with st.spinner("📍 Convertendo endereço em coordenadas..."):
                    try:
                        # Importa o motor de geocoding
                        from geopy.geocoders import Nominatim
                        geolocator = Nominatim(user_agent="nexus_route_udesc")
                        
                        # Adiciona a cidade e estado automaticamente para forçar a precisão da busca
                        busca_completa = f"{endereco}, Ibirama, SC, Brasil"
                        location = geolocator.geocode(busca_completa, timeout=5)
                        
                        if location:
                            lat_final = location.latitude
                            lon_final = location.longitude
                        else:
                            # Fallback (Plano B): Se o usuário digitar algo muito louco e o mapa não achar,
                            # jogamos uma coordenada padrão do centro para o MVP não quebrar na apresentação.
                            st.toast("Endereço exato não encontrado. Utilizando região central como referência.", icon="⚠️")
                            lat_final = -27.057617
                            lon_final = -49.522895
                            time.sleep(2)
                            
                        # Salva os dados processados invisivelmente na memória
                        st.session_state.payload = {
                            "id_aluno": nome_crianca,
                            "lat": lat_final,
                            "lon": lon_final,
                            "turma": turma,
                            "turno": turno[1]
                        }
                        ir_para_tela_2()
                        st.rerun() # Força a transição de tela
                        
                    except Exception as e:
                        st.error("Erro no serviço de geolocalização. O servidor de mapas pode estar congestionado.")

    with col_img:
        # Card decorativo imitando o seu lado direito do Tailwind
        st.markdown("""
        <div class="card-decorativo">
            <h1 style="font-size: 64px; margin-bottom: 0;">🗺️</h1>
            <h3 style="color: #e1e2e7;">Mapa Interativo</h3>
            <p style="color: #88919d;">A visualização do bairro e das rotas logísticas aparecerá aqui após a busca.</p>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TELA 2: PROCESSAMENTO E RESULTADO (O Mapa 3D)
# =============================================================================
elif st.session_state.tela_atual == 2:
    
    st.button("← Fazer Nova Busca", on_click=voltar_tela_1)
    st.divider()

    with st.spinner(" Acionando Pesquisa Operacional e calculando matrizes de roteamento..."):
        try:
            response = requests.post(API_URL, json=st.session_state.payload, headers=HEADERS_API, timeout=15)
            time.sleep(0.5) # Leve delay apenas para efeito visual de carregamento

            if response.status_code == 200:
                dados = response.json()
                
                st.success(f" **Alocação Concluída:** {dados['aluno_id']} foi direcionado(a) com sucesso.")
                
                # Cards de Métricas Estilo Dashboard
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Região", f"Zona {dados['zona_identificada']}")
                c2.metric("Instituição", dados['escola_alocada'])
                c3.metric("Extensão da Rota", f"{dados['distancia_km']} km")
                c4.metric("Deslocamento", f"{dados['tempo_min']} min")
                
                # Renderiza o mapa Deck.gl
                coords = dados['rota_geojson']['coordinates']
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                lat_center = (min(lats) + max(lats)) / 2
                lon_center = (min(lons) + max(lons)) / 2

                render_mapa_clean(coords, lat_center, lon_center, dados['escola_alocada'].upper())

            elif response.status_code == 401:
                st.error("🔒 Conexão bloqueada pelo firewall do servidor. Chave inválida.")
            else:
                st.error(f"Erro na matriz matemática. Código: {response.status_code}")

        except requests.exceptions.RequestException:
            st.error("⚠️ Servidor Oracle offline ou inacessível no momento.")
