--
-- PostgreSQL database dump
--

\restrict i3JpWuaJ4F6fRRxvyVWwTIvtXBgikkcSQ6knZ3M30grvhCB3FGrPMuBRCcqVi1n

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
96	CONCEPT
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
752	5411012537593	CO1001	96	EXCEL | ADMIN	2026-06-03 11:32:24.240588	\N
753	5411012537609	CO1002	96	EXCEL | ADMIN	2026-06-03 11:32:24.240594	\N
754	5411012537616	CO1003	96	EXCEL | ADMIN	2026-06-03 11:32:24.240596	\N
755	5411012537623	CO1004	24	EXCEL | ADMIN	2026-06-03 11:32:24.240597	\N
756	5411012537630	CO1005	24	EXCEL | ADMIN	2026-06-03 11:32:24.240599	\N
757	5411012537647	CO1006	96	EXCEL | ADMIN	2026-06-03 11:32:24.2406	\N
758	5411012537654	CO1007	204	EXCEL | ADMIN	2026-06-03 11:32:24.240601	\N
759	5411012537661	CO1008	96	EXCEL | ADMIN	2026-06-03 11:32:24.240602	\N
760	5411012537678	CO1009	96	EXCEL | ADMIN	2026-06-03 11:32:24.240603	\N
761	5411012537685	CO1010	96	EXCEL | ADMIN	2026-06-03 11:32:24.240604	\N
762	5411012537692	CO1011	96	EXCEL | ADMIN	2026-06-03 11:32:24.240605	\N
763	5411012537708	CO1012	30	EXCEL | ADMIN	2026-06-03 11:32:24.240606	\N
764	5411012537715	CO1013	24	EXCEL | ADMIN	2026-06-03 11:32:24.240607	\N
765	5411012537722	CO1014	60	EXCEL | ADMIN	2026-06-03 11:32:24.240608	\N
766	5411012537739	CO1015	18	EXCEL | ADMIN	2026-06-03 11:32:24.240609	\N
767	5411012537746	CO1016	96	EXCEL | ADMIN	2026-06-03 11:32:24.24061	\N
768	5411012537753	CO1017	96	EXCEL | ADMIN	2026-06-03 11:32:24.240611	\N
769	5411012537760	CO1018	30	EXCEL | ADMIN	2026-06-03 11:32:24.240612	\N
770	5411012537777	CO1019	30	EXCEL | ADMIN	2026-06-03 11:32:24.240613	\N
771	5411012537784	CO1020	30	EXCEL | ADMIN	2026-06-03 11:32:24.240614	\N
772	5411012537906	CO1101	30	EXCEL | ADMIN	2026-06-03 11:32:24.240615	\N
773	5411012537913	CO1102	36	EXCEL | ADMIN	2026-06-03 11:32:24.240616	\N
774	5411012537920	CO1103	30	EXCEL | ADMIN	2026-06-03 11:32:24.240617	\N
775	5411012537937	CO1104	18	EXCEL | ADMIN	2026-06-03 11:32:24.240619	\N
776	5411012537944	CO1105	24	EXCEL | ADMIN	2026-06-03 11:32:24.24062	\N
777	5411012537951	CO1106	30	EXCEL | ADMIN	2026-06-03 11:32:24.240621	\N
778	5411012537975	CO1201	156	EXCEL | ADMIN	2026-06-03 11:32:24.240622	\N
779	5411012537982	CO1202	156	EXCEL | ADMIN	2026-06-03 11:32:24.240623	\N
780	5411012537999	CO1203	96	EXCEL | ADMIN	2026-06-03 11:32:24.240624	\N
781	5411012538002	CO1204	30	EXCEL | ADMIN	2026-06-03 11:32:24.240625	\N
782	5411012538019	CO1205	96	EXCEL | ADMIN	2026-06-03 11:32:24.240626	\N
783	5411012538026	CO1206	156	EXCEL | ADMIN	2026-06-03 11:32:24.240627	\N
784	5411012537791	CO3001	96	EXCEL | ADMIN	2026-06-03 11:32:24.240628	\N
785	5411012537807	CO3002	96	EXCEL | ADMIN	2026-06-03 11:32:24.240629	\N
786	5411012537814	CO3003	96	EXCEL | ADMIN	2026-06-03 11:32:24.24063	\N
787	5411012537821	CO3004	0	EXCEL | ADMIN	2026-06-03 11:32:24.240631	\N
788	5411012537852	CO3005	30	EXCEL | ADMIN	2026-06-03 11:32:24.240632	\N
789	5411012537838	CO3006	30	EXCEL | ADMIN	2026-06-03 11:32:24.240633	\N
790	5411012537845	CO3007	30	EXCEL | ADMIN	2026-06-03 11:32:24.240634	\N
791	5411012537876	CO3008	18	EXCEL | ADMIN	2026-06-03 11:32:24.240635	\N
792	5411012537869	CO3009	96	EXCEL | ADMIN	2026-06-03 11:32:24.240636	\N
793	5411012537883	CO3010	96	EXCEL | ADMIN	2026-06-03 11:32:24.240637	\N
794	5411012538378	CO3101	30	EXCEL | ADMIN	2026-06-03 11:32:24.240638	\N
795	5411012538385	CO3102	30	EXCEL | ADMIN	2026-06-03 11:32:24.240639	\N
796	5411012538392	CO3103	30	EXCEL | ADMIN	2026-06-03 11:32:24.24064	\N
\.


--
-- Data for Name: urunler; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.urunler (id, barkod, isim, miktar, kategori_id, lot, yer) FROM stdin;
573	5411012537593	CO1001	96	96	444146/01	
574	5411012537609	CO1002	96	96	444148/01	
575	5411012537616	CO1003	96	96	443595/01	
576	5411012537623	CO1004	24	96	443177/01	
577	5411012537630	CO1005	24	96	443274/01	
578	5411012537647	CO1006	96	96	443856/01	
579	5411012537654	CO1007	204	96	444152/01	
580	5411012537661	CO1008	96	96	442310/01	
581	5411012537678	CO1009	96	96	443276/01	
582	5411012537685	CO1010	96	96	444145/01	
583	5411012537692	CO1011	96	96	443559/01	
584	5411012537708	CO1012	30	96	443741/01	
585	5411012537715	CO1013	24	96	443606/01	
586	5411012537722	CO1014	60	96	441812/01	
587	5411012537739	CO1015	18	96	441962/01	
588	5411012537746	CO1016	96	96	443560/01	
589	5411012537753	CO1017	96	96	443607/01	
590	5411012537760	CO1018	30	96	443742/01	
591	5411012537777	CO1019	30	96	443608/01	
592	5411012537784	CO1020	30	96	443561/01	
593	5411012537906	CO1101	30	96	443345/01	
594	5411012537913	CO1102	36	96	443562/01	
595	5411012537920	CO1103	30	96	443563/01	
596	5411012537937	CO1104	18	96	443743/01	
597	5411012537944	CO1105	24	96	440844/02	
598	5411012537951	CO1106	30	96	442758/01	
599	5411012537975	CO1201	156	96	443744/01	
600	5411012537982	CO1202	156	96	444174/01	
601	5411012537999	CO1203	96	96	443746/01	
602	5411012538002	CO1204	30	96	440896/01	
603	5411012538019	CO1205	96	96	442762/01	
604	5411012538026	CO1206	156	96	443749/01	
605	5411012537791	CO3001	96	96	440815/01	
606	5411012537807	CO3002	96	96	440816/01	
607	5411012537814	CO3003	96	96	440817/01	
608	5411012537821	CO3004	0	96		
609	5411012537852	CO3005	30	96	440819/01	
610	5411012537838	CO3006	30	96	440820/01	
611	5411012537845	CO3007	30	96	440821/01	
612	5411012537876	CO3008	18	96	440822/01	
613	5411012537869	CO3009	96	96	443981/01	
614	5411012537883	CO3010	96	96	443982/01	
615	5411012538378	CO3101	30	96	442765/01	
616	5411012538385	CO3102	30	96	442766/01	
617	5411012538392	CO3103	30	96	443752/01	
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

SELECT pg_catalog.setval('public.kategoriler_id_seq', 96, true);


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

SELECT pg_catalog.setval('public.stok_hareketleri_id_seq', 796, true);


--
-- Name: urunler_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.urunler_id_seq', 617, true);


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

\unrestrict i3JpWuaJ4F6fRRxvyVWwTIvtXBgikkcSQ6knZ3M30grvhCB3FGrPMuBRCcqVi1n

