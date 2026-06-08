--
-- PostgreSQL database dump
--

\restrict YmZtwrgHJ4IhmPp8uP403rxlJBu3lDS7fScxhDcRh56WPqvzaWNfhM6HL8sfYNL

-- Dumped from database version 18.2
-- Dumped by pg_dump version 18.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: depo_yerleri; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.depo_yerleri (
    id integer NOT NULL,
    ad character varying
);


ALTER TABLE public.depo_yerleri OWNER TO postgres;

--
-- Name: depo_yerleri_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.depo_yerleri_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.depo_yerleri_id_seq OWNER TO postgres;

--
-- Name: depo_yerleri_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.depo_yerleri_id_seq OWNED BY public.depo_yerleri.id;


--
-- Name: islem_nedenleri; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.islem_nedenleri (
    id integer NOT NULL,
    ad character varying
);


ALTER TABLE public.islem_nedenleri OWNER TO postgres;

--
-- Name: islem_nedenleri_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.islem_nedenleri_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.islem_nedenleri_id_seq OWNER TO postgres;

--
-- Name: islem_nedenleri_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.islem_nedenleri_id_seq OWNED BY public.islem_nedenleri.id;


--
-- Name: kategoriler; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kategoriler (
    id integer NOT NULL,
    ad character varying NOT NULL
);


ALTER TABLE public.kategoriler OWNER TO postgres;

--
-- Name: kategoriler_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kategoriler_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kategoriler_id_seq OWNER TO postgres;

--
-- Name: kategoriler_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kategoriler_id_seq OWNED BY public.kategoriler.id;


--
-- Name: kullanicilar; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kullanicilar (
    id integer NOT NULL,
    kullanici_adi character varying,
    sifre character varying,
    rol character varying,
    can_add_stock boolean DEFAULT true,
    can_exit_stock boolean DEFAULT true,
    can_edit_product boolean DEFAULT true,
    can_delete boolean DEFAULT true,
    can_manage_users boolean DEFAULT true,
    can_see_logs boolean DEFAULT true,
    rol_id integer
);


ALTER TABLE public.kullanicilar OWNER TO postgres;

--
-- Name: kullanicilar_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kullanicilar_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kullanicilar_id_seq OWNER TO postgres;

--
-- Name: kullanicilar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kullanicilar_id_seq OWNED BY public.kullanicilar.id;


--
-- Name: musteriler; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.musteriler (
    id integer NOT NULL,
    ad character varying NOT NULL
);


ALTER TABLE public.musteriler OWNER TO postgres;

--
-- Name: musteriler_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.musteriler_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.musteriler_id_seq OWNER TO postgres;

--
-- Name: musteriler_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.musteriler_id_seq OWNED BY public.musteriler.id;


--
-- Name: roller; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roller (
    id integer NOT NULL,
    ad character varying,
    can_add_stock boolean,
    can_exit_stock boolean,
    can_edit_product boolean,
    can_delete boolean,
    can_manage_users boolean,
    can_see_logs boolean
);


ALTER TABLE public.roller OWNER TO postgres;

--
-- Name: roller_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roller_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roller_id_seq OWNER TO postgres;

--
-- Name: roller_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roller_id_seq OWNED BY public.roller.id;


--
-- Name: sayimlar; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sayimlar (
    id integer NOT NULL,
    barkod character varying,
    lot_no character varying,
    miktar integer,
    kayit_tarihi timestamp without time zone,
    urun_adi character varying
);


ALTER TABLE public.sayimlar OWNER TO postgres;

--
-- Name: sayimlar_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sayimlar_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sayimlar_id_seq OWNER TO postgres;

--
-- Name: sayimlar_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sayimlar_id_seq OWNED BY public.sayimlar.id;


--
-- Name: stok_hareketleri; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stok_hareketleri (
    id integer NOT NULL,
    urun_barkod character varying,
    urun_isim character varying,
    miktar_degisimi integer,
    islem_tipi character varying,
    tarih timestamp without time zone,
    urun_lot character varying
);


ALTER TABLE public.stok_hareketleri OWNER TO postgres;

--
-- Name: stok_hareketleri_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stok_hareketleri_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stok_hareketleri_id_seq OWNER TO postgres;

--
-- Name: stok_hareketleri_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stok_hareketleri_id_seq OWNED BY public.stok_hareketleri.id;


--
-- Name: urunler; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.urunler (
    id integer NOT NULL,
    barkod character varying NOT NULL,
    isim character varying NOT NULL,
    miktar integer,
    kategori_id integer,
    lot character varying,
    yer character varying
);


ALTER TABLE public.urunler OWNER TO postgres;

--
-- Name: urunler_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.urunler_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.urunler_id_seq OWNER TO postgres;

--
-- Name: urunler_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.urunler_id_seq OWNED BY public.urunler.id;


--
-- Name: depo_yerleri id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.depo_yerleri ALTER COLUMN id SET DEFAULT nextval('public.depo_yerleri_id_seq'::regclass);


--
-- Name: islem_nedenleri id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.islem_nedenleri ALTER COLUMN id SET DEFAULT nextval('public.islem_nedenleri_id_seq'::regclass);


--
-- Name: kategoriler id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kategoriler ALTER COLUMN id SET DEFAULT nextval('public.kategoriler_id_seq'::regclass);


--
-- Name: kullanicilar id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kullanicilar ALTER COLUMN id SET DEFAULT nextval('public.kullanicilar_id_seq'::regclass);


--
-- Name: musteriler id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.musteriler ALTER COLUMN id SET DEFAULT nextval('public.musteriler_id_seq'::regclass);


--
-- Name: roller id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roller ALTER COLUMN id SET DEFAULT nextval('public.roller_id_seq'::regclass);


--
-- Name: sayimlar id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sayimlar ALTER COLUMN id SET DEFAULT nextval('public.sayimlar_id_seq'::regclass);


--
-- Name: stok_hareketleri id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stok_hareketleri ALTER COLUMN id SET DEFAULT nextval('public.stok_hareketleri_id_seq'::regclass);


--
-- Name: urunler id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urunler ALTER COLUMN id SET DEFAULT nextval('public.urunler_id_seq'::regclass);


--
-- Data for Name: depo_yerleri; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.depo_yerleri (id, ad) FROM stdin;
\.


--
-- Data for Name: islem_nedenleri; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.islem_nedenleri (id, ad) FROM stdin;
\.


--
-- Data for Name: kategoriler; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.kategoriler (id, ad) FROM stdin;
\.


--
-- Data for Name: kullanicilar; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.kullanicilar (id, kullanici_adi, sifre, rol, can_add_stock, can_exit_stock, can_edit_product, can_delete, can_manage_users, can_see_logs, rol_id) FROM stdin;
1	ADMIN	1881	admin	t	t	t	t	t	t	1
\.


--
-- Data for Name: musteriler; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.musteriler (id, ad) FROM stdin;
\.


--
-- Data for Name: roller; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roller (id, ad, can_add_stock, can_exit_stock, can_edit_product, can_delete, can_manage_users, can_see_logs) FROM stdin;
1	ADMIN	t	t	t	t	t	t
2	DEPOCU	t	t	t	f	f	t
3	KULLANICI	f	f	f	f	f	t
\.


--
-- Data for Name: sayimlar; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sayimlar (id, barkod, lot_no, miktar, kayit_tarihi, urun_adi) FROM stdin;
\.


--
-- Data for Name: stok_hareketleri; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.stok_hareketleri (id, urun_barkod, urun_isim, miktar_degisimi, islem_tipi, tarih, urun_lot) FROM stdin;
\.


--
-- Data for Name: urunler; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.urunler (id, barkod, isim, miktar, kategori_id, lot, yer) FROM stdin;
\.


--
-- Name: depo_yerleri_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.depo_yerleri_id_seq', 36, true);


--
-- Name: islem_nedenleri_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.islem_nedenleri_id_seq', 3, true);


--
-- Name: kategoriler_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.kategoriler_id_seq', 95, true);


--
-- Name: kullanicilar_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.kullanicilar_id_seq', 28, true);


--
-- Name: musteriler_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.musteriler_id_seq', 26, true);


--
-- Name: roller_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roller_id_seq', 11, true);


--
-- Name: sayimlar_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sayimlar_id_seq', 156, true);


--
-- Name: stok_hareketleri_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.stok_hareketleri_id_seq', 751, true);


--
-- Name: urunler_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.urunler_id_seq', 572, true);


--
-- Name: depo_yerleri depo_yerleri_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.depo_yerleri
    ADD CONSTRAINT depo_yerleri_pkey PRIMARY KEY (id);


--
-- Name: islem_nedenleri islem_nedenleri_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.islem_nedenleri
    ADD CONSTRAINT islem_nedenleri_pkey PRIMARY KEY (id);


--
-- Name: kategoriler kategoriler_ad_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kategoriler
    ADD CONSTRAINT kategoriler_ad_key UNIQUE (ad);


--
-- Name: kategoriler kategoriler_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kategoriler
    ADD CONSTRAINT kategoriler_pkey PRIMARY KEY (id);


--
-- Name: kullanicilar kullanicilar_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kullanicilar
    ADD CONSTRAINT kullanicilar_pkey PRIMARY KEY (id);


--
-- Name: musteriler musteriler_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.musteriler
    ADD CONSTRAINT musteriler_pkey PRIMARY KEY (id);


--
-- Name: roller roller_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roller
    ADD CONSTRAINT roller_pkey PRIMARY KEY (id);


--
-- Name: sayimlar sayimlar_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sayimlar
    ADD CONSTRAINT sayimlar_pkey PRIMARY KEY (id);


--
-- Name: stok_hareketleri stok_hareketleri_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stok_hareketleri
    ADD CONSTRAINT stok_hareketleri_pkey PRIMARY KEY (id);


--
-- Name: urunler urunler_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urunler
    ADD CONSTRAINT urunler_pkey PRIMARY KEY (id);


--
-- Name: ix_depo_yerleri_ad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_depo_yerleri_ad ON public.depo_yerleri USING btree (ad);


--
-- Name: ix_depo_yerleri_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_depo_yerleri_id ON public.depo_yerleri USING btree (id);


--
-- Name: ix_islem_nedenleri_ad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_islem_nedenleri_ad ON public.islem_nedenleri USING btree (ad);


--
-- Name: ix_islem_nedenleri_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_islem_nedenleri_id ON public.islem_nedenleri USING btree (id);


--
-- Name: ix_kullanicilar_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kullanicilar_id ON public.kullanicilar USING btree (id);


--
-- Name: ix_kullanicilar_kullanici_adi; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_kullanicilar_kullanici_adi ON public.kullanicilar USING btree (kullanici_adi);


--
-- Name: ix_musteriler_ad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_musteriler_ad ON public.musteriler USING btree (ad);


--
-- Name: ix_musteriler_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_musteriler_id ON public.musteriler USING btree (id);


--
-- Name: ix_roller_ad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roller_ad ON public.roller USING btree (ad);


--
-- Name: ix_roller_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roller_id ON public.roller USING btree (id);


--
-- Name: ix_sayimlar_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sayimlar_id ON public.sayimlar USING btree (id);


--
-- Name: urunler urunler_kategori_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.urunler
    ADD CONSTRAINT urunler_kategori_id_fkey FOREIGN KEY (kategori_id) REFERENCES public.kategoriler(id);


--
-- PostgreSQL database dump complete
--

\unrestrict YmZtwrgHJ4IhmPp8uP403rxlJBu3lDS7fScxhDcRh56WPqvzaWNfhM6HL8sfYNL

