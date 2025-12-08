"""
Dashboard interactivo de EcoShop utilizando Streamlit y Plotly.
Muestra análisis y visualizaciones del impacto ambiental de productos.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Agregar path
ecoshop_path = Path(__file__).parent.parent / "backend" / "ecoshop-data"
sys.path.append(str(ecoshop_path))

from data_module.impact_calculator import ImpactCalculator

# Paleta de colores EcoShop
ECOSHOP_COLORS = {
    'cream': '#F5E3C8',
    'light': '#FDF5E8',
    'white': '#FFFCF4',
    'green': '#6A8459',
    'dark': '#393939',
    'green_light': '#8B9E7A',
    'green_pale': '#B8C5A9'
}

ECOSHOP_PALETTE = ['#6A8459', '#8B9E7A', '#B8C5A9', '#F5E3C8', '#393939']

# Configuración
st.set_page_config(
    page_title="EcoShop Dashboard",
    page_icon="🌱",
    layout="wide"
)

# CSS personalizado - Tema Crema
st.markdown("""
    <style>
    /* Fondo general crema */
    .stApp {
        background-color: #FFFCF4 !important;
    }
    
    .main {
        background-color: #FFFCF4 !important;
    }
    
    .block-container {
        background-color: #FFFCF4 !important;
        padding-top: 2rem;
    }
    
    /* Sidebar con tono más oscuro */
    [data-testid="stSidebar"] {
        background-color: #FDF5E8 !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #FDF5E8 !important;
    }
    
    /* Headers verdes */
    h1, h2, h3 {
        color: #6A8459 !important;
    }
    
    /* Texto general oscuro */
    p, span, label, [data-testid="stMarkdownContainer"] {
        color: #393939 !important;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        color: #6A8459 !important;
        font-weight: bold;
    }
    
    [data-testid="stMetricLabel"] {
        color: #393939 !important;
    }
    
    /* Botones */
    .stButton>button {
        background-color: #6A8459 !important;
        color: #FFFCF4 !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #576d48 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #F5E3C8 !important;
        color: #393939 !important;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #6A8459 !important;
        color: #FFFCF4 !important;
    }
    
    /* DataFrames */
    .dataframe {
        background-color: white !important;
    }
    
    /* Inputs */
    .stSelectbox label, .stSlider label, .stCheckbox label {
        color: #393939 !important;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #393939 !important;
    }
    
    .stRadio [role="radiogroup"] label {
        color: #393939 !important;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data():
    csv_path = Path(__file__).parent.parent / "backend" / "ecoshop-data" / "data" / "products_with_impact.csv"
    return pd.read_csv(csv_path)


def create_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'color': ECOSHOP_COLORS['green'], 'size': 16}},
        number={'font': {'color': ECOSHOP_COLORS['dark'], 'size': 32}},
        gauge={
            'axis': {'range': [None, 3], 'tickcolor': ECOSHOP_COLORS['dark']},
            'bar': {'color': ECOSHOP_COLORS['green']},
            'steps': [
                {'range': [0, 0.5], 'color': ECOSHOP_COLORS['green_pale']},
                {'range': [0.5, 1.5], 'color': ECOSHOP_COLORS['cream']},
                {'range': [1.5, 3], 'color': '#D4A574'}
            ],
        }
    ))
    fig.update_layout(
        height=250,
        paper_bgcolor=ECOSHOP_COLORS['white'],
        font={'color': ECOSHOP_COLORS['dark']}
    )
    return fig


def style_plotly_chart(fig):
    """Aplica estilos EcoShop a gráficos Plotly"""
    fig.update_layout(
        plot_bgcolor=ECOSHOP_COLORS['white'],
        paper_bgcolor=ECOSHOP_COLORS['white'],
        font=dict(color=ECOSHOP_COLORS['dark']),
        title_font_color=ECOSHOP_COLORS['green'],
        title_font_size=18
    )
    return fig


# Cargar datos
try:
    df = load_data()
except Exception as e:
    st.error(f" Error: {e}")
    st.info(" Ejecutar: `python backend/ecoshop-data/data_module/impact_calculator.py`")
    st.stop()


# SIDEBAR
st.sidebar.title("🌱 EcoShop Dashboard")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navegación",
    ["🏠 Inicio", "📊 Análisis", "🔍 Explorador de Productos"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Estadísticas Globales")
st.sidebar.metric("Total Productos", len(df))
st.sidebar.metric("Huella Promedio", f"{df['huella_total'].mean():.3f} kg CO2e")
if 'recyclable_packaging' in df.columns:
    st.sidebar.metric("% Reciclable", f"{df['recyclable_packaging'].sum()/len(df)*100:.1f}%")


# PÁGINA: INICIO
if page == "🏠 Inicio":
    st.title("🌍 EcoShop - Dashboard de Impacto Ambiental")
    
    st.markdown("""
    **EcoShop** | E-commerce desarrollado para promover el consumo sostenible
    """)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        bajo = len(df[df['eco_badge'].str.contains('Bajo', na=False)])
        st.metric("🌱 Bajo Impacto", bajo, f"{bajo/len(df)*100:.1f}%")
    
    with col2:
        medio = len(df[df['eco_badge'].str.contains('Medio', na=False)])
        st.metric("🌿 Medio Impacto", medio, f"{medio/len(df)*100:.1f}%")
    
    with col3:
        alto = len(df[df['eco_badge'].str.contains('Alto', na=False)])
        st.metric("🌳 Alto Impacto", alto, f"{alto/len(df)*100:.1f}%")
    
    with col4:
        st.metric("💰 Precio Promedio", f"${df['money'].mean():.2f}", "USD")
    
    st.markdown("---")
    st.subheader("📊 Distribución de Impacto por Categoría")
    
    fig = px.box(df, x='category', y='huella_total', color='category',
                 title="Huella de Carbono por Categoría",
                 color_discrete_sequence=ECOSHOP_PALETTE)
    fig = style_plotly_chart(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📋 Resumen por Categoría")
    resumen = df.groupby('category').agg({
        'huella_total': ['mean', 'min', 'max'],
        'money': 'mean',
        'product': 'count'
    }).round(3)
    resumen.columns = ['Huella Promedio', 'Huella Mín', 'Huella Máx', 'Precio Promedio', 'Cantidad']
    st.dataframe(resumen, use_container_width=True)


# PÁGINA: ANÁLISIS
elif page == "📊 Análisis":
    st.title(" Análisis Detallado")
    
    tab1, tab2, tab3 = st.tabs(["Composición", "Comparativas", "Top Productos"])
    
    with tab1:
        st.subheader("Composición de la Huella")
        
        col1, col2 = st.columns(2)
        
        with col1:
            componentes = df[['huella_materiales', 'huella_transporte', 'huella_manufactura']].mean()
            fig = px.pie(values=componentes.values,
                        names=['Materiales', 'Transporte', 'Manufactura'],
                        title="Composición Promedio",
                        color_discrete_sequence=ECOSHOP_PALETTE)
            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.plotly_chart(create_gauge(df['huella_total'].mean(), "Huella Promedio (kg CO2e)"),
                          use_container_width=True)
    
    with tab2:
        st.subheader("Comparativas")
        
        fig = px.bar(df.groupby('category')['huella_total'].mean().reset_index(),
                    x='category', y='huella_total',
                    title="Huella Promedio por Categoría",
                    color_discrete_sequence=[ECOSHOP_COLORS['green']])
        fig = style_plotly_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        if 'recyclable_packaging' in df.columns:
            fig = px.box(df, x='recyclable_packaging', y='huella_total',
                        color='recyclable_packaging',
                        title="Impacto: Reciclable vs No Reciclable",
                        color_discrete_sequence=ECOSHOP_PALETTE)
            fig = style_plotly_chart(fig)
            st.plotly_chart(fig, use_container_width=True)
        
        fig = px.scatter(df, x='money', y='huella_total', color='category',
                        size='weight', hover_data=['product', 'brand'],
                        title="Precio vs Impacto",
                        color_discrete_sequence=ECOSHOP_PALETTE)
        fig = style_plotly_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader(" **Top 10 Más Sostenibles** ")
        
        top_sostenibles = df.nsmallest(10, 'huella_total')[
            ['product', 'brand', 'category', 'money', 'huella_total', 'eco_badge']
        ]
        st.dataframe(top_sostenibles, use_container_width=True)
        
        fig = px.bar(top_sostenibles, x='product', y='huella_total',
                    color='eco_badge', title="Top 10 Más Sostenibles",
                    color_discrete_map={
                        '🌱 Bajo impacto': ECOSHOP_COLORS['green'],
                        '🌿 Medio impacto': ECOSHOP_COLORS['cream'],
                        '🌳 Alto impacto': ECOSHOP_COLORS['dark']
                    })
        fig.update_xaxes(tickangle=-45)
        fig = style_plotly_chart(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.subheader(" **Top 10 Mayor Impacto** ")
        
        top_impacto = df.nlargest(10, 'huella_total')[
            ['product', 'brand', 'category', 'money', 'huella_total', 'eco_badge']
        ]
        st.dataframe(top_impacto, use_container_width=True)


# PÁGINA: EXPLORADOR
elif page == "🔍 Explorador de Productos":
    st.title("🔍 Explorador de Productos")
    
    st.markdown(f"**Total disponibles: {len(df)} productos**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categorias = ['Todas'] + sorted(df['category'].unique().tolist())
        categoria_sel = st.selectbox("Categoría", categorias)
    
    with col2:
        precio_max = st.slider("Precio máximo (USD)", 
                              float(df['money'].min()), 
                              float(df['money'].max()), 
                              float(df['money'].max()))
    
    with col3:
        if 'recyclable_packaging' in df.columns:
            solo_reciclable = st.checkbox("Solo reciclables", value=False)
        else:
            solo_reciclable = False
    
    # Filtrar
    df_filtered = df.copy()
    
    if categoria_sel != 'Todas':
        df_filtered = df_filtered[df_filtered['category'] == categoria_sel]
    
    df_filtered = df_filtered[df_filtered['money'] <= precio_max]
    
    if solo_reciclable and 'recyclable_packaging' in df.columns:
        df_filtered = df_filtered[df_filtered['recyclable_packaging'] == True]
    
    # Orden
    orden = st.radio("Ordenar por:", 
                    ["Menor huella", "Mayor huella", "Menor precio", "Mayor precio"],
                    horizontal=True)
    
    if orden == "Menor huella":
        df_filtered = df_filtered.sort_values('huella_total')
    elif orden == "Mayor huella":
        df_filtered = df_filtered.sort_values('huella_total', ascending=False)
    elif orden == "Menor precio":
        df_filtered = df_filtered.sort_values('money')
    else:
        df_filtered = df_filtered.sort_values('money', ascending=False)
    
    st.markdown(f"**Mostrando: {len(df_filtered)} productos**")
    
    if len(df_filtered) == 0:
        st.warning("No hay productos que cumplan los filtros seleccionados.")
    else:
        st.dataframe(
            df_filtered[['product', 'brand', 'category', 'money', 'huella_total', 'eco_badge']],
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader(" Detalle de Producto")
        
        producto_sel = st.selectbox("Seleccionar:", df_filtered['product'].tolist())
        
        prod = df_filtered[df_filtered['product'] == producto_sel].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(" Precio", f"${prod['money']:.2f} USD")
            st.metric(" Peso", f"{prod['weight']} g")
            if 'origin_country' in prod:
                st.metric(" Origen", prod['origin_country'])
        
        with col2:
            st.metric(" Huella Total", f"{prod['huella_total']:.3f} kg CO2e")
            st.metric(" Eco-Badge", prod['eco_badge'])
            if 'brand' in prod:
                st.metric(" Marca", prod['brand'])
        
        with col3:
            if 'packaging_material' in prod:
                st.metric(" Packaging", prod['packaging_material'].replace('_', ' ').title())
            if 'recyclable_packaging' in prod:
                st.metric(" Reciclable", "Sí" if prod['recyclable_packaging'] else "No")
            if 'ingredient_main' in prod:
                st.metric(" Ingrediente", prod['ingredient_main'])
        
        st.markdown("---")
        st.subheader(" Desglose de Huella")
        
        fig = go.Figure(data=[
            go.Bar(name='Materiales', x=['Materiales'], y=[prod['huella_materiales']], 
                  marker_color=ECOSHOP_COLORS['green']),
            go.Bar(name='Transporte', x=['Transporte'], y=[prod['huella_transporte']], 
                  marker_color=ECOSHOP_COLORS['cream']),
            go.Bar(name='Manufactura', x=['Manufactura'], y=[prod['huella_manufactura']], 
                  marker_color=ECOSHOP_COLORS['green_light'])
        ])
        fig.update_layout(yaxis_title="kg CO2e", showlegend=True)
        fig = style_plotly_chart(fig)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("🌱 **EcoShop Dashboard** | E-Commerce desarrollado para promover el consumo sostenible")

