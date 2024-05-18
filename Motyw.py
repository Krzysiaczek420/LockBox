import json
################################################################
# funkcja do zmieny koloru i motywu
################################################################

################################################################
# funkcja odczytujaca kolor i motyw z plkiku settings.json
################################################################
def wczytaj_ustawienia(sciezka):
    with open(sciezka, 'r') as plik:
        ustawienia = json.load(plik)
    return ustawienia

################################################################
# funkcja ustawiajaca motyw i kolor
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
