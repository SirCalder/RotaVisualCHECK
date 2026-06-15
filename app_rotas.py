import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Nexus Route | Sistema de Roteamento",
    page_icon="#",
    layout="wide"
)

st.title(" Nexus Route: Otimizador Autônomo")
st.markdown("**Motor de Roteamento Baseado em OSRM (Infraestrutura Customizada)**")
st.divider()

# =============================================================================
# DICIONÁRIO DE TEMAS VISUAIS
# =============================================================================
TEMAS = {
    "Industrial / QGIS (Alto Contraste)": {
        "style": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        "bg_html": "#111",
        "glow_color": "[255, 140, 0, 80]",     # Laranja
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
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.header(" Parâmetros da Rota")
    
    st.markdown("### Ponto de Origem")
    lon_orig = st.number_input("Longitude", value=-49.522895, format="%.6f", key="lon_orig")
    lat_orig = st.number_input("Latitude",  value=-27.057617, format="%.6f", key="lat_orig")
    
    st.markdown("### Ponto de Destino")
    lon_dest = st.number_input("Longitude", value=-49.550954, format="%.6f", key="lon_dest")
    lat_dest = st.number_input("Latitude",  value=-27.031774, format="%.6f", key="lat_dest")
    
    st.markdown("---")
    
    st.header(" Estilização")
    tema_selecionado = st.selectbox("Selecione o Tema do Mapa", list(TEMAS.keys()))
    
    st.markdown("---")
    calcular = st.button("Traçar Rota", type="primary", use_container_width=True)

# =============================================================================
# SERVIDOR OSRM
# =============================================================================
# Substitua pelo IP público do Oracle Cloud que está com o OSRM rodando
OSRM_URL = "http://64.181.181.24/route/v1/driving"

# =============================================================================
# FUNÇÃO: Renderiza o mapa aplicando o tema dinamicamente
# =============================================================================
def render_mapa_clean(coordinates: list, lat_center: float, lon_center: float, tema: dict):
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
    timestamps.push(i * 10); // Timestamps para a animação
}}
// Timestamp final para o último ponto
timestamps.push((COORDINATES.length - 1) * 10);
const maxTime = timestamps[timestamps.length - 1];

// Dados para a animação de pulso
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
  // Construções 3D
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

  // Criando Marcadores Customizados em SVG
  function createMarker(color, label) {{
      const el = document.createElement('div');
      el.style.display = 'flex';
      el.style.flexDirection = 'column';
      el.style.alignItems = 'center';
      
      const r = color[0], g = color[1], b = color[2];
      
      // Pin Icon (SVG desenhado no JS via concatenação para evitar erros de formatação do Python)
      const svg = '<svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
        '<path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" ' +
        'fill="rgba(' + r + ',' + g + ',' + b + ', 0.9)" stroke="white" stroke-width="2.5"/>' +
        '<circle cx="12" cy="9" r="4" fill="white"/>' +
      '</svg>';
      
      // Label flutuante abaixo do Pin
      const labelHtml = '<div style="' +
          'background: rgba(20,20,20,0.85); ' +
          'color: white; padding: 4px 10px; border-radius: 6px; ' +
          'font-size: 11px; margin-top: -2px; font-weight: bold; ' +
          'box-shadow: 0 0 10px rgba(' + r + ',' + g + ',' + b + ',0.6); ' +
          'border: 1px solid rgba(' + r + ',' + g + ',' + b + ',0.4);' +
      '">' + label + '</div>';

      el.innerHTML = svg + labelHtml;
      return el;
  }}

  // Adiciona a Origem e Destino com os Ícones HTML/SVG
  new maplibregl.Marker({{element: createMarker(colorOrig, 'ORIGEM'), anchor: 'bottom'}})
      .setLngLat(COORDINATES[0])
      .addTo(map);

  new maplibregl.Marker({{element: createMarker(colorDest, 'DESTINO'), anchor: 'bottom'}})
      .setLngLat(COORDINATES[COORDINATES.length - 1])
      .addTo(map);

  // Instância base do Deck.GL
  const deckOverlay = new deck.MapboxOverlay({{
    interleaved: false,
    layers: []
  }});
  map.addControl(deckOverlay);

  // LOOP DE RENDERIZAÇÃO ANIMADA
  let currentTime = 0;
  function animate() {{
      currentTime = (currentTime + 2) % maxTime; // Velocidade da animação

      deckOverlay.setProps({{
        layers: [
          // 1. Rota - Sombra/Glow com Gradiente
          new PathLayer({{
            id: 'route-glow',
            data: segmentedPath,
            getPath: d => d.path,
            getColor: d => [d.color[0], d.color[1], d.color[2], 90], 
            getWidth: 18,
            widthUnits: 'pixels',
            jointRounded: true,
            capRounded: true,
          }}),

          // 2. Rota - Núcleo com Gradiente
          new PathLayer({{
            id: 'route-core',
            data: segmentedPath,
            getPath: d => d.path,
            getColor: d => d.color, 
            getWidth: 4,
            widthUnits: 'pixels',
            jointRounded: true,
            capRounded: true,
          }}),

          // 3. Efeito animado do trajeto (TripsLayer)
          new TripsLayer({{
            id: 'route-pulse',
            data: tripData,
            getPath: d => d.path,
            getTimestamps: d => d.timestamps,
            getColor: [255, 255, 255, 255], // Branco brilhante
            opacity: 0.9,
            widthMinPixels: 5,
            trailLength: maxTime * 0.25, // Tamanho do rastro animado
            currentTime: currentTime,
            capRounded: true,
            jointRounded: true
          }})
        ]
      }});

      requestAnimationFrame(animate);
  }}

  // Inicia a animação
  animate();
  map.keyboard.disable();
}});
</script>
</body>
</html>
"""
    components.html(html, height=620, scrolling=False)

# =============================================================================
# LÓGICA PRINCIPAL
# =============================================================================
if calcular:
    url = f"{OSRM_URL}/{lon_orig},{lat_orig};{lon_dest},{lat_dest}?overview=full&geometries=geojson"
    headers = {"x-api-key": "labind_udesc_2026"}

    with st.spinner("Consultando motor de rotas no servidor..."):
        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 401:
                st.error(" Acesso Negado: Chave de API inválida.")

            elif response.status_code == 200:
                data = response.json()

                if data.get("code") == "Ok":
                    # Extração de Métricas
                    distancia_km = data["routes"][0]["distance"] / 1000
                    tempo_min    = data["routes"][0]["duration"] / 60
                    
                    # Painel de Métricas Nativo do Streamlit
                    col1, col2, col3 = st.columns(3)
                    col1.metric(" Distância", f"{distancia_km:.2f} km")
                    col2.metric(" Tempo Estimado", f"{tempo_min:.0f} min")
                    col3.metric(" Status", "Online (Privado)")
                    
                    st.markdown("<br>", unsafe_allow_html=True)

                    # Dados do Mapa
                    coords = data["routes"][0]["geometry"]["coordinates"]
                    lons = [c[0] for c in coords]
                    lats = [c[1] for c in coords]
                    lat_center = (min(lats) + max(lats)) / 2
                    lon_center = (min(lons) + max(lons)) / 2

                    # Renderização repassando o tema escolhido
                    tema_atual = TEMAS[tema_selecionado]
                    render_mapa_clean(coords, lat_center, lon_center, tema_atual)

                else:
                    st.warning("Nenhum caminho viável encontrado entre os pontos informados.")
            else:
                st.error(f"Erro no servidor. Código: {response.status_code}")

        except requests.exceptions.RequestException:
            st.error(" Falha de Conexão. Verifique se o servidor na Oracle está ativo e a porta 80 liberada.")
else:
    # Estado inicial limpo
    st.info(" Ajuste o Tema e as Coordenadas na barra lateral e clique em **Traçar Rota** para iniciar.")
