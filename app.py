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
# Asegúrate de configurar estos nombres en Streamlit Cloud > Settings > Secrets
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

# --- 4. FUNCIÓN DE CARGA Y FILTRADO (NUEVO FORMATO) ---
@st.cache_data(ttl=300)
def cargar_datos():
    try:
        # Lectura desde el enlace CSV de Google Sheets
        df = pd.read_csv(URL_GSHEETS)
        
        # Limpieza de nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Columnas según tu última imagen: SKU, Descripción del artículo, C. Central, Patrón, Total, Stock
        # Solo mostraremos las dos que pediste:
        columnas_visibles = ['Descripción del artículo', 'Stock']
        
        if set(columnas_visibles).issubset(df.columns):
            # Retornamos solo lo necesario
            return df[columnas_visibles]
        else:
            st.error(f"Error: No se encontraron las columnas exactas. Columnas detectadas: {list(df.columns)}")
            return None
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

# --- 5. FUNCIÓN DE COLORES (CORREGIDA) ---
def resaltar_filas(row):
    # .strip().lower() hace que "Hay stock", "HAY STOCK" o " hay stock " funcionen igual
    estado = str(row['Stock']).strip().lower()
    
    if "hay stock" in estado:
        # Verde RASA (Fondo verde oscuro, texto blanco)
        color = 'background-color: #06402B; color: #FFFFFF; font-weight: bold;'
    elif "no hay stock" in estado:
        # Rojo Alerta (Fondo rojo oscuro, texto blanco)
        color = 'background-color: #5C191E; color: #FFFFFF; font-weight: bold;'
    elif "consultar" in estado:
        # Gris Neutro (Fondo gris oscuro, texto blanco)
        color = 'background-color: #3D3D3D; color: #FFFFFF; font-weight: bold;'
    else:
        # Sin color si no coincide con nada
        color = ''
    
    return [color] * len(row)

# --- 6. LÓGICA DE LA APLICACIÓN ---
if check_password():
    # BARRA LATERAL
    st.sidebar.title("⚙️ Panel de Control")
    st.sidebar.info(f"Sesión activa: **{st.session_state.user_email}**")
    
    if st.sidebar.button("🔄 Actualizar Inventario", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    # CUERPO PRINCIPAL
    st.title("🛞 Stock de Neumáticos - RASA")
    
    with st.spinner('Sincronizando con la base de datos...'):
        df_inventario = cargar_datos()

    if df_inventario is not None:
        # BUSCADOR DINÁMICO
        busqueda = st.text_input("🔍 Buscar por marca, medida o diseño (Ej: 215/75 o BRIDGESTONE):").strip().upper()

        if busqueda:
            # Dividir búsqueda por palabras para búsqueda flexible
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
                    height=600
                )
            else:
                st.warning("No se encontraron productos que coincidan con tu búsqueda.")
        else:
            # VISTA INICIAL
            st.info("💡 Escribe en el buscador para filtrar rápidamente.")
            st.dataframe(
                df_inventario.style.apply(resaltar_filas, axis=1),
                use_container_width=True, 
                hide_index=True,
                height=800
            )

# --- FIN DEL CÓDIGO ---
