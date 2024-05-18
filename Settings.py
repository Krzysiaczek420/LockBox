import json

################################################################
# funkcja do zmiany koloru i motywu
################################################################

################################################################
# funkcja odczytująca kolor i motyw z pliku settings.json
################################################################
def wczytaj_ustawienia(sciezka='settings.json'):
    with open(sciezka, 'r') as plik:
        ustawienia = json.load(plik)
    return ustawienia

################################################################
# funkcja ustawiająca motyw i kolor
################################################################
def ustaw_motyw_i_kolor(sciezka_do_pliku):
    # Słownik mapujący nazwy kolorów na ich ścieżki do plików JSON lub nazwy domyślne
    kolory = {
        "blue": "motywy/blue.json",
        #"dark-blue": "dark-blue",
        "green": "motywy/green.json",
        "red": "motywy/red.json",
        "yellow": "motywy/yellow.json",
        "orange": "motywy/orange.json",
        "pink": "motywy/pink.json",
        "violet": "motywy/violet.json"
    }
    
    ustawienia = wczytaj_ustawienia(sciezka_do_pliku)
    kolor = ustawienia.get('color', 'default_color')
    motyw = ustawienia.get('theme', 'default_theme')
    
    # Pobierz odpowiednią wartość ze słownika kolory
    kolor = kolory.get(kolor, kolor)  # Jeśli kolor nie jest w słowniku, użyj go bezpośrednio

    return motyw, kolor

################################################################
# funkcja wczytująca tłumaczenie dla danego modułu i języka
################################################################
def wczytaj_tlumaczenie_modulu(jezyk, modul):
    sciezka_do_tlumaczen = f'tlumaczenia/{modul}-{jezyk}.json'
    with open(sciezka_do_tlumaczen, 'r', encoding='utf-8') as plik:
        tlumaczenie = json.load(plik)
    return tlumaczenie
