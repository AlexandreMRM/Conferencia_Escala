import pandas as pd
import streamlit as st
from weasyprint import HTML
from bbtc import BD_Escala, split_apoio_data

st.set_page_config(layout='wide')

if 'lista_dataframes_pdf' not in st.session_state:
    st.session_state['lista_dataframes_pdf'] = []

if 'pesquisa_dupla' not in st.session_state:
    st.session_state['pesquisa_dupla'] = None

if 'mostrar_resultados' not in st.session_state:
    st.session_state['mostrar_resultados'] = False
    

def main():
    st.title('Impressão de Ordens de Serviços')
    #Esconder a Navegação   
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
            data_ini = st.date_input('Data da Escala', value=pd.Timestamp.today().date(), format='DD/MM/YYYY', key='data_ini_2')
            data_fim = data_ini + pd.Timedelta(days=2)
            
            with st.spinner('Carregando dados do Phoenix...'):
                st.session_state.df = BD_Escala(data_ini, data_fim)
            df = st.session_state.df
            
            ######
            lista_motorista = df['Motorista'].dropna().unique().tolist()
            lista_motorista.sort()
            lista_guia = df['Guia'].dropna().unique().tolist()
            lista_guia.sort()
            lista_os = df['Escala'].dropna().unique().tolist()
            lista_os.sort()

            #lista_dataframes_pdf = None

            #########
            tipo_impressao = st.radio('Selecione o Modo de Impressão', ['Motorista', 'Guia', 'Ordem de Serviço', 'Todos'])
            # Agrupando todos as colunas de datas para responderem pelo input de data
            data_ini = pd.to_datetime(data_ini)
            df_filtrado = df[
                (df['Data Escala'] == data_ini)
            ]

            # Applying the function to df_filtrado and dropping rows without 'Apoio' data
            df_apoio = df_filtrado.apply(split_apoio_data, axis=1).dropna(subset=['Escala Auxiliar'])
            # Removing the suffixes from the specific columns
            df_apoio['Escala Auxiliar'] = df_apoio['Escala Auxiliar'].str.replace("Escala Auxiliar: ", "", regex=False)
            df_apoio['Veiculo'] = df_apoio['Veiculo'].str.replace("Veículo: ", "", regex=False)
            df_apoio['Motorista'] = df_apoio['Motorista'].str.replace("Motorista: ", "", regex=False)
            df_apoio['Guia'] = df_apoio['Guia'].str.replace("Guia: ", "", regex=False)
            
            df_apoio = df_apoio.rename(columns={'Escala Auxiliar': 'Escala'})

            df_filtrado = df_filtrado[['Escala', 'Veiculo', 'Motorista', 'Data Execucao', 'Guia', 'Data | Horario Apresentacao', 'Servico', 'Voo', 'Reserva', 'Parceiro', 'Total ADT', 'Total CHD', 'Observacao', 'Estabelecimento', 'Cliente', 'Telefone Cliente', 'Apoio']]
            df_ordem = pd.concat([df_apoio, df_filtrado], ignore_index=True)
            
            df_ordem['Data Execucao'] = pd.to_datetime(df_ordem['Data Execucao'], format='%d/%m/%Y')
            df_ordem['Data Execucao'] = df_ordem['Data Execucao'].dt.strftime('%d/%m/%Y')

            # Agrupar os dados pelo valor da coluna 'Escala' e criar uma lista de DataFrames
            lista_dataframes = [grupo for _, grupo in df_ordem.groupby('Escala')]
            df_filtro_os = lista_dataframes.copy()
            
            if tipo_impressao == 'Motorista':
                filtro_motorista = st.selectbox('Motorista', lista_motorista, index=None, key='select001')
                if st.button('Pesquisar', key='botao001'):
                    st.session_state['lista_dataframes_pdf'] = []
                    if st.session_state['pesquisa_dupla'] != filtro_motorista:
                        df_filtro_motorista = [df for df in lista_dataframes if (df['Motorista'] == filtro_motorista).any()]
                        st.session_state['lista_dataframes_pdf'] = df_filtro_motorista   
                        st.session_state['pesquisa_dupla'] = filtro_motorista 
                        st.session_state['mostrar_resultados'] = True
                
                if st.session_state['mostrar_resultados']:
                    if st.session_state['lista_dataframes_pdf']:
                        for idx, df_filtro_motorista in enumerate(st.session_state['lista_dataframes_pdf']):
                            
                            guia = df_filtro_motorista['Guia'].iloc[0]
                            motorista = df_filtro_motorista['Motorista'].iloc[0]
                            veiculo = df_filtro_motorista['Veiculo'].iloc[0]
                            data_execucao = df_filtro_motorista['Data Execucao'].iloc[0]
                            servico = df_filtro_motorista['Servico'].iloc[0]
                            escala = df_filtro_motorista['Escala'].iloc[0]
                            total_paxs = df_filtro_motorista['Total ADT'].sum() + df_filtro_motorista['Total CHD'].sum()
                            df_filtro_motorista.sort_values(by='Data | Horario Apresentacao', ascending=True, inplace=True)
                            df_filtro_motorista['Horario'] = df_filtro_motorista['Data | Horario Apresentacao'].dt.strftime('%H:%M')
                            with col2: 
                                st.write(f"Data Execução: {data_execucao} - Servico: {servico} - Ordem de Servico - {escala}")
                                st.write(f"Motorista: {motorista} - Guia: {guia} - Veiculo: {veiculo} - Total Escalado: {total_paxs}")
                                st.dataframe(df_filtro_motorista[['Reserva', 'Horario', 'Voo', 'Estabelecimento', 'Cliente', 'Telefone Cliente', 'Total ADT', 'Total CHD', 'Observacao', 'Apoio']], hide_index=True, use_container_width=True)
                                st.divider()
                    st.session_state['mostrar_resultados'] = False

            if tipo_impressao == 'Guia':
                filtro_guia = st.selectbox('Guia', lista_guia, index=None, key='select002')
                if st.button('Pesquisar', key='botao001'):
                    st.session_state['lista_dataframes_pdf'] = []
                    if st.session_state['pesquisa_dupla'] != filtro_guia:
                        df_filtro_guia = [df for df in lista_dataframes if df['Guia'].str.contains(filtro_guia).any()]
                        st.session_state['lista_dataframes_pdf'] = df_filtro_guia
                        st.session_state['pesquisa_dupla'] = filtro_guia
                        st.session_state['mostrar_resultados'] = True

                if st.session_state['mostrar_resultados']:
                    if st.session_state['lista_dataframes_pdf']:
                        for idx, df_filtro_guia in enumerate(st.session_state['lista_dataframes_pdf']):
                            guia = df_filtro_guia['Guia'].iloc[0]
                            motorista = df_filtro_guia['Motorista'].iloc[0]
                            veiculo = df_filtro_guia['Veiculo'].iloc[0]
                            data_execucao = df_filtro_guia['Data Execucao'].iloc[0]
                            servico = df_filtro_guia['Servico'].iloc[0]
                            escala = df_filtro_guia['Escala'].iloc[0]
                            total_paxs = df_filtro_guia['Total ADT'].sum() + df_filtro_guia['Total CHD'].sum()
                            df_filtro_guia.sort_values(by='Data | Horario Apresentacao', ascending=True, inplace=True)
                            df_filtro_guia['Horario'] = df_filtro_guia['Data | Horario Apresentacao'].dt.strftime('%H:%M')
                            with col2: 
                                st.write(f"Data Execução: {data_execucao} - Servico: {servico} - Ordem de Servico - {escala}")
                                st.write(f"Motorista: {motorista} - Guia: {guia} - Veiculo: {veiculo} - Total Escalado: {total_paxs}")
                                st.dataframe(df_filtro_guia[['Reserva', 'Horario', 'Voo', 'Estabelecimento', 'Cliente', 'Telefone Cliente', 'Total ADT', 'Total CHD', 'Observacao', 'Apoio']], hide_index=True, use_container_width=True)
                                st.divider()
                    st.session_state['mostrar_resultados'] = False
                
            if tipo_impressao == 'Ordem de Serviço':
                filtro_os = st.selectbox('Ordem de Serviço', lista_os, index=None, key='select003')
                if st.button('Pesquisar', key='botao001'):
                    st.session_state['lista_dataframes_pdf'] = []
                    if st.session_state['pesquisa_dupla'] != filtro_os:
                        df_filtro_os = [df for df in lista_dataframes if df['Escala'].str.contains(filtro_os).any()]
                        st.session_state['lista_dataframes_pdf'] = df_filtro_os
                        st.session_state['pesquisa_dupla'] = filtro_os
                        st.session_state['mostrar_resultados'] = True

                if st.session_state['mostrar_resultados']:
                    if st.session_state['lista_dataframes_pdf']:
                        for idx, df_filtro_os in enumerate(st.session_state['lista_dataframes_pdf']):
                            guia = df_filtro_os['Guia'].iloc[0]
                            motorista = df_filtro_os['Motorista'].iloc[0]
                            veiculo = df_filtro_os['Veiculo'].iloc[0]
                            data_execucao = df_filtro_os['Data Execucao'].iloc[0]
                            servico = df_filtro_os['Servico'].iloc[0]
                            escala = df_filtro_os['Escala'].iloc[0]
                            total_paxs = df_filtro_os['Total ADT'].sum() + df_filtro_os['Total CHD'].sum()
                            df_filtro_os.sort_values(by='Data | Horario Apresentacao', ascending=True, inplace=True)
                            df_filtro_os['Horario'] = df_filtro_os['Data | Horario Apresentacao'].dt.strftime('%H:%M')
                            with col2:
                                st.write(f"Data Execução: {data_execucao} - Servico: {servico} - Ordem de Servico - {escala}")
                                st.write(f"Motorista: {motorista} - Guia: {guia} - Veiculo: {veiculo} - Total Escalado: {total_paxs}")
                                st.dataframe(df_filtro_os[['Reserva', 'Horario', 'Voo', 'Estabelecimento', 'Cliente', 'Telefone Cliente', 'Total ADT', 'Total CHD', 'Observacao', 'Apoio']], hide_index=True, use_container_width=True)
                                st.divider()
                    st.session_state['mostrar_resultados'] = False

            if tipo_impressao == 'Todos':
                if st.button('Pesquisar', key='botao001'):
                    st.session_state['lista_dataframes_pdf'] = []
                    st.session_state['lista_dataframes_pdf'] = df_filtro_os
                    st.session_state['mostrar_resultados'] = True
                
                if st.session_state['mostrar_resultados']:
                    if st.session_state['lista_dataframes_pdf']:
                        for idx, df in enumerate(st.session_state['lista_dataframes_pdf']):
                            #lista_dataframes_pdf = df_filtro_os.copy()
                            guia = df['Guia'].iloc[0]
                            motorista = df['Motorista'].iloc[0]
                            veiculo = df['Veiculo'].iloc[0]
                            data_execucao = df['Data Execucao'].iloc[0]
                            servico = df['Servico'].iloc[0]
                            escala = df['Escala'].iloc[0]
                            total_paxs = df['Total ADT'].sum() + df['Total CHD'].sum()
                            df.sort_values(by='Data | Horario Apresentacao', ascending=True, inplace=True)
                            df['Horario'] = df['Data | Horario Apresentacao'].dt.strftime('%H:%M')
                            with col2:
                                st.write(f"Data Execução: {data_execucao} - Servico: {servico} - Ordem de Servico - {escala}")
                                st.write(f"Motorista: {motorista} - Guia: {guia} - Veiculo: {veiculo} - Total Escalado: {total_paxs}")                           
                                st.dataframe(df[['Reserva', 'Horario', 'Voo', 'Estabelecimento', 'Cliente', 'Telefone Cliente', 'Total ADT', 'Total CHD', 'Observacao', 'Apoio']], hide_index=True, use_container_width=True)
                                st.divider()
                    st.session_state['mostrar_resultados'] = False



        html_content = """
            <!DOCTYPE html>
            <html lang="pt-br">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ordens de Serviço</title>
            <style>
            body { font-family: Calibri, sans-serif; margin: 20px; font-size: 12px;}
            h2 { color: #333; font-size: 16px; background-color: #bdbbbb; border: 1px solid #000;}
            table { 
                border-collapse: collapse; 
                width: 100%; 
                text-align: center; 
            }
            th, td {
                border: 1px solid #000; 
                padding: 8px; 
                text-align: center; 
            }
            th { 
                background-color: #f4f4f4; 
            }
            tr:nth-child(even) { 
                background-color: #f9f9f9; 
            }
            tr:hover { 
                background-color: #f1f1f1; 
            }
            table.dataframe {
                margin-bottom: 50px; /* Espaçamento entre tabelas */
            }
            .spacer {
                height: 30px; /* Espaçamento entre tabelas */
            }
            
            @media print {
            @page {
                size: A4 landscape; /* Orientação horizontal */
                margin: 10mm;
                }
            }
            </style>
            </head>
            <body>
            """
        if 'botao_baixar' not in st.session_state:
            st.session_state['botao_baixar'] = False
            
        lista_dataframes_pdf = []
        if st.session_state['lista_dataframes_pdf'] is None or not st.session_state['lista_dataframes_pdf']:
            with col2:
                st.warning('Selecione o Filtro de Pesquisa, ou Pesquise SEM FILTRO para Todas as Ordens')
        else:
            lista_dataframes_pdf = st.session_state['lista_dataframes_pdf']
            with col2:
                botao_baixar = st.button('Gerar PDF', key='botao002')
            st.session_state['botao_baixar'] = botao_baixar
            if all (df.empty for df in lista_dataframes_pdf):
                st.warning('Nenhum dado inserido na OS')

        for item in lista_dataframes_pdf:
            if isinstance(item, pd.DataFrame):
                item = item.rename(columns={"Estabelecimento": "Estabelecimento", 'Telefone Cliente': "Telefone_Cliente", "Total ADT": "Adulto", "Total CHD": "Criança"})
                nome_motorista = item['Motorista'].iloc[0]
                nome_guia = item['Guia'].iloc[0]
                nome_veiculo = item['Veiculo'].iloc[0]
                data_execucao = item['Data Execucao'].iloc[0]
                servico = item['Servico'].iloc[0]
                escala = item['Escala'].iloc[0]
                total_paxs = item['Adulto'].sum() + item['Criança'].sum()
                df_impressao = item[['Reserva', 'Horario', 'Voo', 'Estabelecimento', 'Cliente', 'Telefone_Cliente', 'Adulto', 'Criança', 'Observacao', 'Apoio']]

                html_content += '<div class="table-container">'
                html_content += '<br>'  
                html_content += f'<h2>Motorista: {nome_motorista} - Guia: {nome_guia} - Veículo: {nome_veiculo} - Total Escalado: {total_paxs}</h2>'
                html_content += f'<h2 style="font-size:12px;"> Data Execução: {data_execucao} - Servico: {servico} - Ordem de Servico - {escala}</h2>'
                html_content += '<br><br>'

                lista = []  # Lista para armazenar os dados formatados

                for row in df_impressao.itertuples(index=False):
                    lista.append(f'<tr>'
                    f'<td>{row.Horario}</td>'
                    f'<td>{row.Reserva}</td>'
                    f'<td>{row.Estabelecimento}</td>'
                    f'<td>{row.Voo}</td>'
                    f'<td>{row.Cliente}</td>'
                    f'<td>{row.Telefone_Cliente}</td>'
                    f'<td>{row.Adulto}</td>'
                    f'<td>{row.Criança}</td>'
                    f'</tr>')
                    if row.Observacao.strip():  # Se houver observação, adiciona uma linha extra
                        lista.append(f'<tr><td colspan="8" style="text-align: left; font-size: 8px;"><b>Obs: {row.Observacao}</b></td></tr>')
                    if pd.notna(row.Apoio) and str(row.Apoio).strip():
                        lista.append(f'<tr><td colspan="8" style="text-align: left; font-size: 8px;"><b>Apoio {row.Apoio}</b></td></tr>')

                # Criando uma tabela HTML para exibir os dados corretamente
                html_content += ('<table border="1">'
                        '<tr>'
                        '<th>Horário</th>'
                        '<th>Reserva</th>'
                        '<th>Estabelecimento</th>'
                        '<th>Voo</th>'
                        '<th>Cliente</th>'
                        '<th>Telefone Cliente</th>'
                        '<th>Adulto</th>'
                        '<th>Criança</th>'
                        '</tr>')
                html_content += "".join(lista)  # Concatena os elementos da lista como string
                html_content += '</table>'

                html_content += '</div>'
                html_content += '<div style="page-break-after: always;"></div>'


        html_content += """
        </body>
        </html>
        """
    with col2:
        if st.session_state['botao_baixar']:
            with open('ordemdeservico.html', 'w', encoding='utf-8') as f:
                f.write(html_content)

                pdf_path = "ordens_de_servico.pdf"
                HTML(string=html_content).write_pdf(pdf_path)

                st.success(f"PDF gerado: {pdf_path}")

                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    st.download_button(
                        label="Baixar PDF",
                        data=pdf_bytes,
                        file_name="ordens_de_servico.pdf",
                        mime="application/pdf"
                    )
                        
                

if __name__ == '__main__':
    main()
