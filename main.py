import pandas as pd
import streamlit as st
from bbtc import BD_Escala, split_apoio_data

st.set_page_config(layout='wide')
with st.spinner('Carregando dados do Phoenix...'):
    st.session_state.df = BD_Escala()
df = st.session_state.df

st.title('Conferência de Escala')
st.markdown("""
            <style>
            .stApp{
                background-color: #047c6c;
            }
            h1{
                font-size: 30pt;
                color: #d17d7f;

            h2, h3, .stMarkdown, .stRadio label, .stSelectbox label{
                font-size: 10pt;
                color: #74c4bc;
            }
            .stDateInput label {
                font-size: 20pt;
                color: #74c4bc;
            }
            <style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 7.5])

with col1:
    with st.container():
        data_ini = st.date_input('Data da Escala', value=pd.Timestamp.today().date(), format='DD/MM/YYYY', key='data_ini_1')
    
        # Agrupando todos as colunas de datas para responderem pelo input de data
        data_ini = pd.to_datetime(data_ini)
        df_filtrado = df[
            (df['Data Escala'] == data_ini)
        ]

        with col2:
            # Applying the function to df_filtrado and dropping rows without 'Apoio' data
            df_apoio = df_filtrado.apply(split_apoio_data, axis=1).dropna(subset=['Escala Auxiliar'])
            # Removing the suffixes from the specific columns
            df_apoio['Escala Auxiliar'] = df_apoio['Escala Auxiliar'].str.replace("Escala Auxiliar: ", "", regex=False)
            df_apoio['Veiculo'] = df_apoio['Veiculo'].str.replace("Veículo: ", "", regex=False)
            df_apoio['Motorista'] = df_apoio['Motorista'].str.replace("Motorista: ", "", regex=False)
            df_apoio['Guia'] = df_apoio['Guia'].str.replace("Guia: ", "", regex=False)

            df_apoio = df_apoio.rename(columns={'Escala Auxiliar': 'Escala'})

            df_geral = df_filtrado.groupby(['Escala'], as_index=False).agg({
                'Data | Horario Apresentacao': 'first',
                'Veiculo': 'first',
                'Motorista': 'first',
                'Guia': 'first',
                'Servico': 'first'
            })

            df_escala = pd.concat([df_apoio, df_geral], ignore_index=True)

            df_escala = df_escala.groupby('Escala').agg({
                'Data | Horario Apresentacao': 'min',
                'Veiculo': 'first',
                'Motorista': 'first',
                'Guia': 'first',
                'Servico': 'first'
            }).reset_index()

            df_escala = df_escala.sort_values(by='Data | Horario Apresentacao', ascending=True).reset_index(drop=True)

            df_escala['Data | Horario Apresentacao'] = df_escala['Data | Horario Apresentacao'].dt.strftime('%H:%M')
            df_escala = df_escala.rename(columns={'Data | Horario Apresentacao': 'Hora'})
            st.dataframe(df_escala, height=1200, hide_index=True, use_container_width=True)
