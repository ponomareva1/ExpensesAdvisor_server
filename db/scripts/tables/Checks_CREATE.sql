-- Table: public."Checks"

-- DROP TABLE public."Checks";

CREATE TABLE public."Checks"
(
    id bigint NOT NULL DEFAULT nextval('"Checks_id_seq"'::regclass),
    specifier text COLLATE pg_catalog."default" NOT NULL,
    shop text COLLATE pg_catalog."default" NOT NULL,
    date date NOT NULL,
    id_user bigint NOT NULL,
    CONSTRAINT "Checks_pkey" PRIMARY KEY (id),
    CONSTRAINT user_fkey FOREIGN KEY (id_user)
        REFERENCES public."Users" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Checks"
    OWNER to postgres;