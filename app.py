import streamlit as st
import pages.main_conf as main_conf
import pages.main_os as main_os


#st.set_page_config(layout='wide')


# CSS DEFINITIVO para esconder a navegação
hide_menu_style = """
    <style>
        /* Ocultar barra lateral completa */
        [data-testid="stSidebar"] {
            display: none;
        }
        /* Ocultar Seta (SVG) da Navegação Lateral */
        svg[class*="st-emotion-cache"] {
            display: none;
            visibility: hidden;
        }
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)


# Ler o parâmetro da URL e normalizar
query_params = st.query_params
app = query_params.get('app', [''])[0].strip().lower()

# Redirecionamento para a página correspondente
if app == 'conferencia':
    from pages.main_conf import main as conferencia_main
    conferencia_main()
elif app == 'ordens_servico':
    from pages.main_os import main as ordens_servico_main
    ordens_servico_main()

