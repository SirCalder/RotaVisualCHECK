import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Nexus Route | Sistema de Alocação",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Nexus Route: Otimizador Autônomo")
st.markdown("**Sistema Inteligente de Distribuição Escolar e Roteamento Logístico**")
st.divider()

# =============================================================================
# DICIONÁRIO DE TEMAS VISUAIS
# =============================================================================
TEMAS = {
    "Industrial / QGIS (Alto Contraste)": {
        "style": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        "bg_html": "#111",
        "glow_color": "[255, 140, 0, 80]",      # Laranja
        "core_color": "[255, 200, 0, 255]",    # Amarelo Ouro
        "orig_color": "[0, 200, 255]",         # Ciano
        "dest_color": "[255, 50, 100]",        # Rosa Choque
        "stroke_color": "[20, 20, 20, 255]",   # Borda Escura
        "text_color": "[255, 255, 255, 255]",
        "text_bg": "[30, 30, 30, 220]"
    },
    "Corporativo (Claro)": {
        "style": "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        "bg_html": "#f0f2f6",
        "glow_color": "[100, 150, 255, 90]",   # Azul Metálico
        "core_color": "[20, 80, 255, 255]",    # Azul Royal
        "orig_color": "[10, 180, 100]",        # Verde Folha
        "dest_color": "[220, 50, 50]",         # Vermelho Clássico
        "stroke_color": "[255, 255, 255, 255]",# Borda Branca
        "text_color": "[50, 50, 50, 255]",
        "text_bg": "[255, 255, 255, 230]"
    },
    "Midnight (Moderno)": {
        "style": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        "bg_html": "#0b0c10",
        "glow_color": "[138, 43, 226, 90]",    # Roxo Vibrante
        "core_color": "[218, 112, 214, 255]",  # Rosa Claro
        "orig_color": "[0, 255, 128]",         # Verde Limão
        "dest_color": "[255, 215, 0]",         # Dourado
        "stroke_color": "[255, 255, 255, 255]",# Borda Branca
        "text_color": "[255, 255, 255, 255]",
        "text_bg": "[20, 15, 30, 220]"
    }
}

# =============================================================================
# SIDEBAR - INPUT DO USUÁRIO
# =============================================================================
with st.sidebar:
    st.header(" Dados do Aluno")
    
    id_aluno = st.text_input("Matrícula / Identificador", value="ALUNO-MVP-01")
    
    st.markdown("### Endereço (Coordenadas)")
    lon_aluno = st.number_input("Longitude", value=-49.522895, format="%.6f")
    lat_aluno = st.number_input("Latitude",  value=-27.057617, format="%.6f")
    
    st.markdown("### Perfil Acadêmico")
    turma = st.number_input("Turma (Ano Escolar)", min_value=1, max_value=9, value=4)
    turno = st.number_input("Turno (1=Manhã, 2=Tarde, 3=Noite)", min_value=1, max_value=3, value=3)
    
    st.markdown("---")
    
    st.header("🎨 Estilização")
    tema_selecionado = st.selectbox("Selecione o Tema Visual", list(TEMAS.keys()))
    
    st.markdown("---")
    calcular = st.button("Alocar e Traçar Rota", type="primary", use_container_width=True)

# =============================================================================
# CONFIGURAÇÃO DE BACKEND (O MAESTRO)
# =============================================================================
# Aponta para a porta 80 do Servidor 2 (O Nginx vai redirecionar internamente para o FastAPI)
API_URL = "http://137.131.134.108/alocar-aluno"
HEADERS_API = {"x-api-key": "ChallengeUDESC"}

# =============================================================================
# FUNÇÃO: Renderiza o mapa mantendo sua animação e SVG customizados
# =============================================================================
def render_mapa_clean(coordinates: list, lat_center: float, lon_center: float, tema: dict, label_escola: str):
    coords_json = json.dumps(coordinates)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background: {tema['bg_html']}; font-family: system-ui, sans-serif; overflow:hidden; }}
  #map {{ width:100%; height:600px; position:relative; border-radius: 8px; }}
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
const colorOrig = {tema['orig_color']};
const colorDest = {tema['dest_color']};

// Função para interpolar cores para o Gradiente
function interpolateColor(c1, c2, factor) {{
    return [
        Math.round(c1[0] + (c2[0] - c1[0]) * factor),
        Math.round(c1[1] + (c2[1] - c1[1]) * factor),
        Math.round(c1[2] + (c2[2] - c1[2]) * factor),
        255
    ];
}}

// Quebrando a rota em segmentos para criar o efeito de gradiente
const segmentedPath = [];
const timestamps = [];
for(let i = 0; i < COORDINATES.length - 1; i++) {{
    const factor = i / (COORDINATES.length - 1);
    segmentedPath.push({{
        path: [COORDINATES[i], COORDINATES[i+1]],
        color: interpolateColor(colorOrig, colorDest, factor)
    }});
    timestamps.push(i * 10);
}}
timestamps.push((COORDINATES.length - 1) * 10);
const maxTime = timestamps[timestamps.length - 1];

const tripData = [{{ path: COORDINATES, timestamps: timestamps }}];

const map = new maplibregl.Map({{
  container: 'map',
  style: '{tema['style']}',
  center: [{lon_center}, {lat_center}],
  zoom: 13.5,
  pitch: 50,
  bearing: 20,
  antialias: true
}});

map.on('load', () => {{
  map.addLayer({{
    'id': '3d-buildings',
    'source': 'carto-dark', 
    'type': 'fill-extrusion',
    'paint': {{
        'fill-extrusion-color': '#aaa',
        'fill-extrusion-height': 10,
        'fill-extrusion-opacity': 0.3
    }}
  }});

  function createMarker(color, label) {{
      const el = document.createElement('div');
      el.style.display = 'flex';
      el.style.flexDirection = 'column';
      el.style.alignItems = 'center';
      
      const r = color[0], g = color[1], b = color[2];
      
      const svg = '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
        '<path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" ' +
        'fill="rgba(' + r + ',' + g + ',' + b + ', 0.9)" stroke="white" stroke-width="2.5"/>' +
        '<circle cx="12" cy="9" r="4" fill="white"/>' +
      '</svg>';
      
      const labelHtml = '<div style="' +
          'background: rgba(20,20,20,0.85); color: white; padding: 4px 10px; border-radius: 6px; ' +
          'font-size: 11px; margin-top: -2px; font-weight: bold; ' +
          'box-shadow: 0 0 10px rgba(' + r + ',' + g + ',' + b + ',0.6); ' +
          'border: 1px solid rgba(' + r + ',' + g + ',' + b + ',0.4);">' + label + '</div>';

      el.innerHTML = svg + labelHtml;
      return el;
  }}

  // Marcadores Customizados
  new maplibregl.Marker({{element: createMarker(colorOrig, 'CASA DO ALUNO'), anchor: 'bottom'}})
      .setLngLat(COORDINATES[0])
      .addTo(map);

  new maplibregl.Marker({{element: createMarker(colorDest, '{label_escola}'), anchor: 'bottom'}})
      .setLngLat(COORDINATES[COORDINATES.length - 1])
      .addTo(map);

  const deckOverlay = new deck.MapboxOverlay({{ interleaved: false, layers: [] }});
  map.addControl(deckOverlay);

  let currentTime = 0;
  function animate() {{
      currentTime = (currentTime + 2) % maxTime;

      deckOverlay.setProps({{
        layers: [
          new PathLayer({{
            id: 'route-glow',
            data: segmentedPath,
            getPath: d => d.path,
            getColor: d => [d.color[0], d.color[1], d.color[2], 90], 
            getWidth: 18, widthUnits: 'pixels', jointRounded: true, capRounded: true,
          }}),
          new PathLayer({{
            id: 'route-core',
            data: segmentedPath,
            getPath: d => d.path,
            getColor: d => d.color, 
            getWidth: 4, widthUnits: 'pixels', jointRounded: true, capRounded: true,
          }}),
          new TripsLayer({{
            id: 'route-pulse',
            data: tripData,
            getPath: d => d.path,
            getTimestamps: d => d.timestamps,
            getColor: [255, 255, 255, 255],
            opacity: 0.9, widthMinPixels: 5, trailLength: maxTime * 0.25,
            currentTime: currentTime, capRounded: true, jointRounded: true
          }})
        ]
      }});
      requestAnimationFrame(animate);
  }}
  animate();
  map.keyboard.disable();
}});
</script>
</body>
</html>
"""
    components.html(html, height=620, scrolling=False)

# =============================================================================
# LÓGICA DE ALOCAÇÃO E ROTEAMENTO
# =============================================================================
if calcular:
    # O Streamlit agora prepara um pacote para o seu Servidor FastAPI, e não pro OSRM
    payload = {
        "id_aluno": id_aluno,
        "lat": lat_aluno,
        "lon": lon_aluno,
        "turma": turma,
        "turno": turno
    }

    with st.spinner(" Acionando Otimização Matemática e Roteamento Autônomo..."):
        try:
            # Envio da requisição com o cabeçalho de segurança exigido pelo Nginx
            response = requests.post(API_URL, json=payload, headers=HEADERS_API, timeout=15)

            if response.status_code == 401:
                st.error(" Acesso Negado: Chave de segurança inválida.")
            
            elif response.status_code == 200:
                dados = response.json()
                
                st.success(f" Otimização concluída! O aluno **{dados['aluno_id']}** foi alocado com sucesso.")
                
                # Painel de Métricas (Consumindo a resposta pronta do FastAPI)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(" Região Demográfica", f"Zona {dados['zona_identificada']}")
                c2.metric(" Escola Alocada", dados['escola_alocada'])
                c3.metric(" Distância Lógica", f"{dados['distancia_km']} km")
                c4.metric("⏱ Tempo de Rota", f"{dados['tempo_min']} min")
                
                st.markdown("<br>", unsafe_allow_html=True)

                # Extrai as coordenadas retornadas pelo Maestro
                coords = dados['rota_geojson']['coordinates']
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                lat_center = (min(lats) + max(lats)) / 2
                lon_center = (min(lons) + max(lons)) / 2

                # Renderiza o mapa com a escola identificada e a animação
                tema_atual = TEMAS[tema_selecionado]
                render_mapa_clean(coords, lat_center, lon_center, tema_atual, dados['escola_alocada'].upper())

            else:
                st.error(f"Erro no servidor. Código: {response.status_code} | Detalhe: {response.text}")

        except requests.exceptions.RequestException:
            st.error("⚠️ Falha de Conexão. Verifique se o Servidor Maestro está ativo e a porta 80 liberada.")
else:
    st.info("👈 Preencha os dados de residência e perfil escolar do aluno, escolha um tema e clique em **Alocar e Traçar Rota**.")
