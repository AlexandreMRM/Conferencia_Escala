import pandas as pd
import mysql.connector
import streamlit as st



@st.cache_data(ttl=600, show_spinner=False)
def BD_Escala(data_ini=None, data_fim=None):
    # Parametros de Login AWS
    config = {
    'user': 'user_automation_jpa',
    'password': 'luck_jpa_2024',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_joao_pessoa'
    }
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()

    query = '''
        SELECT 
            `Tipo de Servico`,
            `Data | Horario Apresentacao`,
            `Data Execucao`,
            COALESCE(NULLIF(`Voo`, ''), '-') AS `Voo`,
            `Est. Origem`,
            `Est. Destino`,
            `Reserva`,
            `Parceiro`,
            `Total ADT`,
            `Total CHD`,
            `Observacao`,
            `Escala`,
            `Veiculo`,
            `Motorista`,
            `Guia`,
            `Fornecedor Motorista`,
            `Cliente`,
            `Telefone Cliente`,
            `Servico`,
            `Apoio`,
            CASE
                WHEN `Tipo de Servico` = 'IN' THEN `Est. Destino`
                ELSE `Est. Origem`
            END AS `Estabelecimento`
        FROM vw_payment_guide
    '''
    if data_ini and data_fim:
        query += " WHERE `Data | Horario Apresentacao` BETWEEN %s AND %s"
        cursor.execute(query, (data_ini, data_fim))
    else:
        cursor.execute(query)
        
    # Coloca o request em uma variavel
    resultado = cursor.fetchall()
    # Busca apenas o cabecalhos do Banco
    cabecalho = [desc[0] for desc in cursor.description]

    # Fecha a conexão
    cursor.close()
    conexao.close()

    # Coloca em um dataframe e muda o tipo de decimal para float
    df = pd.DataFrame(resultado, columns=cabecalho)
    df['Data | Horario Apresentacao'] = pd.to_datetime(df['Data | Horario Apresentacao'], format='%Y-%m-%d', errors='coerce')
    df['Data Escala'] = df['Data | Horario Apresentacao']
    df['Data Escala'] = pd.to_datetime(df['Data Escala'], errors='coerce').dt.normalize()
    return df


# Function to split 'Apoio' and map values to the new columns
def split_apoio_data(row):
    if pd.notna(row['Apoio']):
        parts = row['Apoio'].split(',')
        return pd.Series({
            'Escala Auxiliar': parts[0].strip() if len(parts) > 0 else None,
            'Veiculo': parts[1].strip() if len(parts) > 1 else None,
            'Motorista': parts[2].strip() if len(parts) > 2 else None,
            'Guia': parts[3].strip() if len(parts) > 3 else None,
            'Data | Horario Apresentacao': row['Data | Horario Apresentacao'],
            'Servico': f'APOIO - '+ row['Servico'],
            'Reserva': row['Reserva'],
            'Voo': row['Voo'],
            'Parceiro': row['Parceiro'],
            'Total ADT': row['Total ADT'],
            'Total CHD': row['Total CHD'],
            'Observacao': row['Observacao'],
            'Estabelecimento': row['Estabelecimento'],
            'Cliente': row['Cliente'],
            'Telefone Cliente': row['Telefone Cliente'],
            'Data Execucao': row['Data Execucao']
        })
    else:
        # Return None for rows without 'Apoio' data to filter them out later
        return pd.Series({
            'Escala Auxiliar': None,
            'Veiculo': None,
            'Motorista': None,
            'Guia': None,
            'Data | Horario Apresentacao': row['Data | Horario Apresentacao'],
            'Servico': row['Servico'],
            'Reserva': row['Reserva'],
            'Voo': row['Voo'],
            'Parceiro': row['Parceiro'],
            'Total ADT': row['Total ADT'],
            'Total CHD': row['Total CHD'],
            'Observacao': row['Observacao'],
            'Estabelecimento': row['Estabelecimento'],
            'Cliente': row['Cliente'],
            'Telefone Cliente': row['Telefone Cliente'],
            'Data Execucao': row['Data Execucao']
        })


