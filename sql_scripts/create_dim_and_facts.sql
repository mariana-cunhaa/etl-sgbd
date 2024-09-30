CREATE TABLE dim_tempo (
	dim_tempo_id SERIAL primary key,
	ano int NULL
);


CREATE TABLE dim_nome_programa (
	dim_nome_programa_id SERIAL primary key,
	codigo_programa text NULL,
	programa_fomento text NULL
);


CREATE TABLE dim_localidade (
	dim_localidade_id SERIAL primary key,
	uf text NULL,
	municipio text NULL,
	regiao text NULL
);

CREATE TABLE dim_instituicao (
	dim_instituicao_id SERIAL primary key,
	status_juridico text NULL,
	ies text NULL
);

CREATE TABLE dim_nivel_estudo(
	dim_nivel_estudo_id SERIAL primary key,
	programa_fomento text null,
	iniciacao_cientifica text null,
	mestrado text NULL,
	doutorado_pleno text NULL, 
    pos_doutorado text NULL
);

CREATE TABLE dim_programa(
	dim_programa_id SERIAL primary key,
	programa_fomento text NULL,
	tipo text NULL
);

CREATE TABLE dim_area (
	dim_area_id SERIAL primary key,
	area_avaliacao text NULL,
	area_conhecimento text NULL,
	grande_area text NULL
);

CREATE TABLE ft_media_vl_bolsas (
    dim_tempo_id INTEGER,
    dim_nome_programa_id INTEGER,
    dim_area_id INTEGER,
    dim_instituicao_id INTEGER,
    qtd_medio_bolsa DECIMAL(10,2),
    FOREIGN KEY (dim_tempo_id) REFERENCES dim_tempo(dim_tempo_id),
    FOREIGN KEY (dim_nome_programa_id) REFERENCES dim_nome_programa(dim_nome_programa_id),
    FOREIGN KEY (dim_area_id) REFERENCES dim_area(dim_area_id),
    FOREIGN KEY (dim_instituicao_id) REFERENCES dim_instituicao(dim_instituicao_id)
);


