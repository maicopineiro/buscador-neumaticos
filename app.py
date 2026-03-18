import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Stock RASA", 
    page_icon="ico.ico", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CARGA DE CREDENCIALES DESDE SECRETS ---
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

# --- 4. FUNCIÓN DE CARGA Y LIMPIEZA DE DATOS (NUEVO FORMATO) ---
@st.cache_data(ttl=300)
def cargar_datos():
    try:
        # Leemos el CSV
        df = pd.read_csv(URL_GSHEETS)
        
        # Limpiamos espacios en blanco en los nombres de las columnas
        df.columns = df.columns.str.strip()
        
        # Según tu nueva imagen, las columnas son: SKU, Descripción del artículo, C. Central, Patrón, Total, Stock
        # Pero tú solo quieres mostrar 'Descripción del artículo' y 'Stock'
        columnas_finales = ['Descripción del artículo', 'Stock']
        
        if set(columnas_finales).issubset(df.columns):
            # Retornamos solo las dos columnas de interés
            return df[columnas_finales]
        else:
            st.error(f"Error: No se encontraron las columnas. Columnas actuales: {list(df.columns)}")
            return None
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None
# --- 5. ESTILO VISUAL DE LAS FILAS (Versión Robusta) ---
def resaltar_filas(row):
    # .strip() elimina espacios al inicio/final
    # .lower() convierte todo a minúsculas para comparar sin errores
    estado = str(row['Stock']).strip().lower()
    
    if "hay stock" in estado:
        # Verde RASA (Fondo verde, texto blanco)
        color = 'background-color: #06402B; color: #FFFFFF' 
    elif "no hay stock" in estado:
        # Rojo Alerta (Fondo rojo, texto blanco)
        color = 'background-color: #5C191E; color: #FFFFFF' 
    elif "consultar" in estado:
        # Gris Oscuro (Fondo gris, texto blanco)
        color = 'background-color: #3D3D3D; color: #FFFFFF' 
    else:
        # Si la celda está vacía o tiene otro texto
        color = '' 
    
    # Aplicar el mismo color a todas las celdas de la fila
    return [color] * len(row)

# --- 6. LÓGICA PRINCIPAL ---
if check_password():
    # Barra lateral
    st.sidebar.title("Panel de Control")
    st.sidebar.info(f"Usuario: **{st.session_state.user_email}**")
    
    if st.sidebar.button("🔄 Actualizar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.title("🛞 Buscador de Stock - Neumáticos RASA")
    
    with st.spinner('Cargando inventario actualizado...'):
        df_inventario = cargar_datos()

    if df_inventario is not None:
        # Buscador de texto
        busqueda = st.text_input("🔍 Buscar por medida, marca o modelo (ej. 215/75 o BRIDGESTONE):").strip().upper()

        if busqueda:
            # Filtro inteligente por múltiples palabras
            palabras = busqueda.split()
            mask = True
            for p in palabras:
                mask &= df_inventario['Descripción del artículo'].astype(str).str.contains(p, case=False, na=False)
            
            resultados = df_inventario[mask]

            if not resultados.empty:
                st.dataframe(
                    resultados.style.apply(resaltar_filas, axis=1),
                    use_container_width=True,
                    hide_index=True,
                    height=600
                )
            else:
                st.warning("No se encontraron coincidencias para esa búsqueda.")
        else:
            # Vista general inicial
            st.info("Escribe arriba para filtrar el stock.")
            st.dataframe(
                df_inventario.style.apply(resaltar_filas, axis=1),
                use_container_width=True, 
                hide_index=True,
                height=700
            )

# --- FIN ---
