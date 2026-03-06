import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Buscador de Neumáticos", page_icon="🛞")

st.title("🔍 Consulta de Stock")
st.markdown("Busca por medida (ej: 145/70 R12) o marca.")

@st.cache_data
def cargar_datos():
    try:
        # Cargamos el CSV con el nuevo formato (Descripción, Medida, Stock)
        df = pd.read_csv('inventario.csv', sep=';', encoding='latin-1')
        
        # Limpieza de espacios en blanco en los textos
        df.columns = df.columns.str.strip()
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

df = cargar_datos()

if df is not None:
    # Buscador inteligente
    busqueda = st.text_input("Escribe aquí la medida o modelo:").strip().upper()

    if busqueda:
        # Filtra en ambas columnas (Medida y Descripción)
        filtro = (
            df['Medida'].str.contains(busqueda, case=False, na=False) | 
            df['Descripción del artículo'].str.contains(busqueda, case=False, na=False)
        )
        resultados = df[filtro]

        if not resultados.empty:
            # Estilo de colores para la columna Stock
            def color_stock(val):
                color = "#035817" if val == "Hay Stock" else "#0c08e9" if val == "Consultar" else "#d61d1d"
                return f'background-color: {color}'

            # Mostrar tabla
            st.dataframe(
                resultados.style.applymap(color_stock, subset=['Stock']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No se encontraron coincidencias.")