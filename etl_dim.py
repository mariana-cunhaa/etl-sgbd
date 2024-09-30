import pandas as pd
from sqlalchemy import create_engine

def create_engine_with_retry(connection_string, max_retries=3):
    for attempt in range(max_retries):
        try:
            engine = create_engine(connection_string)
            engine.connect()
            return engine
        except Exception as e:
            print(f"Tentativa {attempt + 1} falhou: {str(e)}")
            if attempt < max_retries - 1:
                print("Tentando novamente...")
            else:
                raise Exception(f"Falha ao conectar ao banco de dados após {max_retries} tentativas: {str(e)}")

def extract_data(engine):
    query = "SELECT * FROM capes_bolsas"
    df = pd.read_sql(query, engine)
    return df

# Populando as dimensões
def etl_dim_tempo(df, dw_engine):
    dim_tempo = df[['ano']].drop_duplicates().reset_index(drop=True)
    
    try:
        dim_tempo.to_sql('dim_tempo', con=dw_engine, index=False, if_exists='append')
        print("Dados inseridos com sucesso na tabela dim_tempo.")
    except Exception as e:
        print(f"Erro ao inserir dados na tabela dim_tempo: {e}")

def etl_nome_programa(df, dw_engine):
    dim_nome_programa = df[['programa_fomento', 'codigo_programa']].drop_duplicates().reset_index(drop=True)
    
    try:
        dim_nome_programa.to_sql('dim_nome_programa', con=dw_engine, index=False, if_exists='append')
        print("Dados inseridos com sucesso na tabela dim_nome_programa.")
    except Exception as e:
        print(f"Erro ao inserir dados na tabela dim_nome_programa: {e}")

def etl_dim_localidade(df, dw_engine):
    dim_localidade = df[['regiao', 'uf', 'municipio']].drop_duplicates().reset_index(drop=True)
    
    try:
        dim_localidade.to_sql('dim_localidade', con=dw_engine, index=False, if_exists='append')
        print("Dados inseridos com sucesso na tabela dim_localidade.")
    except Exception as e:
        print(f"Erro ao inserir dados na tabela dim_localidade: {e}")

def etl_dim_instituicao(df, dw_engine):
    dim_instituicao = df[['ies', 'status_juridico']].drop_duplicates().reset_index(drop=True)
    
    try:
        dim_instituicao.to_sql('dim_instituicao', con=dw_engine, index=False, if_exists='append')
        print("Dados inseridos com sucesso na tabela dim_instituicao.")
    except Exception as e:
        print(f"Erro ao inserir dados na tabela dim_instituicao: {e}")

def etl_dim_nivel_estudo(df, dw_engine):
    
    df['iniciacao_cientifica'] = df.apply(lambda row: 'sim' if row['iniciacao_cientifica'] > 0 else 'nao', axis=1)
    df['mestrado'] = df.apply(lambda row: 'sim' if row['mestrado'] > 0 else 'nao', axis=1)
    df['doutorado_pleno'] = df.apply(lambda row: 'sim' if row['doutorado_pleno'] > 0 else 'nao', axis=1)
    df['pos_doutorado'] = df.apply(lambda row: 'sim' if row['pos_doutorado'] > 0 else 'nao', axis=1)

    
    dim_nivel_estudo = df[['programa_fomento', 'iniciacao_cientifica', 'mestrado', 'doutorado_pleno', 'pos_doutorado']].drop_duplicates().reset_index(drop=True)

    try:
        dim_nivel_estudo.to_sql('dim_nivel_estudo', con=dw_engine, index=False, if_exists='append')
        print("Dados inseridos com sucesso na tabela dim_nivel_estudo.")
    except Exception as e:
        print(f"Erro ao inserir dados na tabela dim_nivel_estudo: {e}")

def etl_dim_programa(df, dw_engine):

    tipos = ['mestrado', 'mestrado_profissional', 'doutorado_pleno', 'doutorado_profissional']
    
    expanded_rows = []
    
    # Iterar sobre as linhas do DataFrame original
    for _, row in df.iterrows():
        for tipo in tipos:
            if row[tipo] > 0:
                new_row = {
                    'programa_fomento': row['programa_fomento'],
                    'tipo': tipo
                }
                expanded_rows.append(new_row)

    dim_programa = pd.DataFrame(expanded_rows)
    
    dim_programa = dim_programa[['programa_fomento', 'tipo']].drop_duplicates().reset_index(drop=True)

    try:
        dim_programa.to_sql('dim_programa', con=dw_engine, index=False, if_exists='append')
        print("Dados inseridos com sucesso na tabela dim_programa.")
    except Exception as e:
        print(f"Erro ao inserir dados na tabela dim_programa: {e}")
        
def etl_dim_area(df, dw_engine):
    dim_area = df[['area_avaliacao', 'area_conhecimento', 'grande_area']].drop_duplicates().reset_index(drop=True)
    
    try:
        dim_area.to_sql('dim_area', con=dw_engine, index=False, if_exists='append')
        print("Dados inseridos com sucesso na tabela dim_area.")
    except Exception as e:
        print(f"Erro ao inserir dados na tabela dim_area: {e}")

if __name__ == "__main__":
    try:
        # Conexão com o banco de dados intermediário
        intermediate_engine = create_engine_with_retry('postgresql+psycopg2://postgres:123@localhost:5432/banco_intermediario')
        
        # Conexão com o banco de dados dw
        dw_engine = create_engine_with_retry('postgresql+psycopg2://postgres:123@localhost:5432/dw_capes_bolsas')
        
        # Extrair dados do banco intermediário
        df = extract_data(intermediate_engine)
        # etl_dim_tempo(df, dw_engine)
        # etl_nome_programa(df, dw_engine)
        # etl_dim_localidade(df, dw_engine)
        # etl_dim_instituicao(df, dw_engine)
        # etl_dim_nivel_estudo(df, dw_engine)
        # etl_dim_programa(df, dw_engine)
        # etl_dim_area(df, dw_engine)
    
    except Exception as e:
        print(f"Ocorreu um erro durante a execução do script: {e}")
    
    finally:
        if 'intermediate_engine' in locals():
            intermediate_engine.dispose()
        if 'dw_engine' in locals():
            dw_engine.dispose()
        print("Script finalizado.")
