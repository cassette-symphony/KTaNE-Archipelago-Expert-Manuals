from concurrent.futures import Future

import urllib.request
import webbrowser
import socketserver
import http.server
import multiprocessing
import ssl
import certifi

import asyncio
import websockets
import json
import typing

import threading

ssl_context = ssl.create_default_context(cafile=certifi.where())
#ssl.SSLContext.load_cert_chain()

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Create a new event loop for the background thread
background_loop = asyncio.new_event_loop()
threading.Thread(target=start_background_loop, args=(background_loop,), daemon=True).start()

class Version(typing.NamedTuple):
    major: int
    minor: int
    build: int

    def as_simple_string(self) -> str:
        return ".".join(str(item) for item in self)

PORT = 21713
apSocket = None
connectionResult = None
connectionError = None
versionNumber = "0.2.0"
apVersion = Version(0, 6, 3)

allModsRepo = {
    "en": {
        "TheButton": "The%20Button",
        "Wires": "Wires",
        "Keypad": "Keypad",
        "Capacitor": "Capacitor%20Discharge",
        "ComplicatedWires": "Complicated%20Wires",
        "Knob": "Knob",
        "Maze": "Maze",
        "Memory": "Memory",
        "MorseCode": "Morse%20Code",
        "Password": "Password",
        "SimonSays": "Simon%20Says",
        "VentGas": "Venting%20Gas",
        "WhosonFirst": "Who%27s%20on%20First",
        "WireSequence": "Wire%20Sequence"
    },
    "cs": {
        "TheButton": "The%20Button%20translated%20(Čeština%20—%20Tlačítko)%20originální%20modul%20(Frank%20%26%20adamcz)",
        "Wires": "Wires%20translated%20(Čeština%20—%20Dráty)%20(Frank%20%26%20adamcz)",
        "Keypad": "Keypad%20translated%20(Čeština%20—%20Klávesnice)%20(Frank%20%26%20adamcz)",
        "Capacitor": "Capacitor%20Discharge%20translated%20(Čeština%20—%20Vybití%20Kondenzátoru)%20(Frank%20%26%20adamcz)",
        "ComplicatedWires": "Complicated%20Wires%20translated%20(Čeština%20—%20Komplikované%20Dráty)%20(Frank%20%26%20adamcz)",
        "Knob": "Knob%20translated%20(Čeština%20—%20Knoflík)%20optimalizováno%20(Frank%20%26%20adamcz)",
        "Maze": "Maze%20translated%20(Čeština%20—%20Bludiště)%20(Frank%20%26%20adamcz)",
        "Memory": "Memory%20translated%20(Čeština%20—%20Paměť)%20(Frank%20%26%20adamcz)",
        "MorseCode": "Morse%20Code%20translated%20(Čeština%20—%20Morseovka)%20originální%20modul%20(Frank%20%26%20adamcz)",
        "Password": "Password%20translated%20(Čeština%20—%20Hesla)%20originální%20modul%20(Frank%20%26%20adamcz)",
        "SimonSays": "Simon%20Says%20translated%20(Čeština%20—%20Šimon%20Říká)%20(Frank%20%26%20adamcz)",
        "VentGas": "Venting%20Gas%20translated%20(Čeština%20—%20Vypouštění%20Plynu)%20(Frank%20%26%20adamcz)",
        "WhosonFirst": "Who%27s%20on%20First%20translated%20(Čeština%20—%20Kdo%20je%20první)%20originální%20modul%20(Frank,%20adamcz,%20Asmir,%20Cirax)",
        "WireSequence": "Wire%20Sequence%20translated%20(Čeština%20—%20Posloupnost%20Drátů)%20(Frank%20%26%20adamcz)"
    },
    "es": {
        "TheButton": "The%20Button%20translated%20(Español%20—%20El%20botón)%20oficial",
        "Wires": "Wires%20translated%20(Español%20—%20Cables)",
        "Keypad": "Keypad%20translated%20(Español%20—%20Teclado)",
        "Capacitor": "Capacitor%20Discharge%20translated%20(Español%20—%20Descargador%20de%20condensadores)",
        "ComplicatedWires": "Complicated%20Wires%20translated%20(Español%20—%20Cables%20complicados)",
        "Knob": "Knob%20translated%20(Español%20—%20Interruptor%20giratorio)",
        "Maze": "Maze%20translated%20(Español%20—%20Laberinto)",
        "Memory": "Memory%20translated%20(Español%20—%20Memoria)",
        "MorseCode": "Morse%20Code%20translated%20(Español%20—%20Código%20morse)%20oficial",
        "Password": "Password%20translated%20(Español%20—%20Contraseña)%20oficial",
        "SimonSays": "Simon%20Says%20translated%20(Español%20—%20Simón%20dice)",
        "VentGas": "Venting%20Gas%20translated%20(Español%20—%20Pantalla%20con%20mensajes)",
        "WhosonFirst": "Who%27s%20on%20First%20translated%20(Español%20—%20Quién%20va%20primero)%20oficial",
        "WireSequence": "Wire%20Sequence%20translated%20(Español%20—%20Secuencia%20de%20cables)"
    },
    "fr": {
        "TheButton": "The%20Button%20translated%20(Français%20—%20Le%20Bouton)%20officiel",
        "Wires": "Wires%20translated%20(Français%20—%20Fils)",
        "Keypad": "Keypad%20translated%20(Français%20—%20Clavier)",
        "Capacitor": "Capacitor%20Discharge%20translated%20(Français%20—%20Condensateur)",
        "ComplicatedWires": "Complicated%20Wires%20translated%20(Français%20—%20Fils%20compliqués)",
        "Knob": "Knob%20translated%20(Français%20—%20Molette)",
        "Maze": "Maze%20translated%20(Français%20—%20Labyrinthe)",
        "Memory": "Memory%20translated%20(Français%20—%20Memory)",
        "MorseCode": "Morse%20Code%20translated%20(Français%20—%20Code%20Morse)%20officiel",
        "Password": "Password%20translated%20(Français%20—%20Mot%20de%20Passe)%20officiel",
        "SimonSays": "Simon%20Says%20translated%20(Français%20—%20Simon)",
        "VentGas": "Venting%20Gas%20translated%20(Français%20—%20Évacuation%20du%20gaz)",
        "WhosonFirst": "Who%27s%20on%20First%20translated%20(Français%20—%20Jeux%20de%20Mots)%20officiel",
        "WireSequence": "Wire%20Sequence%20translated%20(Français%20—%20Séquences%20de%20fils)"
    },
    "ja": {
        "TheButton": "The%20Button%20translated%20(日本語%20—%20ボタン)",
        "Wires": "Wires%20translated%20(日本語%20—%20ワイヤ)",
        "Keypad": "Keypad%20translated%20(日本語%20—%20キーパッド)",
        "Capacitor": "Capacitor%20Discharge%20translated%20(日本語%20—%20コンデンサー)",
        "ComplicatedWires": "Complicated%20Wires%20translated%20(日本語%20—%20複雑ワイヤ)",
        "Knob": "Knob%20translated%20(日本語%20—%20ダイヤル)",
        "Maze": "Maze%20translated%20(日本語%20—%20迷路)",
        "Memory": "Memory%20translated%20(日本語%20—%20記憶)",
        "MorseCode": "Morse%20Code%20translated%20(日本語%20—%20モールス信号)",
        "Password": "Password%20translated%20(日本語%20—%20パスワード)",
        "SimonSays": "Simon%20Says%20translated%20(日本語%20—%20サイモンゲーム)",
        "VentGas": "Venting%20Gas%20translated%20(日本語%20—%20ガス放出)",
        "WhosonFirst": "Who%27s%20on%20First%20translated%20(日本語%20—%20表比較)",
        "WireSequence": "Wire%20Sequence%20translated%20(日本語%20—%20順番ワイヤ)"
    },
    "nl": {
        "TheButton": "The%20Button%20translated%20(Nederlands%20—%20De%20knop)",
        "Wires": "Wires%20translated%20(Nederlands%20—%20Draden)",
        "Keypad": "Keypad%20translated%20(Nederlands%20—%20Toetsenpanelen)",
        "ComplicatedWires": "Complicated%20Wires%20translated%20(Nederlands%20—%20Ingewikkelde%20Draden)",
        "Maze": "Maze%20translated%20(Nederlands%20—%20Doolhof)",
        "Memory": "Memory%20translated%20(Nederlands%20—%20Memory)",
        "MorseCode": "Morse%20Code%20translated%20(Nederlands%20—%20Morse-codering)",
        "Password": "Password%20translated%20(Nederlands%20—%20Wachtwoorden)",
        "SimonSays": "Simon%20Says%20translated%20(Nederlands%20—%20Simon%20Zegt)",
        "WhosonFirst": "Who%27s%20on%20First%20translated%20(Nederlands%20—%20Who%27s%20on%20First)",
        "WireSequence": "Wire%20Sequence%20translated%20(Nederlands%20—%20Dradenreeks)"
    },
    "pl": {
        "TheButton": "The%20Button%20translated%20(Polski%20—%20Przycisk)",
        "Wires": "Wires%20translated%20(Polski%20—%20Przewody)",
        "Keypad": "Keypad%20translated%20(Polski%20—%20Klawiatura)",
        "Capacitor": "Capacitor%20Discharge%20translated%20(Polski%20—%20Rozładowywanie%20Kondensatora)",
        "ComplicatedWires": "Complicated%20Wires%20translated%20(Polski%20—%20Skomplikowane%20Przewody)",
        "Knob": "Knob%20translated%20(Polski%20—%20Gałka)",
        "Maze": "Maze%20translated%20(Polski%20—%20Labirynt)",
        "Memory": "Memory%20translated%20(Polski%20—%20Pamięć)",
        "MorseCode": "Morse%20Code%20translated%20(Polski%20—%20Alfabet%20Morse%27a)",
        "Password": "Password%20translated%20(Polski%20—%20Hasło)",
        "SimonSays": "Simon%20Says%20translated%20(Polski%20—%20Simon%20Mówi)",
        "VentGas": "Venting%20Gas%20translated%20(Polski%20—%20Wietrzenie%20Gazu)",
        "WhosonFirst": "Who%27s%20on%20First%20translated%20(Polski%20—%20Kto%20Jest%20Na%20Pierwszym)",
        "WireSequence": "Wire%20Sequence%20translated%20(Polski%20—%20Sekwencja%20Przewodów)"
    },
    "ru": {
        "TheButton": "The%20Button%20translated%20(Русский%20—%20Кнопка)%20оригинальный",
        "Wires": "Wires%20translated%20(Русский%20—%20Провода)",
        "Keypad": "Keypad%20translated%20(Русский%20—%20Клавиатура)%20оригинальный",
        "Capacitor": "Capacitor%20Discharge%20translated%20(Русский%20—%20Разрядка%20конденсатора)",
        "ComplicatedWires": "Complicated%20Wires%20translated%20(Русский%20—%20Сложные%20провода)",
        "Knob": "Knob%20translated%20(Русский%20—%20Поворотная%20ручка)",
        "Maze": "Maze%20translated%20(Русский%20—%20Лабиринт)",
        "Memory": "Memory%20translated%20(Русский%20—%20Память)",
        "MorseCode": "Morse%20Code%20translated%20(Русский%20—%20Азбука%20Морзе)%20оригинальный",
        "Password": "Password%20translated%20(Русский%20—%20Пароль)%20оригинальный",
        "SimonSays": "Simon%20Says%20translated%20(Русский%20—%20Саймон%20говорит)",
        "VentGas": "Venting%20Gas%20translated%20(Русский%20—%20Выпуск%20газа)",
        "WhosonFirst": "Who%27s%20on%20First%20translated%20(Русский%20—%20Меня%20зовут%20Авас,%20а%20вас？)%20оригинальный",
        "WireSequence": "Wire%20Sequence%20translated%20(Русский%20—%20Последовательность%20проводов)"
    },
    #"pt-BR": [],
    #"zh-CN": [],
    #"da": [],
    #"de": [],
    #"eo": [],
    #"et": [],
    #"fi": [],
    #"he": [],
    #"it": [],
    #"ko": [],
    #"no": [],
    #"sv": [],
    #"th": []
}

allModsNames = ["The Button", "Wires", "Keypad", "Capacitor", "Complicated Wires", "Knob", "Maze", "Memory", "Morse Code", "Password", "Simon Says", "Vent Gas", "Who's on First", "Wire Sequence"]
allModsLinks = ["TheButton", "Wires", "Keypad", "Capacitor", "ComplicatedWires", "Knob", "Maze", "Memory", "MorseCode", "Password", "SimonSays", "VentGas", "WhosonFirst", "WireSequence"]
modPages = []

def loadPage(moduleName, lib, playerInfo):
    module = ""
    if moduleName in list(allModsRepo[playerInfo["sdLanguage"]].keys()):
        module = allModsRepo[playerInfo["sdLanguage"]][moduleName]
    else:
        module = allModsRepo["en"][moduleName]
    fullUrl = "https://ktane.timwi.de/HTML/" + module + ".html" + ("" if playerInfo["sdRuleSeed"] == 1 else "#" + str(playerInfo["sdRuleSeed"]))
    fullUrl = fullUrl.replace("%20", " ").replace("%26", "&").replace("%27", "'")

    #encoding fix
    parts = urllib.parse.urlsplit(fullUrl)
    encoded_path = urllib.parse.quote(parts.path)
    encoded_query = urllib.parse.quote(parts.query, safe="=&")
    encodedFullUrl = urllib.parse.urlunsplit((parts.scheme, parts.netloc, encoded_path, encoded_query, parts.fragment))

    modPage = urllib.request.urlopen(encodedFullUrl, context=ssl_context)
    htmlContent = modPage.read().decode("utf8")
    modPage.close()

    htmlContent = htmlContent.replace(
        '<link rel="stylesheet" type="text/css" href="css/font.css">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">'
    )
    #CORS problem
    #russianFontCss = urllib.request.urlopen("https://ktane.timwi.de/HTML/css/font-cyrillic.css", context=ssl_context).read().decode("utf8")
    #russianFontCss = russianFontCss.replace("..", "https://ktane.timwi.de/HTML")
    #htmlContent = htmlContent.replace(
    #    '<link rel="stylesheet" type="text/css" href="css/font-cyrillic.css">',
    #    '<style>' + russianFontCss + "</style>"
    #)
    #htmlContent = htmlContent.replace(
    #    '<link rel="stylesheet" type="text/css" href="https://ktane.timwi.de/HTML/css/font-cyrillic.css">',
    #    '<style>' + russianFontCss + "</style>"
    #)
    htmlContent = htmlContent.replace(
        '<link rel="stylesheet" type="text/css" href="css/font-cyrillic.css">',
        '<link rel="stylesheet" type="text/css" href="https://ktane.timwi.de/HTML/css/font-cyrillic.css">'
    )
    htmlContent = htmlContent.replace(
        '<link rel="stylesheet" type="text/css" href="css/normalize.css">',
        '<link rel="stylesheet" type="text/css" href="https://ktane.timwi.de/HTML/css/normalize.css">'
    )
    htmlContent = htmlContent.replace(
        '<link rel="stylesheet" type="text/css" href="css/Modules/',
        '<link rel="stylesheet" type="text/css" href="https://ktane.timwi.de/HTML/css/Modules/'
    )
    htmlContent = htmlContent.replace(
        '<link rel="stylesheet" type="text/css" href="css/main.css">',
        '<link rel="stylesheet" type="text/css" href="https://ktane.timwi.de/HTML/css/main.css">'
    )
    ktaneUtilsPage = urllib.request.urlopen("https://ktane.timwi.de/HTML/js/ktane-utils.js", context=ssl_context).read().decode("utf8")
    ktaneUtilsPage = ktaneUtilsPage.replace('e.src = scriptDir + "jquery.3.7.0.min.js"', 'e.src = "https://ktane.timwi.de/HTML/js/jquery.3.7.0.min.js"')
    htmlContent = htmlContent.replace(
        '<script src="js/ktane-utils.js"></script>',
        '<script>' + ktaneUtilsPage + '</script>'
    )
    ruleSeedPage = urllib.request.urlopen("https://ktane.timwi.de/HTML/js/ruleseed.js", context=ssl_context).read().decode("utf8")
    ruleSeedPage = ruleSeedPage.replace("this.seed = seed;", "this.seed = " + str(playerInfo["sdRuleSeed"]) + ";")
    ruleSeedPage = ruleSeedPage.replace('if (/^#(\\d+)$/.exec(window.location.hash) && (RegExp.$1 | 0) !== 1)', 'if (' + str(playerInfo["sdRuleSeed"] > 1).lower() + ')')
    ruleSeedPage = ruleSeedPage.replace('var seed = RegExp.$1 | 0;', 'var seed = ' + str(playerInfo["sdRuleSeed"]) + ";")
    if (playerInfo["sdRandomRuleSeed"]):
        ruleSeedPage = ruleSeedPage.replace("Array.from(document.getElementsByClassName('ruleseed-header')).forEach(x => { x.innerText = 'RULE SEED: ' + seed; });", "Array.from(document.getElementsByClassName('ruleseed-header')).forEach(x => { x.innerText = 'Archipelago'; });")
        ruleSeedPage = ruleSeedPage.replace("x.innerText = names[x.getAttribute('name-id')] + ' — rule seed: ' + seed;", "x.innerText = names[x.getAttribute('name-id')] + ' — Archipelago'")
    htmlContent = htmlContent.replace(
        "<script src='js/ruleseed.js'></script>",
        "<script>" + ruleSeedPage + "</script>"
    )
    htmlContent = htmlContent.replace(
        '<script src="js/ruleseed.js"></script>',
        "<script>" + ruleSeedPage + "</script>"
    )
    htmlContent = htmlContent.replace(
        '<script src="js/jquery.3.7.0.min.js"></script>',
        '<script src="https://ktane.timwi.de/HTML/js/jquery.3.7.0.min.js"></script>'
    )
    htmlContent = htmlContent.replace(
        '<script src="js/Utilities/svg-utils.js"></script>',
        '<script src="https://ktane.timwi.de/HTML/js/Utilities/svg-utils.js"></script>'
    )
    htmlContent = htmlContent.replace(
        'img/Comp',
        'https://ktane.timwi.de/HTML/img/Comp'
    )
    htmlContent = htmlContent.replace(
        'img/Keypad/',
        'https://ktane.timwi.de/HTML/img/Keypad/'
    )
    htmlContent = htmlContent.replace(
        'img/Who',
        'https://ktane.timwi.de/HTML/img/Who'
    )
    htmlContent = htmlContent.replace(
        'img/Morse',
        'https://ktane.timwi.de/HTML/img/Morse'
    )
    htmlContent = htmlContent.replace(
        "console.log('seed = ' + rnd.seed);",
        ""
    )
    lib[moduleName] = htmlContent
    print("Loaded " + moduleName)

def appendicesPage(lang):
    ktaneUtilsPage = urllib.request.urlopen("https://ktane.timwi.de/HTML/js/ktane-utils.js", context=ssl_context).read().decode("utf8")
    ktaneUtilsPage = ktaneUtilsPage.replace('e.src = scriptDir + "jquery.3.7.0.min.js"', 'e.src = "https://ktane.timwi.de/HTML/js/jquery.3.7.0.min.js"')
    appLoc = {
        "en": [
            "Indicators",
            "Appendix A: Indicator Identification Reference",
            "Labelled indicator lights can be found on the sides of the bomb casing.",
            "Common Indicators",
            "Page 1 of 3",
            "Batteries",
            "Appendix B: Battery Identification Reference",
            "Common battery types can be found within enclosures on the sides of the bomb casing.",
            "Battery",
            "Type",
            "AA",
            "D",
            "Page 2 of 3",
            "Ports",
            "Appendix C: Port Identification Reference",
            "Digital and analog ports can be found on sides of the bomb casing.",
            "Port",
            "Name",
            "DVI-D",
            "Parallel",
            "PS/2",
            "RJ-45",
            "Serial",
            "Stereo RCA",
            "Page 3 of 3"
        ],
        "cs": [
            "Indikátory (čeština) v1.4",
            "Dodatek A: Instrukce k identifikaci indikátorů (čeština)",
            "Pojmenované světelné indikátory jsou na stranách bomby.",
            "Běžné indikátory:",
            "Strana 1 z 3",
            "Baterie (čeština) v1.4",
            "Dodatek B: Instrukce k identifikaci baterií (čeština)",
            "Běžné typy baterií mohou být nalezeny v držácích na stranách krytu bomby.",
            "Baterie",
            "Typ",
            "AA",
            "D",
            "Strana 2 z 3",
            "Porty (čeština) v1.4",
            "Dodatek C: Instrukce k identifikaci portů (čeština)",
            "Digitální a analogové porty se mohou nacházet na stranách bomby.",
            "Port",
            "Jméno",
            "DVI-D",
            "Paralelní",
            "PS/2",
            "RJ-45",
            "Sériový",
            "Stereo RCA",
            "Strana 3 z 3"
        ],
        "es": [
            "Indicadores",
            "Apéndice A: Identificación del indicador",
            "Los indicadores lumínicos etiquetados se pueden encontrar a los lados de la carcasa de la bomba.",
            "Indicadores comunes",
            "Página 1 de 3",
            "Baterías",
            "Apéndice B: Identificación de la batería",
            "Se pueden encontrar tipos de baterías comunes conectadas a los lados de la carcasa de la bomba.",
            "Batería",
            "Tipo",
            "AA",
            "D",
            "Página 2 de 3",
            "Puertos",
            "Apéndice C: Identificación del puerto",
            "Los puertos analógicos y digitales se pueden encontrar a los lados de la carcasa de la bomba.",
            "Puerto",
            "Nombre",
            "DVI-D",
            "Paralelo",
            "PS/2",
            "RJ-45",
            "Serial",
            "RCA estéreo",
            "Página 3 de 3"
        ],
        "fr": [
            "Indicateurs",
            "Annexe A : Identification des Indicateurs",
            "Des indicateurs, composés d’un libellé et d’une lumière, peuvent se trouver sur les côtés de la bombe.",
            "Indicateurs ordinaires :",
            "Page 1 sur 3",
            "Piles",
            "Annexe B : Identification des Piles",
            "Des piles aux formats ordinaires peuvent se trouver sur les côtés de la bombe.",
            "Pile",
            "Type",
            "AA",
            "D",
            "Page 2 sur 3",
            "Ports",
            "Annexe C : Identification des Ports",
            "Des ports numériques et analogiques peuvent se trouver sur les côtés de la bombe.",
            "Port",
            "Nom",
            "DVI-D",
            "Parallèle",
            "PS/2",
            "RJ-45",
            "Série",
            "Stéréo RCA",
            "Page 3 sur 3"
        ],
        "ja": [
            "付録A",
            "付録A：インジケーター確認表",
            "ケースの側面にはインジケーターがついていることがある。",
            "インジケーター例",
            "ページ 1/3",
            "付録B",
            "付録B：バッテリー確認表",
            "ケースの側面には一般的な電池がついていることがある。",
            "バッテリー",
            "種類",
            "単3",
            "単1",
            "ページ 2/3",
            "付録C",
            "付録C：ポート確認表",
            "ケースの側面には各種のデジタル・アナログポートがついていることがある。",
            "ポート",
            "名称",
            "DVI-D",
            "パラレル",
            "PS/2",
            "RJ-45",
            "シリアル",
            "ステレオRCA",
            "ページ 3/3"
        ],
        "nl": [
            "Indicators",
            "Bijlage A: Indicatoridentificatie",
            "Gelabelde indicatorlichten kunnen aan de zijkant van de bom worden gevonden.",
            "Gebruikelijke Indicatoren",
            "Pagina 1 van 3",
            "Batterijen",
            "Bijlage B: Batterijidentificatie",
            "Gebruikelijke batterijsoorten kunnen aan de zijkanten van de bom worden gevonden.",
            "Batterij",
            "Type",
            "AA",
            "D",
            "Pagina 2 van 3",
            "Poorten",
            "Bijlage C: Poortidentificatie",
            "Deigitale en analoge poorten kunnen aan de zijkanten van de bom worden gevonden.",
            "Poort",
            "Naam",
            "DVI-D",
            "Parallel",
            "PS/2",
            "RJ-45",
            "Serieel",
            "Stereo RCA",
            "Pagina 3 van 3"
        ],
        "pl": [
            "Wskaźniki",
            "Załącznik A: Rozpoznawanie wskaźników",
            "Wskaźniki opatrzone napisami można znaleźć na bocznych ścianach obudowy bomby.",
            "Powszechne wskaźniki",
            "Strona 1 z 3",
            "Baterie",
            "Załącznik B: Rozpoznawanie baterii",
            "Popularne typy baterii można znaleźć w gniazdach na bocznych ścianach obudowy bomby.",
            "Bateria",
            "Typ",
            "AA",
            "D",
            "Strona 2 z 3",
            "Porty",
            "Załącznik C: Rozpoznawanie portów",
            "Porty cyfrowe i analogowe można znaleźć na bocznych ścianach obudowy bomby.",
            "Port",
            "Nazwa",
            "DVI-D",
            "Równoległy",
            "PS/2",
            "RJ-45",
            "Szeregowy",
            "Stereo RCA",
            "Strona 3 z 3"
        ],
        "ru": [
            "Индикаторы",
            "Приложение A: Определение индикатора",
            "По бокам корпуса бомбы можно обнаружить подписанные световые индикаторы.",
            "Часто встречающиеся индикаторы",
            "Стр. 1 из 3",
            "Элементы питания",
            "Приложение B: Определение элемента питания",
            "По бокам корпуса бомбы можно обнаружить стандартные элементы питания.",
            "Элемент питания",
            "Тип",
            "AA",
            "D",
            "Стр. 2 из 3",
            "Порты",
            "Приложение C: Определение порта",
            "По бокам корпуса бомбы можно обнаружить цифровые и аналоговые порты.",
            "Порт",
            "Название",
            "DVI-D",
            "Параллельный",
            "PS/2",
            "RJ-45",
            "Последовательный/Серийный",
            "Двухканальный RCA",
            "Стр. 3 из 3"
        ]
    }
    if lang not in list(appLoc.keys()):
        lang = "en"
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="initial-scale=1">
        <title>Appendices — Keep Talking and Nobody Explodes</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
        <link rel="stylesheet" type="text/css" href="https://ktane.timwi.de/HTML/css/normalize.css">
        <link rel="stylesheet" type="text/css" href="https://ktane.timwi.de/HTML/css/main.css">
        <link rel="stylesheet" type="text/css" href="https://ktane.timwi.de/HTML/css/Modules/Ports.css">
        <script>""" + ktaneUtilsPage + """</script>
        <style>
            td img { height: 80px; }
            .dark td img { filter: invert(87%); }
            .dark img { filter: invert(87%); }
        </style>
    </head>""" + f"""
    <body>
        <div class="section">
            <div class="page page-bg-07 appendix-indicators">
                <div class="page-header">
                    <span class="page-header-doc-title">Keep Talking and Nobody Explodes</span>
                    <span class="page-header-section-title">{appLoc[lang][0]}</span>
                </div>
                <div class="page-content">
                    <h2>{appLoc[lang][1]}</h2>
                    <p>{appLoc[lang][2]}</p>
                    <img src="https://ktane.timwi.de/HTML/img/Component/IndicatorWidget.svg" style="height: 5em; display: block; margin: .6em 0 0">
                    <h3>{appLoc[lang][3]}</h3>
                    <ul><li>SND</li><li>CLR</li><li>CAR</li><li>IND</li><li>FRQ</li><li>SIG</li><li>NSA</li><li>MSA</li><li>TRN</li><li>BOB</li><li>FRK</li></ul>
                </div>
                <div class="page-footer relative-footer">{appLoc[lang][4]}</div>
            </div>
        </div>
        <div class="page page-bg-01 appendix-batteries">
            <div class="page-header">
                <span class="page-header-doc-title">Keep Talking and Nobody Explodes</span>
                <span class="page-header-section-title">{appLoc[lang][5]}</span>
            </div>
            <div class="page-content">
                <h2>{appLoc[lang][6]}</h2>
                <p>{appLoc[lang][7]}</p>
                <table style="margin-top: 1em">
                    <tr><th>{appLoc[lang][8]}</th><th>{appLoc[lang][9]}</th></tr>
                    <tr><td><img src="https://ktane.timwi.de/HTML/img/appendix-batteries/Battery-AA.svg" style="width: 4.09375em; height: 6.18125em"></td><td>{appLoc[lang][10]}</td></tr>
                    <tr><td><img src="https://ktane.timwi.de/HTML/img/appendix-batteries/Battery-D.svg" style="width: 4.09375em; height: 5.553125em"></td><td>{appLoc[lang][11]}</td></tr>
                </table>
            </div>
            <div class="page-footer relative-footer">{appLoc[lang][12]}</div>
        </div>
        <div class="page page-bg-02 appendix-ports">
            <div class="page-header">
                <span class="page-header-doc-title">Keep Talking and Nobody Explodes</span>
                <span class="page-header-section-title">{appLoc[lang][13]}</span>
            </div>
            <div class="page-content">
                <h2>{appLoc[lang][14]}</h2>
                <p>{appLoc[lang][15]}</p>
                <table>
                    <tr><th>{appLoc[lang][16]}</th><th>{appLoc[lang][17]}</th></tr>
                    <tr><td><img src="https://ktane.timwi.de/HTML/img/appendix-ports/DVI-D.svg" style="height:60px"></td><td>{appLoc[lang][18]}</td></tr>
                    <tr><td><img src="https://ktane.timwi.de/HTML/img/appendix-ports/Parallel.svg" style="height:60px"></td><td>{appLoc[lang][19]}</td></tr>
                    <tr><td><img src="https://ktane.timwi.de/HTML/img/appendix-ports/PS2.svg"></td><td>{appLoc[lang][20]}</td></tr>
                    <tr><td><img src="https://ktane.timwi.de/HTML/img/appendix-ports/RJ-45.svg"></td><td>{appLoc[lang][21]}</td></tr>
                    <tr><td><img src="https://ktane.timwi.de/HTML/img/appendix-ports/Serial.svg" style="height:60px"></td><td>{appLoc[lang][22]}</td></tr>
                    <tr><td><img src="https://ktane.timwi.de/HTML/img/appendix-ports/Stereo RCA.svg"></td><td>{appLoc[lang][23]}</td></tr>
                </table>
            </div>
            <div class="page-footer relative-footer">{appLoc[lang][24]}</div>
        </div>
    </body>
    </html>
    """

def connectionPage(playerInfo):
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AP KTANE - Connection</title>
            <meta charset="UTF-8">

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
            <style>
                body {
                    background-color: #222326;
                    color: #FFFFFF;
                    font-family: "Special Elite";
                }
                img {
                    width: 100%;
                }
                input {
                    font-size: 24px;
                }
                label {
                    font-size: 24px;
                    margin-bottom: .0rem;
                }
                span {
                    width: 100%;
                    display: block;
                }
                textarea {
                    width: 100%;
                }

                .button {
                    background-color: #BA4423;
                    border-radius: 2.5em;
                    font-size: 36px;
                    width: 100%;
                    margin-top: 5px;
                    margin-bottom: 10px;
                }
                .container {
                    margin: 0px;
                    max-width: 100%;
                }
                .connection-section {
                    background-color: #FFFFFF;
                    color: #222326;
                    border-radius: 2.5em;
                    margin: 20px 0px 10px 0px;
                }
                .error {
                    border-color: #FF0000;
                }
                .input-field-row {
                    margin: 3px 0px;
                }
                .text-input {
                    width: 100%;
                }
                .title {
                    font-size: 48px;
                    text-align: center;
                }
            </style>
            <script>
                function storeCookies(urlStr, portStr, nameStr) {
                    const d = new Date();
                    d.setTime(d.getTime() + 1209600000); //two weeks
                    coo = "url=" + urlStr + ";port=" + portStr + ";slotName=" + nameStr + ";expires=" + d.toUTCString() + ";path=/"
                    //document.cookie = coo;
                    document.cookie = "url=" + urlStr + ";expires=" + d.toUTCString() + ";path=/"
                    document.cookie = "port=" + portStr + ";expires=" + d.toUTCString() + ";path=/"
                    document.cookie = "slotName=" + nameStr + ";expires=" + d.toUTCString() + ";path=/"
                }

                function getCookiesList() {
                    let decodedCookies = decodeURIComponent(document.cookie);
                    let fullCookieList = decodedCookies.split(";");
                    const cookieList = [];
                    cookieList["url"] = "";
                    cookieList["port"] = "";
                    cookieList["slotName"] = "";
                    for(let i = 0; i < fullCookieList.length; i++) {
                        let coo = fullCookieList[i]
                        while (coo.charAt(0) == ' ') {
                            coo = coo.substring(1);
                        }
                        cParts = coo.split("=");
                        cookieList[cParts[0]] = cParts[1];
                    }
                    return cookieList;
                }

                document.addEventListener("DOMContentLoaded", function() {
                    let myCookies = getCookiesList();
                    if (myCookies["url"] != "") {
                        document.getElementById("txt-server-url").value = myCookies["url"];
                    }
                    if (myCookies["port"] != "") {
                        document.getElementById("txt-server-port").value = myCookies["port"];
                    }
                    if (myCookies["slotName"] != "") {
                        document.getElementById("txt-slot-name").value = myCookies["slotName"];
                    }
                    document.getElementById("connect-button").addEventListener("click", function() {
                        url = document.getElementById("txt-server-url");
                        port = document.getElementById("txt-server-port");
                        slotName = document.getElementById("txt-slot-name");
                        password = document.getElementById("txt-server-password");
                        var filled = true;
                        if (url.value == "") {
                            url.classList.add("error");
                            filled = false;
                        }
                        else {
                            url.classList.remove("error");
                        }
                        if (port.value == "") {
                            port.classList.add("error");
                            filled = false;
                        }
                        else if (!/^\\d+$/.test(port.value)) {
                            port.classList.add("error");
                            filled = false;
                        }
                        else {
                            port.classList.remove("error");
                        }
                        if (slotName.value == "") {
                            slotName.classList.add("error");
                            filled = false;
                        }
                        else {
                            slotName.classList.remove("error");
                        }
                        if (filled) {
                            storeCookies(url.value, port.value, slotName.value);
                            document.getElementById("frm-connection").submit();
                        }
                    })
                });
            </script>
        </head>
        """+f"""
        <body>
            <div class="container">
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img src="https://archipelago.gg/static/static/branding/header-logo.svg" alt="AP logo">
                    </div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img src="https://www.bombmanual.com/img/header.png" alt="KTANE logo">
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8">
                        <form method="POST" id="frm-connection" accept-charset="UTF-8">
                            <input type="hidden" name="post-command" value="connect">
                            <div class="container connection-section">
                                <div class="row">
                                    <div class="col-12">
                                        <span class="title">Connection:</span>
                                    </div>
                                </div>
                                <div class="row input-field-row">
                                    <div class="col-0 col-xl-1"></div>
                                    <div class="col-12 col-sm-4 col-xl-3 my-auto"><label for="txt-server-url">Server URL:</label></div>
                                    <div class="col-12 col-sm-8 col-xl-7">
                                        <input type="text" id="txt-server-url" name="server-url" class="text-input" value="{playerInfo["cdUrl"]}">
                                    </div>
                                    <div class="col-0 col-xl-1"></div>
                                </div>
                                <div class="row input-field-row">
                                    <div class="col-0 col-xl-1"></div>
                                    <div class="col-12 col-sm-4 col-xl-3 my-auto"><label for="txt-server-port">Server Port:</label></div>
                                    <div class="col-12 col-sm-8 col-xl-7">
                                        <input type="text" id="txt-server-port" name="server-port" class="text-input" value="{playerInfo["cdPort"]}">
                                    </div>
                                    <div class="col-0 col-xl-1"></div>
                                </div>
                                <div class="row input-field-row">
                                    <div class="col-0 col-xl-1"></div>
                                    <div class="col-12 col-sm-4 col-xl-3 my-auto"><label for="txt-slot-name">Slot Name:</label></div>
                                    <div class="col-12 col-sm-8 col-xl-7">
                                        <input type="text" id="txt-slot-name" name="slot-name" class="text-input" value="{playerInfo["cdName"]}">
                                    </div>
                                    <div class="col-0 col-xl-1"></div>
                                </div>
                                <div class="row input-field-row">
                                    <div class="col-0 col-xl-1"></div>
                                    <div class="col-12 col-sm-4 col-xl-3 my-auto"><label for="txt-server-password">Server Password:</label></div>
                                    <div class="col-12 col-sm-8 col-xl-7">
                                        <input type="text" id="txt-server-password" name="server-password" class="text-input" value="{playerInfo["cdPass"]}">
                                    </div>
                                    <div class="col-0 col-xl-1"></div>
                                </div>
                                <div class="row">
                                    <div class="col-0 col-sm-2 col-lg-4"></div>
                                    <div class="col-12 col-sm-8 col-lg-4"><input id="connect-button" class="button" type="button" value="Connect"></div>
                                    <div class="col-0 col-sm-2 col-lg-4"></div>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8">Version {versionNumber}</div>
                    <div class="col-0 col-lg-2"></div>
                </div>
            </div>
        </body>
    </html>
    """

def mainPage(playerInfo):
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AP KTANE - Main Page</title>
            <meta charset="UTF-8">

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
            <style>
                body {
                    background-color: #222326;
                    color: #FFFFFF;
                    font-family: "Special Elite";
                }
                img.responsive {
                    height: 90px;
                }
                @media (max-width: 767px) {
                    img.responsive {
                        height: 50px;
                    }
                }

                .button {
                    background-color: #BA4423;
                    border-radius: 2.5em;
                    font-size: 36px;
                    width: 100%;
                    margin-top: 5px;
                    margin-bottom: 10px;
                }
                .col-md-11 {
                    width: 12.499999995%;
                    flex: 0 0 12.499%;
                    max-width: 12.499%;
                }
                .container {
                    margin: 0px;
                    max-width: 100%;
                }
                .mod-icon {
                    margin: auto;
                    display: block;
                }
                .mod-text {
                    height: 50px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                }
                @media (max-width: 767px) {
                    .mod-text {
                        justify-content: left;
                        text-align: left;
                    }
                }
                .module {
                    background-color: #333334;
                    color: #000000;
                    margin: 3px;
                    padding: 3px;
                    padding-top: 6px;
                }
                .padding-correction {
                    padding-right: 5px;
                    padding-left: 5px;
                }
                .title-icon {
                    max-height: 100px;
                    margin-left: auto;
                    margin-right: auto;
                    width: 100%;
                    object-fit: contain;
                }
                .unlocked {
                    background-color: #666666 !important;
                    color: #FFFFFF !important;
                }
                .username {
                    font-size: 24px;
                    text-align: center;
                    width: 100%;
                    display: block;
                }
            </style>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    document.getElementById("disconnect-button").addEventListener("click", function() {
                        document.getElementById("frm-disconnect").submit();
                    });

                    """ + ("refreshPage();" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and (len(playerInfo["unlockedModules"]) < 14)) else "") + """
                });

                """ + ("""function refreshPage() {
                    setTimeout(function() {
                        location.reload();
                    }, 15000);
                }""" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and (len(playerInfo["unlockedModules"]) < 14)) else "") + """
            </script>
        </head>"""+f"""
        <body>
            <div class="container">
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://archipelago.gg/static/static/branding/header-logo.svg" alt="AP logo">
                    </div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://www.bombmanual.com/img/header.png" alt="KTANE logo">
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8">
                        <span class="username">{playerInfo["name"]}</span>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8">
                        <div class="container">
                            <div class="row">
                                <div class="col-0 col-md-11"></div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/TheButton" target="_blank">
                                        <div class="container module unlocked">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/The%20Button.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    The Button
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/Keypad" target="_blank">
                                        <div class="container module unlocked">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Keypad.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Keypad
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/Wires" target="_blank">
                                        <div class="container module unlocked">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Wires.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Wires
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-0 col-md-11"></div>
                            </div>
                            <div class="row">
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/Maze" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("Maze" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Maze.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Maze
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/Memory" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("Memory" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Memory.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Memory
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/SimonSays" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("SimonSays" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Simon%20Says.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Simon Says
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/WhosonFirst" target="_blank">
                                        <div class="container module  {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("WhosonFirst" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Who%27s%20on%20First.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Who's on First
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/ComplicatedWires" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("ComplicatedWires" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Complicated%20Wires.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Complicated Wires
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/MorseCode" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("MorseCode" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Morse%20Code.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Morse Code
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/Password" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("Password" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Password.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Password
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/WireSequence" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("WireSequence" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Wire%20Sequence.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Wire Sequence
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/Capacitor" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("Capacitor" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Capacitor%20Discharge.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Capacitor
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/Knob" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("Knob" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Knob.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Knob
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/VentGas" target="_blank">
                                        <div class="container module {"unlocked" if ((playerInfo is not None) and ("unlockedModules" in playerInfo.keys()) and ("VentGas" in playerInfo["unlockedModules"]))else ""}">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/Icons/Venting%20Gas.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Vent Gas
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-12 col-md-3 padding-correction">
                                    <a href="/Appendices" target="_blank">
                                        <div class="container module unlocked">
                                            <div class="row">
                                                <div class="col-3 col-sm-2 col-md-12">
                                                    <img class="mod-icon responsive" src="https://ktane.timwi.de/HTML/img/manual.png">
                                                </div>
                                                <div class="col-9 col-sm-10 col-md-12 my-auto mod-text">
                                                    Appendices
                                                </div>
                                            </div>
                                        </div>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-sm-2 col-md-4"></div>
                    <div class="col-12 col-sm-8 col-md-4">
                        <form method="POST" id="frm-disconnect">
                            <input type="hidden" name="post-command" value="disconnect">
                            <input id="disconnect-button" class="button" type="button" value="Disconnect">
                        </form>
                    </div>
                    <div class="col-0 col-sm-2 col-md-4"></div>
                </div>
            </div>
        </body>
    </html>
    """

def notUnlockedPage(playerInfo, module):
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AP KTANE - Not Unlocked Modules</title>
            <meta charset="UTF-8">

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
            <style>
                body {
                    background-color: #222326;
                    color: #FFFFFF;
                    font-family: "Special Elite";
                }

                .center-text {
                    text-align: center;
                }
                .container {
                    margin: 0px;
                    max-width: 100%;
                }
                .locked-sign {
                    color: #FF0000;
                    font-weight: 900;
                    text-align: center;
                    font-size: 156px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .title-icon {
                    max-height: 100px;
                    margin-left: auto;
                    margin-right: auto;
                    width: 100%;
                    object-fit: contain;
                }
                .username {
                    font-size: 24px;
                    text-align: center;
                    width: 100%;
                    display: block;
                }
            </style>
        </head>"""+f"""
        <body>
            <div class="container">
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://archipelago.gg/static/static/branding/header-logo.svg" alt="AP logo">
                    </div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://www.bombmanual.com/img/header.png" alt="KTANE logo">
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8">
                        <span class="username">{playerInfo["name"]}</span>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <span class="locked-sign">🔒</span>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12 center-text">
                        The module {module} is not unlocked yet.
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

def notFoundPage():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AP KTANE - Not Found</title>
            <meta charset="UTF-8">

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
            <style>
                body {
                    background-color: #222326;
                    color: #FFFFFF;
                    font-family: "Special Elite";
                }

                .button {
                    background-color: #BA4423;
                    border-radius: 2.5em;
                    font-size: 36px;
                    width: 100%;
                    margin-top: 5px;
                    margin-bottom: 10px;
                }
                .center-text {
                    text-align: center;
                }
                .container {
                    margin: 0px;
                    max-width: 100%;
                }
                .search-sign {
                    color: #FF0000;
                    font-weight: 900;
                    text-align: center;
                    font-size: 156px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .title-icon {
                    max-height: 100px;
                    margin-left: auto;
                    margin-right: auto;
                    width: 100%;
                    object-fit: contain;
                }
                .username {
                    font-size: 24px;
                    text-align: center;
                    width: 100%;
                    display: block;
                }
            </style>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    document.getElementById("main-page-button").addEventListener("click", function() {
                        document.getElementById("frm-main-page").submit();
                    });
                });
            </script>
        </head>
        """+f"""
        <body>
            <div class="container">
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://archipelago.gg/static/static/branding/header-logo.svg" alt="AP logo">
                    </div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://www.bombmanual.com/img/header.png" alt="KTANE logo">
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8">
                        <span class="username">404 - Not Found</span>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <span class="search-sign">🔍</span>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12 center-text">
                        This page wasn't found.
                    </div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8 center-text">
                        <form method="POST" id="frm-main-page">
                            <input type="hidden" name="post-command" value="main-page">
                            <input id="main-page-button" class="button" type="button" value="Return to safety">
                        </form>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
            </div>
        </body>
    </html>
    """

def notConnectedPage():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AP KTANE - Not Connected</title>
            <meta charset="UTF-8">

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
            <style>
                body {
                    background-color: #222326;
                    color: #FFFFFF;
                    font-family: "Special Elite";
                }

                .button {
                    background-color: #BA4423;
                    border-radius: 2.5em;
                    font-size: 36px;
                    width: 100%;
                    margin-top: 5px;
                    margin-bottom: 10px;
                }
                .center-text {
                    text-align: center;
                }
                .container {
                    margin: 0px;
                    max-width: 100%;
                }
                .user-sign {
                    color: #FF0000;
                    font-weight: 900;
                    text-align: center;
                    font-size: 156px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .title-icon {
                    max-height: 100px;
                    margin-left: auto;
                    margin-right: auto;
                    width: 100%;
                    object-fit: contain;
                }
                .username {
                    font-size: 24px;
                    text-align: center;
                    width: 100%;
                    display: block;
                }
            </style>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    document.getElementById("main-page-button").addEventListener("click", function() {
                        document.getElementById("frm-main-page").submit();
                    });
                });
            </script>
        </head>
        <body>
            <div class="container">
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://archipelago.gg/static/static/branding/header-logo.svg" alt="AP logo">
                    </div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://www.bombmanual.com/img/header.png" alt="KTANE logo">
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8">
                        <span class="username">404 - Not Connected</span>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <span class="user-sign">👤</span>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12 center-text">
                        You are not connected to the Archipelago server.
                    </div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8 center-text">
                        <form method="POST" id="frm-main-page">
                            <input type="hidden" name="post-command" value="main-page">
                            <input id="main-page-button" class="button" type="button" value="Return to connection page">
                        </form>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
            </div>
        </body>
    </html>
    """

def errorConnectionPage(errorType, errorMessage):
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AP KTANE - Not Connected</title>
            <meta charset="UTF-8">

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
            <style>
                body {
                    background-color: #222326;
                    color: #FFFFFF;
                    font-family: "Special Elite";
                }

                .button {
                    background-color: #BA4423;
                    border-radius: 2.5em;
                    font-size: 36px;
                    width: 100%;
                    margin-top: 5px;
                    margin-bottom: 10px;
                }
                .center-text {
                    text-align: center;
                }
                .container {
                    margin: 0px;
                    max-width: 100%;
                }
                .error-sign {
                    color: #FF0000;
                    font-weight: 900;
                    text-align: center;
                    font-size: 156px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .title-icon {
                    max-height: 100px;
                    margin-left: auto;
                    margin-right: auto;
                    width: 100%;
                    object-fit: contain;
                }
                .username {
                    font-size: 24px;
                    text-align: center;
                    width: 100%;
                    display: block;
                }
            </style>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    document.getElementById("disconnect-button").addEventListener("click", function() {
                        document.getElementById("frm-disconnect").submit();
                    });
                });
            </script>
        </head>"""+f"""
        <body>
            <div class="container">
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://archipelago.gg/static/static/branding/header-logo.svg" alt="AP logo">
                    </div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://www.bombmanual.com/img/header.png" alt="KTANE logo">
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8">
                        <span class="username">Error in connection</span>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <span class="error-sign">❌</span>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12 center-text">
                        {str(errorType)}
                    </div>
                </div>
                <div class="row">
                    <div class="col-12 center-text">
                        {str(errorMessage)}
                    </div>
                </div>
                <div class="row">
                    <div class="col-0 col-sm-2 col-md-4"></div>
                    <div class="col-12 col-sm-8 col-md-4">
                        <form method="POST" id="frm-disconnect">
                            <input type="hidden" name="post-command" value="disconnect">
                            <input id="disconnect-button" class="button" type="button" value="Return to connection">
                        </form>
                    </div>
                    <div class="col-0 col-sm-2 col-md-4"></div>
                </div>
            </div>
        </body>
    </html>
    """

def badPostPage():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>AP KTANE - Not Found</title>
            <meta charset="UTF-8">

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Special+Elite&display=swap" rel="stylesheet">
            <style>
                body {
                    background-color: #222326;
                    color: #FFFFFF;
                    font-family: "Special Elite";
                }

                .button {
                    background-color: #BA4423;
                    border-radius: 2.5em;
                    font-size: 36px;
                    width: 100%;
                    margin-top: 5px;
                    margin-bottom: 10px;
                }
                .center-text {
                    text-align: center;
                }
                .container {
                    margin: 0px;
                    max-width: 100%;
                }
                .search-sign {
                    color: #FF0000;
                    font-weight: 900;
                    text-align: center;
                    font-size: 156px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .title-icon {
                    max-height: 100px;
                    margin-left: auto;
                    margin-right: auto;
                    width: 100%;
                    object-fit: contain;
                }
                .username {
                    font-size: 24px;
                    text-align: center;
                    width: 100%;
                    display: block;
                }
            </style>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    document.getElementById("main-page-button").addEventListener("click", function() {
                        document.getElementById("frm-main-page").submit();
                    });
                });
            </script>
        </head>
        """+f"""
        <body>
            <div class="container">
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://archipelago.gg/static/static/branding/header-logo.svg" alt="AP logo">
                    </div>
                    <div class="col-12 col-sm-6 col-lg-4 my-auto">
                        <img class="title-icon" src="https://www.bombmanual.com/img/header.png" alt="KTANE logo">
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8">
                        <span class="username">Bad HTML Post</span>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <span class="search-sign">✉️</span>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12 center-text">
                        The HTML post that was used to transfer data to the server contained invalid data.
                    </div>
                </div>
                <div class="row">
                    <div class="col-0 col-lg-2"></div>
                    <div class="col-12 col-lg-8 center-text">
                        <form method="POST" id="frm-main-page">
                            <input type="hidden" name="post-command" value="main-page">
                            <input id="main-page-button" class="button" type="button" value="Return to safety">
                        </form>
                    </div>
                    <div class="col-0 col-lg-2"></div>
                </div>
            </div>
        </body>
    </html>
    """

#class MyHttpRequestHandler(socketserver.StreamRequestHandler):
class MyHttpRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, player_info=None, **kwargs):
        self.playerInfo = player_info
        super().__init__(*args, **kwargs)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-api-key,Content-Type")

    def _inner_func(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self._send_cors_headers()
        self.end_headers()

    def _scan_for_TypedTuples(self, obj: typing.Any) -> typing.Any:
        if isinstance(obj, tuple) and hasattr(obj, "_fields"):  # NamedTuple is not actually a parent class
            data = obj._asdict()
            data["class"] = obj.__class__.__name__
            return data
        if isinstance(obj, (tuple, list, set, frozenset)):
            return tuple(self._scan_for_TypedTuples(o) for o in obj)
        if isinstance(obj, dict):
            return {key: self._scan_for_TypedTuples(value) for key, value in obj.items()}
        return obj

    async def _keep_alive(self, ws, playerInfo):
        second_counter = 0
        try:
            while playerInfo["connected"]:
                if playerInfo["slotNumber"] != -1:
                    if second_counter > 100:
                        await ws.send(json.JSONEncoder(ensure_ascii=False,check_circular=False,separators=(",",":")).encode(self._scan_for_TypedTuples([{"cmd": "Bounce", "slots": [self.playerInfo["slotNumber"]]}])))
                        second_counter = 0
                await asyncio.sleep(1)
                second_counter += 1
        except Exception as e:
            print("Keep alive error:\n" + str(e))

    async def _message_receiver(self, ws, playerInfo):
        try:
            while playerInfo["connected"]:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=1)
                    asyncio.create_task(self._process_messages(message, playerInfo))
                except asyncio.TimeoutError:
                    continue
        except Exception as e:
            print("Message receiver error:\n" + str(e))

    async def _process_messages(self, msg, playerInfo):
        for recept in json.loads(msg):
            if "cmd" not in recept.keys():
                #not an important message
                continue
            elif recept["cmd"] == "ConnectionRefused":
                await asyncio.create_task(self._connection_refused(recept, playerInfo))
                continue
            elif recept["cmd"] == "Connected":
                await asyncio.create_task(self._finalize_connect(recept, playerInfo))
                continue
            elif recept["cmd"] == "PrintJSON":
                if ("type" in recept.keys()) and (recept["type"] == "ItemSend"):
                    continue #don't want to print this
                print((recept["data"][0])["text"])
                continue
            elif recept["cmd"] == "Bounced":
                continue
            elif recept["cmd"] == "RoomUpdate":
                continue
            elif recept["cmd"] == "ReceivedItems":
                await asyncio.create_task(self._receive_item(recept, playerInfo))
                continue
            else:
                print(f"Received Random Message: {recept}")
                continue

    async def _receive_item(self, itemData, playerInfo):
        moduleList = ["Complicated Wires", "Maze", "Memory", "Morse Code", "Password", "Simon Says", "Who's on First", "Wire Sequence", "Capacitor", "Knob", "Vent Gas"]
        linkList = ["ComplicatedWires", "Maze", "Memory", "MorseCode", "Password", "SimonSays", "WhosonFirst", "WireSequence", "Capacitor", "Knob", "VentGas"]
        for item in itemData["items"]:
            itemId = item["item"]
            if (itemId < 71301001) or (itemId > 71301011):
                #not a module
                continue
            adaptedItemId = itemId - 71301001
            if (linkList[adaptedItemId] not in playerInfo["unlockedModules"]):
                print(f"Received Module {moduleList[adaptedItemId]}")
                playerInfo["unlockedModules"] += [linkList[adaptedItemId]]

    def _connect(self, post_data):
        serverUrl = ""
        serverPort = ""
        slotName = ""
        serverPassword = ""
        errorPage = False
        if "server-url" in post_data.keys():
            serverUrl = post_data["server-url"][0]
            self.playerInfo["cdUrl"] = serverUrl
        else:
            errorPage = True
            self.playerInfo["cdUrl"] = ""
        if "server-port" in post_data.keys():
            serverPort = post_data["server-port"][0]
            self.playerInfo["cdPort"] = serverPort
        else:
            errorPage = True
            self.playerInfo["cdPort"] = ""
        if "slot-name" in post_data.keys():
            slotName = post_data["slot-name"][0]
            self.playerInfo["cdName"] = slotName
        else:
            errorPage = True
            self.playerInfo["cdName"] = ""
        if "server-password" in post_data.keys():
            serverPassword = post_data["server-password"][0]
            self.playerInfo["cdPass"] = serverPassword
        else:
            serverPassword = None
            self.playerInfo["cdPass"] = ""

        if errorPage:
            _wrong_post(post_data)
            return

        asyncio.run_coroutine_threadsafe(self._connect_to_websocket(serverUrl, serverPort, slotName, serverPassword, self.playerInfo), background_loop)

        while (self.playerInfo["connectionResult"] is None):
            pass

        if (self.playerInfo["connectionResult"] == "success"):
            setModPages(self.playerInfo)

            new_path = "/MainPage"
            self.send_response(303)
            self.send_header("Location", new_path)
            self._send_cors_headers()
            self.end_headers()
        else:
            new_path = "/Error"
            self.send_response(303)
            self.send_header("Location", new_path)
            self._send_cors_headers()
            self.end_headers()

    async def _connect_to_websocket(self, serverUrl, serverPort, slotName, serverPassword, playerInfo):
        includePrefix = ("ws://" in serverUrl) or ("wss://" in serverUrl)
        lastTime = includePrefix
        while True:
            prefix = "" if includePrefix else ("wss://" if lastTime else "ws://")
            fullUrl = f"{prefix}{serverUrl}:{serverPort}"
            try:
                async def _inner_connect():
                    if "wss://" in str(fullUrl):
                        ws = await websockets.connect(fullUrl, ssl=ssl_context, ping_timeout=None, ping_interval=None)
                        return ws
                    else:
                        ws = await websockets.connect(fullUrl, ping_timeout=None, ping_interval=None)
                        return ws

                ws = await asyncio.wait_for(_inner_connect(), timeout=5)

                try:
                    wsconJson = await ws.recv()
                    wsconData = (json.loads(wsconJson))[0]
                    if "cmd" in wsconData.keys() and wsconData["cmd"] == "RoomInfo":
                        import uuid
                        infos = [{
                            "cmd": "Connect",
                            "password": serverPassword,
                            "name": slotName,
                            "version": apVersion,
                            "tags": ["ExpertManuals"],
                            "items_handling": 0b111,
                            "uuid": uuid.getnode(),
                            "game": "Keep Talking and Nobody Explodes",
                            "slot_data": True
                        }]
                        playerInfo["connected"] = True
                        keep_alive_task = asyncio.create_task(self._keep_alive(ws, playerInfo))
                        message_receiver_task = asyncio.create_task(self._message_receiver(ws, playerInfo))
                        await ws.send(json.JSONEncoder(ensure_ascii=False,check_circular=False,separators=(",",":")).encode(self._scan_for_TypedTuples(infos)))
                        await keep_alive_task
                        await message_receiver_task
                        playerInfo["name"] = ""
                    else:
                        print("NOT FOUND")
                except Exception as e:
                    print(str(type(e)))
                    print(str(e))
                finally:
                    await ws.close()

                break
            except asyncio.TimeoutError:
                if not lastTime:
                    lastTime = not lastTime
                else:
                    playerInfo["connectionError"] = ["TimeoutError", "Connection attempt timed out"]
                    playerInfo["connectionResult"] = "failure"
                    break
            except websockets.exceptions.InvalidMessage as e:
                if not lastTime:
                    lastTime = not lastTime
                else:
                    playerInfo["connectionError"] = ["Invalid Messages", str(e)]
                    playerInfo["connectionResult"] = "failure"
                    break
            except Exception as e:
                playerInfo["connectionError"] = [str(type(e)), str(e)]
                playerInfo["connectionResult"] = "failure"
                break

    async def _finalize_connect(self, apConData, playerInfo):
        print("CONNECTED")
        self.playerInfo["slotNumber"] = apConData["slot"]
        pl = [f for f in apConData["players"] if f["slot"] == self.playerInfo["slotNumber"]][0]
        self.playerInfo["name"] = pl["alias"]
        if apConData["slot_data"] is None:
            self.playerInfo["sdRuleSeed"] = 1
            self.playerInfo["sdRandomRuleSeed"] = False
            self.playerInfo["sdHardlockModules"] = True
            self.playerInfo["sdLanguage"] = "en"
        else:
            sd = apConData["slot_data"]
            if "rule_seed" in sd.keys():
                if sd["rule_seed"] is None:
                    self.playerInfo["sdRuleSeed"] = 1
                else:
                    self.playerInfo["sdRuleSeed"] = sd["rule_seed"]
            else:
                self.playerInfo["sdRuleSeed"] = 1
            if "random_rule_seed" in sd.keys():
                if sd["random_rule_seed"] is None:
                    self.playerInfo["sdRandomRuleSeed"] = False
                else:
                    self.playerInfo["sdRandomRuleSeed"] = (sd["random_rule_seed"] == 1)
            else:
                self.playerInfo["sdRandomRuleSeed"] = False
            if "hardlock_modules" in sd.keys():
                if sd["hardlock_modules"] is None:
                    self.playerInfo["sdHardlockModules"] = True
                else:
                    self.playerInfo["sdHardlockModules"] = (sd["hardlock_modules"] == 1)
            else:
                self.playerInfo["sdHardlockModules"] = True
            if "manuals_language" in sd.keys():
                if sd["manuals_language"] is None:
                    self.playerInfo["sdLanguage"] = "en"
                else:
                    self.playerInfo["sdLanguage"] = list(allModsRepo.keys())[sd["manuals_language"]]
            else:
                self.playerInfo["sdLanguage"] = "en"
        if not self.playerInfo["sdHardlockModules"]:
            self.playerInfo["unlockedModules"] += ["Capacitor", "VentGas"]
        self.playerInfo["connectionResult"] = "success"

    async def _connection_refused(self, errorData, playerInfo):
        playerInfo["connected"] = False
        playerInfo["connectionError"] = ["Connection Refused", "\n".join(errorData["errors"])]
        playerInfo["connectionResult"] = "failure"

    def _disconnect(self, post_data):
        self.playerInfo["connected"] = False

        self.playerInfo["name"] = ""
        self.playerInfo["slotNumber"] = -1
        self.playerInfo["sdRuleSeed"] = -1
        self.playerInfo["sdRandomRuleSeed"] = False
        self.playerInfo["sdHardlockModules"] = True
        self.playerInfo["sdLanguage"] = "en"
        self.playerInfo["unlockedModules"] = ["TheButton", "Keypad", "Wires"]
        self.playerInfo["connectionResult"] = None
        self.playerInfo["connectionError"] = ["", ""]

        new_path = "/"
        self.send_response(303)
        self.send_header("Location", new_path)
        self._send_cors_headers()
        self.end_headers()

    def _return_to_main_page(self, post_data):
        new_path = "/"
        self.send_response(303)
        self.send_header("Location", new_path)
        self._send_cors_headers()
        self.end_headers()

    def _wrong_post(self, post_data):
        new_path = "/WrongPost"
        self.send_response(303)
        self.send_header("Location", new_path)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        try:
            if self.path == "/":
                if self.playerInfo["name"] != "":
                    #already connected
                    new_path = "/MainPage"
                    self.send_response(303)
                    self.send_header("Location", new_path)
                    self._send_cors_headers()
                    self.end_headers()
                    return None
                self._inner_func()
                self.wfile.write(connectionPage(self.playerInfo).encode("utf8"))
            elif self.path == "/MainPage":
                self._inner_func()
                if self.playerInfo["name"] == "":
                    #not connected
                    self.wfile.write(notConnectedPage().encode("utf8"))
                else:
                    self.wfile.write(mainPage(self.playerInfo).encode("utf8"))
            elif (self.path == "/Error") and (self.playerInfo["connectionResult"] == "failure"):
                self._inner_func()
                self.wfile.write(errorConnectionPage(self.playerInfo["connectionError"][0], self.playerInfo["connectionError"][1]).encode("utf8"))
            elif (self.path == "/WrongPost"):
                self._inner_func()
                self.wfile.write(badPostPage().encode("utf8"))
            elif (self.path == "/Appendices"):
                self._inner_func()
                self.wfile.write(appendicesPage(self.playerInfo["sdLanguage"]).encode("utf8"))
            elif self.path[1:] in allModsLinks:
                self._inner_func()
                if self.playerInfo["name"] == "":
                    #not connected
                    self.wfile.write(notConnectedPage().encode("utf8"))
                    return None
                if self.path[1:] in self.playerInfo["unlockedModules"]:
                    self.wfile.write(modPages[self.path[1:]].encode("utf8"))
                else:
                    #not unlocked
                    self.wfile.write(notUnlockedPage(self.playerInfo, allModsNames[allModsLinks.index(self.path[1:])]).encode("utf8"))
                    return None
            else:
                #invalid link
                self._inner_func()
                self.wfile.write(notFoundPage().encode("utf8"))
        except Exception as e:
            print("An error occured:")
            print(e)
            print("Please contact the developper with a screenshot of this message.")
        return None

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        post_data = urllib.parse.parse_qs(post_data.decode("utf-8"))

        if "post-command" not in post_data.keys():
            self._wrong_post(post_data)
        elif post_data["post-command"][0] == "connect":
            self._connect(post_data)
        elif post_data["post-command"][0] == "disconnect":
            self._disconnect(post_data)
        elif post_data["post-command"][0] == "main-page":
            self._return_to_main_page(post_data)
        else:
            self._wrong_post(post_data)

    def do_OPTIONS(self):
        print("Options")

def setModPages(playerInfo):
    print("Loading Manuals")
    global modPages
    modPages = multiprocessing.Manager().dict()
    threadList = []
    for module in allModsLinks:
        p = multiprocessing.Process(target=loadPage, args=(module, modPages, playerInfo))
        p.start()
        threadList.append(p)

    for p in threadList:
        p.join()

def run_server(player_info):
    def handler(*args, **kwargs):
        MyHttpRequestHandler(*args, player_info=player_info, **kwargs)

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        webbrowser.open(f"http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    multiprocessing.freeze_support()

    print("KTANE Expert Manuals Client")
    playerInfo = multiprocessing.Manager().dict()
    playerInfo["name"] = ""
    playerInfo["slotNumber"] = -1
    playerInfo["cdUrl"] = ""
    playerInfo["cdPort"] = ""
    playerInfo["cdName"] = ""
    playerInfo["cdPass"] = ""
    playerInfo["sdRuleSeed"] = -1
    playerInfo["sdRandomRuleSeed"] = False
    playerInfo["sdHardlockModules"] = True
    playerInfo["sdLanguage"] = "en"
    playerInfo["connected"] = False
    playerInfo["unlockedModules"] = ["TheButton", "Keypad", "Wires"]
    playerInfo["connectionResult"] = None
    playerInfo["connectionError"] = ["", ""]

    server_process = multiprocessing.Process(target=run_server, args=(playerInfo,))
    server_process.start()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()
