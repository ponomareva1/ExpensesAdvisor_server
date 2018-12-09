-- Table: public."Items"

-- DROP TABLE public."Items";

CREATE TABLE public."Items"
(
    id bigint NOT NULL DEFAULT nextval('"Items_id_seq"'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    price bigint NOT NULL,
    quant bigint NOT NULL,
    id_category bigint NOT NULL,
    id_check bigint NOT NULL,
    CONSTRAINT "Items_pkey" PRIMARY KEY (id),
    CONSTRAINT category_fkey FOREIGN KEY (id_category)
        REFERENCES public."Categories" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT check_fkey FOREIGN KEY (id_check)
        REFERENCES public."Checks" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Items"
    OWNER to postgres;