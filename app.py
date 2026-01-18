import streamlit as st
from supabase_client import supabase
import pandas as pd

st.set_page_config(page_title="Magazyn", layout="centered")
st.title("📦 Aplikacja magazynowa")

# ===== FUNKCJE =====

def get_produkty():
    return supabase.table("Produkty").select(
        'id, "Nazwa", "Liczba", "Cena", Kategoria_id("Nazwa")'
    ).execute().data

def get_kategorie():
    return supabase.table("Kategorie").select(
        'id, "Nazwa"'
    ).execute().data

def dodaj_produkt(nazwa, ilosc, cena, kategoria_id):
    supabase.table("Produkty").insert({
        "Nazwa": nazwa,
        "Liczba": ilosc,
        "Cena": cena,
        "Kategoria_id": kategoria_id
    }).execute()

def usun_produkt(pid):
    supabase.table("Produkty").delete().eq("id", pid).execute()

def zmien_cene(pid, cena):
    supabase.table("Produkty").update({"Cena": cena}).eq("id", pid).execute()

def zmien_ilosc(pid, ilosc):
    supabase.table("Produkty").update({"Liczba": ilosc}).eq("id", pid).execute()

# ===== DANE =====

produkty = get_produkty()
kategorie = get_kategorie()

kat_map = {k["Nazwa"]: k["id"] for k in kategorie}
prod_map = {p["Nazwa"]: p["id"] for p in produkty}

# ===== FILTR + SORT =====

st.header("📂 Filtrowanie i sortowanie")

wybrana_kategoria = st.selectbox(
    "Kategoria",
    ["Wszystkie"] + list(kat_map.keys())
)

sortowanie = st.selectbox(
    "Sortuj według",
    ["Brak", "Cena rosnąco", "Cena malejąco", "Ilość rosnąco", "Ilość malejąco"]
)

# ===== TABELA PRODUKTÓW =====

tabela = []

for p in produkty:
    nazwa_kat = p["Kategoria_id"]["Nazwa"]

    if wybrana_kategoria != "Wszystkie" and nazwa_kat != wybrana_kategoria:
        continue

    tabela.append({
        "Nazwa": p["Nazwa"],
        "Kategoria": nazwa_kat,
        "Cena": p["Cena"],
        "Ilość": p["Liczba"]
    })

df = pd.DataFrame(tabela)

# ===== SORTOWANIE =====

if not df.empty:
    if sortowanie == "Cena rosnąco":
        df = df.sort_values("Cena")
    elif sortowanie == "Cena malejąco":
        df = df.sort_values("Cena", ascending=False)
    elif sortowanie == "Ilość rosnąco":
        df = df.sort_values("Ilość")
    elif sortowanie == "Ilość malejąco":
        df = df.sort_values("Ilość", ascending=False)

# ===== SUMA MAGAZYNU =====

st.header("💰 Wartość magazynu")

if not df.empty:
    suma = (df["Cena"] * df["Ilość"]).sum()
    st.metric("Łączna wartość [zł]", f"{suma:.2f}")
else:
    st.metric("Łączna wartość [zł]", "0.00")

# ===== KOLOROWANIE =====

def koloruj_ilosc(val):
    if val <= 5:
        return "background-color: #ffcccc"
    elif val <= 10:
        return "background-color: #fff3cd"
    else:
        return ""

st.header("📊 Produkty")

if not df.empty:
    st.dataframe(
        df.style.applymap(koloruj_ilosc, subset=["Ilość"]),
        use_container_width=True
    )
else:
    st.info("Brak produktów do wyświetlenia")

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
