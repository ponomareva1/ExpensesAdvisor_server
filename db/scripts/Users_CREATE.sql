-- Table: public."Users"

-- DROP TABLE public."Users";

CREATE TABLE public."Users"
(
    id bigint NOT NULL DEFAULT nextval('"Users_id_seq"'::regclass),
    login text COLLATE pg_catalog."default" NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Users_pkey" PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Users"
    OWNER to postgres;