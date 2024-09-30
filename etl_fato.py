import pandas as pd
from sqlalchemy import create_engine, text

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

def etl_ft_media_qtd_bolsas(df, dw_engine):
    # Itera sobre o DataFrame
    with dw_engine.connect() as connection:
    # Itera sobre o DataFrame
    #foi 145515
        for index, row in df.iterrows():
            print(index)
            query = """
                INSERT INTO public.ft_media_vl_bolsas
                (dim_tempo_id, dim_nome_programa_id, dim_area_id, dim_instituicao_id, qtd_medio_bolsa)
                SELECT DISTINCT
                    dt.dim_tempo_id,
                    dnp.dim_nome_programa_id,
                    da.dim_area_id,
                    di.dim_instituicao_id,
                    :qt_bolsas as qtd_medio_bolsa -- Parâmetro que vai ser substituido
                FROM dim_tempo dt,
                    dim_nome_programa dnp,
                    dim_area da,
                    dim_instituicao di
                WHERE dt.ano = :ano
                AND dnp.codigo_programa = :codigo_programa
                AND da.area_avaliacao = :area_avaliacao
                AND da.area_conhecimento = :area_conhecimento
                AND da.grande_area = :grande_area
                AND di.ies = :ies;
                """
                
            qt_bolsas = row[['doutorado_pleno', 'doutorado_profissional', 'iniciacao_cientifica', 
                    'jovens_talentos_a', 'jovens_talentos_b', 'mestrado', 'mestrado_profissional',
                    'pesquisador_visitante_especial', 'prof_visitante_nacional_senior', 
                    'professor_visitante_exterior_pleno', 'professor_visitante_exterior_senior',
                    'pos_doutorado']].fillna(0).sum()


            # Executa a query passando os valores da linha como parâmetros
            # Linha por linha e executa um script passando esses parâmetros
            connection.execute(
                    text(query),
                    {
                        'ano': row['ano'],
                        'codigo_programa': row['codigo_programa'],
                        'area_avaliacao': row['area_avaliacao'],
                        'area_conhecimento': row['area_conhecimento'],
                        'grande_area': row['grande_area'],
                        'ies': row['ies'],
                        'qt_bolsas': int(qt_bolsas)
                    }
                )    


if __name__ == "__main__":
    try:
        # Conexão com o banco de dados intermediário
        intermediate_engine = create_engine_with_retry('postgresql+psycopg2://postgres:123@localhost:5432/banco_intermediario')
        
        # Conexão com o banco de dados dw
        dw_engine = create_engine_with_retry('postgresql+psycopg2://postgres:123@localhost:5432/dw_capes_bolsas')
        
        # Extrair dados do banco intermediário
        df = extract_data(intermediate_engine)
        etl_ft_media_qtd_bolsas(df, dw_engine)
    
    except Exception as e:
        print(f"Ocorreu um erro durante a execução do script: {e}")
    
    finally:
        if 'intermediate_engine' in locals():
            intermediate_engine.dispose()
        if 'dw_engine' in locals():
            dw_engine.dispose()
        print("Script finalizado.")