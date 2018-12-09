-- Table: public."Categories"

-- DROP TABLE public."Categories";

CREATE TABLE public."Categories"
(
    id bigint NOT NULL DEFAULT nextval('"Categories_id_seq"'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Categories_pkey" PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Categories"
    OWNER to postgres;