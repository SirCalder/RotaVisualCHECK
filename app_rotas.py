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
OSRM_URL = "http://<IP_ADDRESS>:80/route/v1/driving"

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
const {{ DeckGL, PathLayer, ScatterplotLayer, TextLayer }} = deck;

const COORDINATES = {coords_json};

const PATH_DATA = [{{ path: COORDINATES }}];

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
  // Opcional: Adiciona construções em 3D nativas do MapLibre (funciona melhor nos temas escuros)
  map.addLayer({{
    'id': '3d-buildings',
    'source': 'carto-dark', // Nome fictício se não houver fonte vetorizada, mas previne erro
    'type': 'fill-extrusion',
    'paint': {{
        'fill-extrusion-color': '#aaa',
        'fill-extrusion-height': 10,
        'fill-extrusion-opacity': 0.5
    }}
  }});

  const deckOverlay = new deck.MapboxOverlay({{
    interleaved: false,
    layers: [
      // 1. Rota - Sombra/Glow
      new PathLayer({{
        id: 'route-glow',
        data: PATH_DATA,
        getPath: d => d.path,
        getColor: {tema['glow_color']}, 
        getWidth: 18,
        widthUnits: 'pixels',
        jointRounded: true,
        capRounded: true,
      }}),

      // 2. Rota - Núcleo
      new PathLayer({{
        id: 'route-core',
        data: PATH_DATA,
        getPath: d => d.path,
        getColor: {tema['core_color']}, 
        getWidth: 4,
        widthUnits: 'pixels',
        jointRounded: true,
        capRounded: true,
      }}),

      // 3. Marcadores de Origem e Destino
      new ScatterplotLayer({{
        id: 'markers',
        data: [
          {{ position: COORDINATES[0], color: {tema['orig_color']} }},
          {{ position: COORDINATES[COORDINATES.length - 1], color: {tema['dest_color']} }}
        ],
        getPosition: d => d.position,
        getFillColor: d => d.color,
        getRadius: 8,
        radiusUnits: 'pixels',
        stroked: true,
        getLineColor: {tema['stroke_color']}, 
        getLineWidth: 2.5,
        lineWidthUnits: 'pixels',
      }}),

      // 4. Etiquetas de Texto Limpas
      new TextLayer({{
        id: 'text-labels',
        data: [
          {{ position: COORDINATES[0], text: 'ORIGEM', offset: [0, -22] }},
          {{ position: COORDINATES[COORDINATES.length - 1], text: 'DESTINO', offset: [0, -22] }}
        ],
        getPosition: d => d.position,
        getText: d => d.text,
        getSize: 12,
        getColor: {tema['text_color']},
        getPixelOffset: d => d.offset,
        fontFamily: 'system-ui, sans-serif',
        fontWeight: 'bold',
        background: true,
        getBackgroundColor: {tema['text_bg']},
        backgroundPadding: [8, 4],
        cornerRadius: 4
      }})
    ]
  }});

  map.addControl(deckOverlay);
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
    headers = {" Substitua pela sua chave configurada no Nginx"}

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
