import streamlit as st
import pandas as pd

# --- 1. Configuración de Página ---
st.set_page_config(
    page_title="Stock RASA", 
    page_icon="🛞", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Carga de Credenciales ---
USUARIO_SISTEMA = st.secrets["credentials"]["usuario"]
CLAVE_SISTEMA = st.secrets["credentials"]["clave"]
URL_GSHEETS = st.secrets["gsheets"]["url"]

# --- 3. Función de Autenticación ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔑 Acceso al Sistema")
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

# --- 4. Función de Carga y Limpieza (Actualizada según imagen) ---
@st.cache_data(ttl=600)
def cargar_datos():
    try:
        # Importante: Asegúrate de que el CSV de Google Sheets tenga estos encabezados exactos
        df = pd.read_csv(URL_GSHEETS)
        df.columns = df.columns.str.strip()
        
        # Seleccionamos solo las columnas que quieres mostrar según la imagen
        # Usamos 'Descripción del artículo' y 'Stock'
        columnas_interes = ['Descripción del artículo', 'Stock']
        
        # Verificamos si las columnas existen para evitar errores
        df = df[columnas_interes]
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None


# --- 5. Estilo Visual ---
def resaltar_filas(row):
    # Convertimos a string, quitamos espacios y pasamos a minúsculas para comparar mejor
    val = str(row['Stock']).strip().lower()
    
    # Definimos colores (puedes ajustarlos a tu gusto)
    verde = 'background-color: #06402B; color: #FFFFFF;' # Verde oscuro, texto blanco
    rojo = 'background-color: #5C191E; color: #FFFFFF;'  # Rojo oscuro, texto blanco
    gris = 'background-color: #333333; color: #FFFFFF;'  # Gris para otros
    
    if "hay stock" in val and "no hay" not in val:
        color = verde
    elif "no hay" in val:
        color = rojo
    else:
        color = gris
        
    return [color] * len(row)

# --- 6. Lógica Principal ---
if check_password():
    st.sidebar.title("⚙️ Panel de Control")
    st.sidebar.info(f"Conectado como: **{st.session_state.user_email}**")
    
    if st.sidebar.button("🔄 Actualizar Inventario"):
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.title("🛞 Buscador de Neumáticos - RASA")
    
    with st.spinner('Sincronizando inventario...'):
        df_inventario = cargar_datos()

    if df_inventario is not None:
        busqueda = st.text_input("🔍 Buscar por Medida, Marca o Modelo:").strip().upper()

        if busqueda:
            palabras = busqueda.split()
            mask = True
            for p in palabras:
                # Busca solo en la descripción del artículo
                mask &= df_inventario['Descripción del artículo'].astype(str).str.contains(p, case=False, na=False)
            
            resultados = df_inventario[mask]

            if not resultados.empty:
                st.success(f"Se encontraron **{len(resultados)}** productos.")
                st.dataframe(
                    resultados.style.apply(resaltar_filas, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    height=600
                )
            else:
                st.warning("No se encontraron coincidencias.")
        else:
            st.info("💡 Escribe para filtrar. Ejemplo: '215/65' o 'BRIDGESTONE'")
            
            # Vista previa inicial de los productos
            st.dataframe(
                df_inventario.style.apply(resaltar_filas, axis=1),
                use_container_width=True, 
                hide_index=True
            )




