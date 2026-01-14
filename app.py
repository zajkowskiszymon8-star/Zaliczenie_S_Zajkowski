import streamlit as st
from supabase_client import supabase

st.set_page_config(page_title="Magazyn", layout="centered")
st.title("📦 Aplikacja magazynowa")

# ===== FUNKCJE =====

def get_produkty():
    return supabase.table("Produkty").select(
        "id, nazwa, liczba, cena, Kategorie(nazwa)"
    ).execute().data

def get_kategorie():
    return supabase.table("Kategorie").select("*").execute().data

def dodaj_produkt(nazwa, ilosc, cena, kategoria_id):
    supabase.table("Produkty").insert({
        "nazwa": nazwa,
        "liczba": ilosc,
        "cena": cena,
        "kategoria_id": kategoria_id
    }).execute()

def usun_produkt(pid):
    supabase.table("Produkty").delete().eq("id", pid).execute()

def zmien_cene(pid, cena):
    supabase.table("Produkty").update({"cena": cena}).eq("id", pid).execute()

def zmien_ilosc(pid, ilosc):
    supabase.table("Produkty").update({"liczba": ilosc}).eq("id", pid).execute()

# ===== DANE =====

produkty = get_produkty()
kategorie = get_kategorie()

kat_map = {k["nazwa"]: k["id"] for k in kategorie}
prod_map = {p["nazwa"]: p["id"] for p in produkty}

# ===== DODAWANIE =====

st.header("➕ Dodaj produkt")

with st.form("add_product"):
    nazwa = st.text_input("Nazwa")
    ilosc = st.number_input("Ilość", min_value=0, step=1)
    cena = st.number_input("Cena", min_value=0.0, step=0.01)
    kategoria = st.selectbox("Kategoria", kat_map.keys())
    if st.form_submit_button("Dodaj"):
        dodaj_produkt(nazwa, ilosc, cena, kat_map[kategoria])
        st.success("Produkt dodany")
        st.experimental_rerun()

# ===== FILTR =====

st.header("📂 Filtr produktów")

wybrana_kategoria = st.selectbox(
    "Pokaż kategorię",
    ["Wszystkie"] + list(kat_map.keys())
)

# ===== LISTA PRODUKTÓW =====

st.header("📋 Produkty")

for p in produkty:
    nazwa_kat = p["Kategorie"]["nazwa"]

    if wybrana_kategoria != "Wszystkie" and nazwa_kat != wybrana_kategoria:
        continue

    if p["liczba"] <= 5:
        st.error(
            f"{p['nazwa']} | {nazwa_kat} | "
            f"Ilość: {p['liczba']} | Cena: {p['cena']} zł"
        )
    else:
        st.write(
            f"{p['nazwa']} | {nazwa_kat} | "
            f"Ilość: {p['liczba']} | Cena: {p['cena']} zł"
        )

# ===== EDYCJA =====

st.header("✏️ Edycja produktu")

produkt = st.selectbox("Produkt", prod_map.keys())
nowa_cena = st.number_input("Nowa cena", min_value=0.0, step=0.01)
nowa_ilosc = st.number_input("Nowa ilość", min_value=0, step=1)

col1, col2 = st.columns(2)

with col1:
    if st.button("Zmień cenę"):
        zmien_cene(prod_map[produkt], nowa_cena)
        st.success("Cena zmieniona")
        st.experimental_rerun()

with col2:
    if st.button("Zmień ilość"):
        zmien_ilosc(prod_map[produkt], nowa_ilosc)
        st.success("Ilość zmieniona")
        st.experimental_rerun()

# ===== USUWANIE =====

st.header("🗑 Usuń produkt")

produkt_usun = st.selectbox("Produkt do usunięcia", prod_map.keys())
if st.button("Usuń"):
    usun_produkt(prod_map[produkt_usun])
    st.warning("Produkt usunięty")
    st.experimental_rerun()
