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
# Asegúrate de configurar estos nombres en el panel de 'Secrets' de Streamlit Cloud
try:
    USUARIO_SISTEMA = st.secrets["credentials"]["usuario"]
    CLAVE_SISTEMA = st.secrets["credentials"]["clave"]
    URL_GSHEETS = st.secrets["gsheets"]["url"]
except Exception:
    st.error("Error: No se encontraron las credenciales en st.secrets. Verifica la configuración.")
    st.stop()

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
@st.cache_data(ttl=300) # Se actualiza cada 5 minutos automáticamente
def cargar_datos():
    try:
        # Lectura del CSV desde la URL pública de Google Sheets
        df = pd.read_csv(URL_GSHEETS)
        
        # Limpieza de nombres de columnas (quita espacios invisibles)
        df.columns = df.columns.str.strip()
        
        # Columnas que queremos mostrar (según tu requerimiento)
        columnas_visibles = ['Descripción del artículo', 'Stock']
        
        # Verificamos que las columnas existan antes de filtrar
        if set(columnas_visibles).issubset(df.columns):
            return df[columnas_visibles]
        else:
            st.error(f"Error: No se encontraron las columnas esperadas. Detectadas: {list(df.columns)}")
            return None
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

# --- 5. FUNCIÓN PARA LOS COLORES DE LAS FILAS ---
def resaltar_filas(row):
    # .strip().lower() asegura que no importen espacios ni mayúsculas/minúsculas
    estado = str(row['Stock']).strip().lower()
    
    if "hay stock" in estado:
        # Verde oscuro con texto blanco
        color = 'background-color: #06402B; color: #FFFFFF;' 
    elif "no hay stock" in estado:
        # Rojo oscuro con texto blanco
        color = 'background-color: #5C191E; color: #FFFFFF;' 
    elif "consultar" in estado:
        # Gris oscuro con texto blanco
        color = 'background-color: #3D3D3D; color: #FFFFFF;' 
    else:
        # Sin formato para cualquier otro caso
        color = ''
    
    return [color] * len(row)

# --- 6. LÓGICA PRINCIPAL DE LA APP ---
if check_password():
    # BARRA LATERAL
    st.sidebar.title("Panel de Control")
    st.sidebar.write(f"👤 Conectado como: **{st.session_state.user_email}**")
    
    # Botón para forzar la actualización de datos
    if st.sidebar.button("🔄 Actualizar Inventario", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Botón de Salir
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.title("🛞 Buscador de Neumáticos - RASA")
    
    with st.spinner('Sincronizando con la base de datos...'):
        df_inventario = cargar_datos()

    if df_inventario is not None:
        # CAMPO DE BÚSQUEDA
        busqueda = st.text_input("🔍 Buscar por marca, medida o diseño (Ej: 215/75 o BRIDGESTONE):").strip().upper()

        if busqueda:
            # Dividir búsqueda en palabras para filtrar mejor (ej: "ONYX 215")
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
                    height=600 # Altura para evitar que la página sea eterna
                )
            else:
                st.warning("No se encontraron productos que coincidan con tu búsqueda.")
        else:
            # VISTA POR DEFECTO (Si no hay búsqueda escrita)
            st.info("💡 Escribe en el buscador para filtrar. La tabla muestra todo el stock disponible.")
            st.dataframe(
                df_inventario.style.apply(resaltar_filas, axis=1),
                use_container_width=True, 
                hide_index=True,
                height=800
            )

# --- FIN DEL CÓDIGO ---
