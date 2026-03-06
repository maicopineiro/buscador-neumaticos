import streamlit as st
import pandas as pd

# 1. Configuración de seguridad (Cambia 'admin123' por la contraseña que desees)
USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "neumaticos2024"

st.set_page_config(page_title="Stock Privado de Neumáticos", page_icon="🔐")

# Función para verificar el login
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔑 Acceso al Sistema")
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        
        if st.button("Entrar"):
            if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        return False
    return True

# 2. Función de carga de datos (tu formato de 3 columnas)
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv('inventario.csv', sep=';', encoding='latin-1')
        df.columns = df.columns.str.strip()
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar el inventario: {e}")
        return None

# 3. Ejecución de la lógica
if check_password():
    # Botón para cerrar sesión en la barra lateral
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

    st.title("🛞 Buscador de Neumáticos")
    
    df = cargar_datos()

    if df is not None:
        busqueda = st.text_input("🔍 Medida o Modelo (ej: 145/70 o ONYX):").strip().upper()

        if busqueda:
            filtro = (
                df['Medida'].str.contains(busqueda, case=False, na=False) | 
                df['Descripción del artículo'].str.contains(busqueda, case=False, na=False)
            )
            resultados = df[filtro]

            if not resultados.empty:
                def color_stock(val):
                    color = '#d4edda' if val == "Hay Stock" else '#fff3cd' if val == "Consultar" else '#f8d7da'
                    return f'background-color: {color}'

                st.dataframe(
                    resultados.style.applymap(color_stock, subset=['Stock']),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.warning("No se encontraron resultados.")
        else:
            st.info("Ingresa un término para buscar en el inventario.")
