import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Stock RASA", 
    page_icon="🛞", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CARGA DE CREDENCIALES DESDE SECRETS ---
# Estos valores se configuran en el panel de Streamlit Cloud (Settings > Secrets)
USUARIO_SISTEMA = st.secrets["credentials"]["usuario"]
CLAVE_SISTEMA = st.secrets["credentials"]["clave"]
URL_GSHEETS = st.secrets["gsheets"]["url"]

# --- 3. FUNCIÓN DE AUTENTICACIÓN ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔑 Acceso al Sistema - RASA")
        col1, _ = st.columns([1, 2])
        with col1:
            usuario_input = st.text_input("Usuario").strip()
            clave_input = st.text_input("Contraseña", type="password")
            
            if st.button("Entrar", use_container_width=True):
                if usuario_input == USUARIO_SISTEMA and clave_input == CLAVE_SISTEMA:
                    st.session_state.authenticated = True
                    st.session_state.user_email = usuario_input
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        return False
    return True

# --- 4. FUNCIÓN DE CARGA Y LIMPIEZA DE DATOS ---
@st.cache_data(ttl=300) # Se actualiza automáticamente cada 5 minutos
def cargar_datos():
    try:
        # Leemos el CSV desde Google Sheets
        df = pd.read_csv(URL_GSHEETS)
        
        # Limpieza de nombres de columnas (quita espacios extra)
        df.columns = df.columns.str.strip()
        
        # Mantenemos solo las columnas solicitadas
        columnas_visibles = ['Descripción del artículo', 'Stock']
        
        # Filtrar solo si las columnas existen en el archivo original
        if set(columnas_visibles).issubset(df.columns):
            df = df[columnas_visibles]
        else:
            st.error(f"Error: No se encontraron las columnas exactas. Columnas detectadas: {list(df.columns)}")
            return None
            
        return df
    except Exception as e:
        st.error(f"Error crítico al conectar con la base de datos: {e}")
        return None

# --- 5. ESTILO VISUAL DE LAS FILAS ---
def resaltar_filas(row):
    # Lógica basada en el texto de la columna 'Stock'
    estado = str(row['Stock']).lower()
    if "hay stock" in estado:
        return ['background-color: #06402B; color: #FFFFFF'] * len(row) # Verde RASA
    elif "no hay" in estado:
        return ['background-color: #5C191E; color: #FFFFFF'] * len(row) # Rojo Alerta
    elif "consultar" in estado:
        return ['background-color: #3D3D3D; color: #FFFFFF'] * len(row) # Gris Neutro
    return [''] * len(row)

# --- 6. LÓGICA PRINCIPAL DE LA APLICACIÓN ---
if check_password():
    # BARRA LATERAL (Sidebar)
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2933/2933830.png", width=100)
    st.sidebar.title("Panel de Control")
    st.sidebar.write(f"👤 Usuario: **{st.session_state.user_email}**")
    
    if st.sidebar.button("🔄 Forzar Actualización", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    # CUERPO PRINCIPAL
    st.title("🛞 Buscador de Stock - Neumáticos RASA")
    
    with st.spinner('Obteniendo datos de inventario...'):
        df_inventario = cargar_datos()

    if df_inventario is not None:
        # BUSCADOR
        busqueda = st.text_input("🔍 Buscar por marca, medida o diseño (Ej: 215/65, Onyx, Bridgestone):").strip().upper()

        if busqueda:
            palabras = busqueda.split()
            mask = True
            for p in palabras:
                mask &= df_inventario['Descripción del artículo'].astype(str).str.contains(p, case=False, na=False)
            
            resultados = df_inventario[mask]

            if not resultados.empty:
                st.success(f"Se encontraron **{len(resultados)}** coincidencias.")
                st.dataframe(
                    resultados.style.apply(resaltar_filas, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    height=500
                )
            else:
                st.warning("No se encontraron productos con ese criterio de búsqueda.")
        else:
            # VISTA POR DEFECTO (Primeros 50 productos)
            st.info("💡 Tip: Puedes buscar múltiples términos a la vez, por ejemplo: 'Bridgestone 215'")
            st.subheader("Lista Completa de Inventario")
            st.dataframe(
                df_inventario.style.apply(resaltar_filas, axis=1),
                use_container_width=True, 
                hide_index=True,
                height=700
            )

# --- FIN DEL CÓDIGO ---
