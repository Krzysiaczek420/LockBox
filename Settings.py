import json

################################################################
# funkcja do zmiany koloru i motywu
################################################################

################################################################
# funkcja odczytująca kolor i motyw z pliku settings.json
################################################################
def load_setting(path='settings.json'):
    with open(path, 'r') as settings_file:
        settings = json.load(settings_file)
    return settings

################################################################
# funkcja ustawiająca motyw i kolor
################################################################
def set_theme_and_color(file_path):
    # Słownik mapujący nazwy kolorów na ich ścieżki do plików JSON lub nazwy domyślne
    colors = {
        "blue": "Themes/blue.json",
        #"dark-blue": "dark-blue",
        "green": "Themes/green.json",
        "red": "Themes/red.json",
        "yellow": "Themes/yellow.json",
        "orange": "Themes/orange.json",
        "pink": "Themes/pink.json",
        "violet": "Themes/violet.json"
    }
    
    settings = load_setting(file_path)
    color = settings.get('color', 'default_color')
    theme = settings.get('theme', 'default_theme')
    
    # Pobierz odpowiednią wartość ze słownika kolory
    color = colors.get(color, color)  # Jeśli kolor nie jest w słowniku, użyj go bezpośrednio

    return theme, color

################################################################
# funkcja wczytująca tłumaczenie dla danego modułu i języka
################################################################
def load_translation(language, module):
    translation_file_path = f'Translations/{module}-{language}.json'
    with open(translation_file_path, 'r', encoding='utf-8') as file_path:
        translation = json.load(file_path)
    return translation

