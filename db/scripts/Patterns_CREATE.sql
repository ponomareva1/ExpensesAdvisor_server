-- Table: public."Patterns"

-- DROP TABLE public."Patterns";

CREATE TABLE public."Patterns"
(
    pattern text COLLATE pg_catalog."default" NOT NULL,
    id_category bigint,
    CONSTRAINT "Patterns_pkey" PRIMARY KEY (pattern),
    CONSTRAINT category_fkey FOREIGN KEY (id_category)
        REFERENCES public."Categories" (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Patterns"
    OWNER to postgres;