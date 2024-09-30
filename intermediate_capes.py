import pandas as pd
from sqlalchemy import create_engine, inspect

def extract_data():
    df = pd.read_csv("capes-bolsas-dataset.csv")
    
    df.columns = [
        "ano", "uf", "municipio", "regiao", "codigo_programa", "programa_fomento", 
        "ies", "status_juridico", "programa", "area_avaliacao", "area_conhecimento", 
        "grande_area", "codigo_ies", "doutorado_pleno", "doutorado_profissional", 
        "iniciacao_cientifica", "jovens_talentos_a", "jovens_talentos_b", "mestrado", 
        "mestrado_profissional", "pesquisador_visitante_especial", 
        "prof_visitante_nacional_senior", "professor_visitante_exterior_pleno", 
        "professor_visitante_exterior_senior", "pos_doutorado", "total_linha"
    ]
    
    return df

def load_to_intermediate(df, engine):
    df.to_sql('capes_bolsas', con=engine, if_exists='append', index=False)
    print("Dados carregados com sucesso na tabela 'capes_bolsas'.")

def create_engine_with_retry(max_retries=3):
    for attempt in range(max_retries):
        try:
            engine = create_engine('postgresql+psycopg2://postgres:123@localhost:5432/banco_intermediario')
            engine.connect()
            return engine
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Tentativa {attempt + 1} falhou. Tentando novamente...")
            else:
                raise Exception(f"Falha ao conectar ao banco de dados após {max_retries} tentativas: {str(e)}")

if __name__ == "__main__":
    try:
        # Criando a conexão com o banco de dados
        engine = create_engine_with_retry()
        
        # Criando um inspetor para verificar a existência da tabela
        inspector = inspect(engine)
        
        # Nome da tabela
        table_name = 'capes_bolsas'
        
        # Verificando se a tabela já existe e possui dados
        if not inspector.has_table(table_name) or pd.read_sql_table(table_name, con=engine).empty:
            df = extract_data()
            load_to_intermediate(df, engine)
        else:
            print(f"A tabela '{table_name}' já existe e contém dados. Nenhuma ação foi executada.")
    
    except Exception as e:
        print(f"Ocorreu um erro durante a execução do script: {str(e)}")
    
    finally:
        if 'engine' in locals():
            engine.dispose()
        print("Script finalizado.")