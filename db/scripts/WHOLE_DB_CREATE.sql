-- SEQUENCE: public."Categories_id_seq"

-- DROP SEQUENCE public."Categories_id_seq";

CREATE SEQUENCE public."Categories_id_seq";

ALTER SEQUENCE public."Categories_id_seq"
    OWNER TO postgres;

-- SEQUENCE: public."Users_id_seq"

-- DROP SEQUENCE public."Users_id_seq";

CREATE SEQUENCE public."Users_id_seq";

ALTER SEQUENCE public."Users_id_seq"
    OWNER TO postgres;


-- SEQUENCE: public."Checks_id_seq"

-- DROP SEQUENCE public."Checks_id_seq";

CREATE SEQUENCE public."Checks_id_seq";

ALTER SEQUENCE public."Checks_id_seq"
    OWNER TO postgres;


-- SEQUENCE: public."Items_id_seq"

-- DROP SEQUENCE public."Items_id_seq";

CREATE SEQUENCE public."Items_id_seq";

ALTER SEQUENCE public."Items_id_seq"
    OWNER TO postgres;


-- Table: public."Users"

-- DROP TABLE public."Users";

CREATE TABLE public."Users"
(
    id bigint NOT NULL DEFAULT nextval('"Users_id_seq"'::regclass),
    login text COLLATE pg_catalog."default" NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Users_pkey" PRIMARY KEY (id),
    UNIQUE (login)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Users"
    OWNER to postgres;

-- Table: public."Categories"

-- DROP TABLE public."Categories";

CREATE TABLE public."Categories"
(
    id bigint NOT NULL DEFAULT nextval('"Categories_id_seq"'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT "Categories_pkey" PRIMARY KEY (id),
    UNIQUE (name)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public."Categories"
    OWNER to postgres;

-- Table: public."Checks"

-- DROP TABLE public."Checks";

CREATE TABLE public."Checks"
(
    id bigint NOT NULL DEFAULT nextval('"Checks_id_seq"'::regclass),
    specifier text COLLATE pg_catalog."default" NOT NULL,
    shop text COLLATE pg_catalog."default" NOT NULL,
    date timestamp(4) without time zone NOT NULL,
    id_user bigint NOT NULL,
    UNIQUE(specifier),
    CONSTRAINT "Checks_pkey" PRIMARY KEY (id),
    CONSTRAINT "Checks_specifier_key" UNIQUE (specifier)
,
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

-- Table: public."Patterns"

-- DROP TABLE public."Patterns";

CREATE TABLE public."Patterns"
(
    pattern text COLLATE pg_catalog."default" NOT NULL,
    id_category bigint,
    UNIQUE (pattern,id_category),
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