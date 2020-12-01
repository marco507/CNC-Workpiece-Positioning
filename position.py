import matplotlib.pyplot as plt


def import_gcode():

    # G-Code öffnen und pw in Liste - gcode schreiben.
    with open("pw.txt", "r") as file:
        gcode = []
        for i in file:
            gcode.append(i.strip())
    file.close()

    return(gcode)


def wangen_suchen(input_gcode):
    # Zeilen von Wangenkontur bis Ende (M00) aussortieren und in Liste - liste_wangen schreiben.
    liste_wangen = []
    wange = []
    start = 0

    for i in input_gcode:
        if "(WANGENKONTOUR)" in i or "(AUFG AUSSENK)" in i:
            start = 1

        if start == 1:
            wange.append(i)

        if "M00" in i:
            if len(wange) != 0:
                liste_wangen.append(wange)
            wange = []
            start = 0

    return(liste_wangen)


def wange_koordinaten_formatieren(input_wange):
    # X-Koordinaten aussortieren und als float in die Liste x_koordinaten_float schreiben
    daten_split = []
    x_koordinaten_string = []
    y_koordinaten_string = []
    x_koordinaten_temp = []
    y_koordinaten_temp = []
    x_koordinaten_float = []
    y_koordinaten_float = []

    # Liste - Koordinaten an den Leerzeilen aufteilen um die Zeilennummerierung (N***) von den Werten zu trennen.
    for i in input_wange:
        daten_split.append(i.split())

    # Die verschachtelten Listen auf die X und Y Koordinaten durchsuchen und in die jeweiligen neuen Listen schreiben.
    for i in daten_split:
        x_counter = False
        y_counter = False
        for j in i:
            if "X" in j:
                x_koordinaten_string.append(j)
                x_counter = True
            if "Y" in j:
                y_koordinaten_string.append(j)
                y_counter = True
        if x_counter and not y_counter:
            y_koordinaten_string.append("Y0")

    # Die Strings mit den X und Y Werten trennen.
    for i in x_koordinaten_string:
        x_koordinaten_temp.append(i.split("X"))
    for i in y_koordinaten_string:
        y_koordinaten_temp.append(i.split("Y"))

    # Die Listen durchsuchen und nur die Spalten mit Inhalt in die neue Liste schreiben, direkt als float.
    for i in x_koordinaten_temp:
        for j in i:
            if j != "":
                x_koordinaten_float.append(float(j))

    for i in y_koordinaten_temp:
        for j in i:
            if j != "":
                y_koordinaten_float.append(float(j))

    # Y-Koordinaten nach Platzhalter (0.0) durchsuchen und mit den vorhergehenden Werten ersetzen
    for i in range(1, len(y_koordinaten_float)):
        if y_koordinaten_float[i] == 0.0:
            y_koordinaten_float[i] = y_koordinaten_float[i-1]

    return(x_koordinaten_float, y_koordinaten_float)


def wangen_select(auswahl_wange, liste_wangen):
    # Wange auswählen
    x_koordinaten_float, y_koordinaten_float = wange_koordinaten_formatieren(
        liste_wangen[auswahl_wange])

    return(x_koordinaten_float, y_koordinaten_float)


def wangenkontur_nachzeichnen(x_koordinaten, y_koordinaten):
    # Wangenkontur fein nachberechnen
    # Die ersten 3 und letzten 2 Werte wegschneiden (Einfahrt und Ausfahrt) für Wangentreppen
    # Den ersten und letzten Wert wegschneiden (Einfahrt und Ausfahrt) für Aufgesattelte Treppen

    x_koordinaten = x_koordinaten[1:len(x_koordinaten)-1:]
    y_koordinaten = y_koordinaten[1:len(y_koordinaten)-1:]

    x_koordinaten_nachgezeichnet = []
    y_koordinaten_nachgezeichnet = []

    # Koordinaten in 1mm Schritten nachberechnen
    raster = 1

    for i in range(len(x_koordinaten)-1):
        start = x_koordinaten[i]
        steigung = (y_koordinaten[i+1] - y_koordinaten[i]) / \
            (x_koordinaten[i+1] - x_koordinaten[i])
        y_koordinaten_temp = y_koordinaten[i]

        # Absteigende Y-Koordinaten
        if(start > x_koordinaten[i+1]):
            while(start > x_koordinaten[i+1]):
                x_koordinaten_nachgezeichnet.append(start)
                y_koordinaten_nachgezeichnet.append(y_koordinaten_temp)
                y_koordinaten_temp = steigung * \
                    ((start-raster) - start) + y_koordinaten_temp
                start = start - raster

        # Aufsteigende Y-Koordinaten
        elif(start < x_koordinaten[i+1]):
            while(start < x_koordinaten[i+1]):
                x_koordinaten_nachgezeichnet.append(start)
                y_koordinaten_temp = steigung * \
                    ((start+raster) - start) + y_koordinaten_temp
                y_koordinaten_nachgezeichnet.append(y_koordinaten_temp)
                start = start + raster

    # Letzte/Erste X und Y Koordinate anhängen
    x_koordinaten_nachgezeichnet.append(x_koordinaten[-1])
    y_koordinaten_nachgezeichnet.append(y_koordinaten[-1])

    return(x_koordinaten_nachgezeichnet, y_koordinaten_nachgezeichnet)


def wangenkontur_mittelpunkt(x_koordinaten_nachgezeichnet, y_koordinaten_nachgezeichnet):
    # Mittelpunktkoordinaten berechnen
    x_koordinaten_int = []
    y_koordinaten_int = []
    x_koordinaten_mittelpunkt = []
    y_koordinaten_min_max = []
    y_koordinaten_mittelpunkt = []

    for i in x_koordinaten_nachgezeichnet:
        x_koordinaten_int.append(int(i))

    for i in y_koordinaten_nachgezeichnet:
        y_koordinaten_int.append(int(i))

    for i in range(min(x_koordinaten_int), max(x_koordinaten_int)):
        x_koordinaten_mittelpunkt.append(i)

    for i in range(min(x_koordinaten_int)+1, max(x_koordinaten_int)):
        y_koordinaten_min_max.append(
            [j for j, n in enumerate(x_koordinaten_int) if n == i])

    y_koordinaten_mittelpunkt.append(
        y_koordinaten_int[x_koordinaten_int.index(min(x_koordinaten_int))])

    for i in y_koordinaten_min_max:
        y_mittelwert = 0
        for j in i:
            y_mittelwert = y_mittelwert + y_koordinaten_int[j]
        y_mittelwert = y_mittelwert / 2
        y_koordinaten_mittelpunkt.append(y_mittelwert)

    # Mittelwertkoordinaten normalisieren
    y_koordinaten_normalisiert = []

    for i in range(len(y_koordinaten_mittelpunkt)-1):
        if y_koordinaten_mittelpunkt[i+1] > (y_koordinaten_mittelpunkt[i] * 1.1):
            y_koordinaten_mittelpunkt[i+1] = y_koordinaten_mittelpunkt[i]
        elif y_koordinaten_mittelpunkt[i+1] < (y_koordinaten_mittelpunkt[i] * 0.9):
            y_koordinaten_mittelpunkt[i+1] = y_koordinaten_mittelpunkt[i]
        y_koordinaten_normalisiert.append(y_koordinaten_mittelpunkt[i])

    y_koordinaten_normalisiert.append(y_koordinaten_mittelpunkt[-1])

    return(x_koordinaten_mittelpunkt, x_koordinaten_int, y_koordinaten_int, y_koordinaten_normalisiert, y_koordinaten_min_max)


def wangenkontur_oberkante(x_koordinaten_int, y_koordinaten_int, y_koordinaten_min_max):
    # Oberseite der Wangenkontur isolieren
    y_koordinaten_oberkante = []

    y_koordinaten_oberkante.append(
        y_koordinaten_int[x_koordinaten_int.index(min(x_koordinaten_int))])

    for i in y_koordinaten_min_max:
        maximum = 0
        for j in i:
            if y_koordinaten_int[j] > maximum:
                maximum = y_koordinaten_int[j]
        y_koordinaten_oberkante.append(maximum)

    return(y_koordinaten_oberkante)


def sauger_kontur(sauger, positionen_sauger_x, positionen_sauger_y):
    # Sauger berechnen

    # Sauger 1
    sauger_1_x = []
    sauger_1_y = []

    sauger_1_x.append(positionen_sauger_x[0] - int(sauger/2))
    sauger_1_x.append(positionen_sauger_x[0] + int(sauger/2))
    sauger_1_x.append(positionen_sauger_x[0] + int(sauger/2))
    sauger_1_x.append(positionen_sauger_x[0] - int(sauger/2))
    sauger_1_x.append(positionen_sauger_x[0] - int(sauger/2))

    sauger_1_y.append(positionen_sauger_y[0] - int(sauger/2))
    sauger_1_y.append(positionen_sauger_y[0] - int(sauger/2))
    sauger_1_y.append(positionen_sauger_y[0] + int(sauger/2))
    sauger_1_y.append(positionen_sauger_y[0] + int(sauger/2))
    sauger_1_y.append(positionen_sauger_y[0] - int(sauger/2))

    # Sauger 2
    sauger_2_x = []
    sauger_2_y = []

    sauger_2_x.append(positionen_sauger_x[1] - int(sauger/2))
    sauger_2_x.append(positionen_sauger_x[1] + int(sauger/2))
    sauger_2_x.append(positionen_sauger_x[1] + int(sauger/2))
    sauger_2_x.append(positionen_sauger_x[1] - int(sauger/2))
    sauger_2_x.append(positionen_sauger_x[1] - int(sauger/2))

    sauger_2_y.append(positionen_sauger_y[1] - int(sauger/2))
    sauger_2_y.append(positionen_sauger_y[1] - int(sauger/2))
    sauger_2_y.append(positionen_sauger_y[1] + int(sauger/2))
    sauger_2_y.append(positionen_sauger_y[1] + int(sauger/2))
    sauger_2_y.append(positionen_sauger_y[1] - int(sauger/2))

    # Sauger 3
    sauger_3_x = []
    sauger_3_y = []

    sauger_3_x.append(positionen_sauger_x[2] - int(sauger/2))
    sauger_3_x.append(positionen_sauger_x[2] + int(sauger/2))
    sauger_3_x.append(positionen_sauger_x[2] + int(sauger/2))
    sauger_3_x.append(positionen_sauger_x[2] - int(sauger/2))
    sauger_3_x.append(positionen_sauger_x[2] - int(sauger/2))

    sauger_3_y.append(positionen_sauger_y[2] - int(sauger/2))
    sauger_3_y.append(positionen_sauger_y[2] - int(sauger/2))
    sauger_3_y.append(positionen_sauger_y[2] + int(sauger/2))
    sauger_3_y.append(positionen_sauger_y[2] + int(sauger/2))
    sauger_3_y.append(positionen_sauger_y[2] - int(sauger/2))

    # Sauger 6
    sauger_6_x = []
    sauger_6_y = []

    sauger_6_x.append(positionen_sauger_x[5] - int(sauger/2))
    sauger_6_x.append(positionen_sauger_x[5] + int(sauger/2))
    sauger_6_x.append(positionen_sauger_x[5] + int(sauger/2))
    sauger_6_x.append(positionen_sauger_x[5] - int(sauger/2))
    sauger_6_x.append(positionen_sauger_x[5] - int(sauger/2))

    sauger_6_y.append(positionen_sauger_y[5] - int(sauger/2))
    sauger_6_y.append(positionen_sauger_y[5] - int(sauger/2))
    sauger_6_y.append(positionen_sauger_y[5] + int(sauger/2))
    sauger_6_y.append(positionen_sauger_y[5] + int(sauger/2))
    sauger_6_y.append(positionen_sauger_y[5] - int(sauger/2))

    # Sauger 5
    sauger_5_x = []
    sauger_5_y = []

    sauger_5_x.append(positionen_sauger_x[4] - int(sauger/2))
    sauger_5_x.append(positionen_sauger_x[4] + int(sauger/2))
    sauger_5_x.append(positionen_sauger_x[4] + int(sauger/2))
    sauger_5_x.append(positionen_sauger_x[4] - int(sauger/2))
    sauger_5_x.append(positionen_sauger_x[4] - int(sauger/2))

    sauger_5_y.append(positionen_sauger_y[4] - int(sauger/2))
    sauger_5_y.append(positionen_sauger_y[4] - int(sauger/2))
    sauger_5_y.append(positionen_sauger_y[4] + int(sauger/2))
    sauger_5_y.append(positionen_sauger_y[4] + int(sauger/2))
    sauger_5_y.append(positionen_sauger_y[4] - int(sauger/2))

    # Sauger 4
    sauger_4_x = []
    sauger_4_y = []

    sauger_4_x.append(positionen_sauger_x[3] - int(sauger/2))
    sauger_4_x.append(positionen_sauger_x[3] + int(sauger/2))
    sauger_4_x.append(positionen_sauger_x[3] + int(sauger/2))
    sauger_4_x.append(positionen_sauger_x[3] - int(sauger/2))
    sauger_4_x.append(positionen_sauger_x[3] - int(sauger/2))

    sauger_4_y.append(positionen_sauger_y[3] - int(sauger/2))
    sauger_4_y.append(positionen_sauger_y[3] - int(sauger/2))
    sauger_4_y.append(positionen_sauger_y[3] + int(sauger/2))
    sauger_4_y.append(positionen_sauger_y[3] + int(sauger/2))
    sauger_4_y.append(positionen_sauger_y[3] - int(sauger/2))

    # Sauger in Liste zusammenfassen
    x_sauger = []
    x_sauger.append(sauger_1_x)
    x_sauger.append(sauger_2_x)
    x_sauger.append(sauger_3_x)
    x_sauger.append(sauger_4_x)
    x_sauger.append(sauger_5_x)
    x_sauger.append(sauger_6_x)

    y_sauger = []
    y_sauger.append(sauger_1_y)
    y_sauger.append(sauger_2_y)
    y_sauger.append(sauger_3_y)
    y_sauger.append(sauger_4_y)
    y_sauger.append(sauger_5_y)
    y_sauger.append(sauger_6_y)

    return(x_sauger, y_sauger)


def tische_berechnen():
    # Tisch berechnen
    # Tisch Links Unten
    x_koordinaten_tisch_links_unten = []
    y_koordinaten_tisch_links_unten = []

    x_koordinaten_tisch_links_unten.append(600)
    x_koordinaten_tisch_links_unten.append(600+1650)
    x_koordinaten_tisch_links_unten.append(600+1650)
    x_koordinaten_tisch_links_unten.append(600+1650-675)
    x_koordinaten_tisch_links_unten.append(600+685)
    x_koordinaten_tisch_links_unten.append(600)
    x_koordinaten_tisch_links_unten.append(600)

    y_koordinaten_tisch_links_unten.append(0)
    y_koordinaten_tisch_links_unten.append(0)
    y_koordinaten_tisch_links_unten.append(420)
    y_koordinaten_tisch_links_unten.append(420)
    y_koordinaten_tisch_links_unten.append(560)
    y_koordinaten_tisch_links_unten.append(560)
    y_koordinaten_tisch_links_unten.append(0)

    # Tisch Links Oben
    x_koordinaten_tisch_links_oben = []
    y_koordinaten_tisch_links_oben = []

    x_koordinaten_tisch_links_oben.append(600)
    x_koordinaten_tisch_links_oben.append(600 + 675)
    x_koordinaten_tisch_links_oben.append(600 + 1650 - 685)
    x_koordinaten_tisch_links_oben.append(600 + 1650)
    x_koordinaten_tisch_links_oben.append(600 + 1650)
    x_koordinaten_tisch_links_oben.append(600)
    x_koordinaten_tisch_links_oben.append(600)

    y_koordinaten_tisch_links_oben.append(600)
    y_koordinaten_tisch_links_oben.append(600)
    y_koordinaten_tisch_links_oben.append(460)
    y_koordinaten_tisch_links_oben.append(460)
    y_koordinaten_tisch_links_oben.append(460 + 380)
    y_koordinaten_tisch_links_oben.append(600 + 240)
    y_koordinaten_tisch_links_oben.append(600)

    # Tisch Links zusammenfassen
    x_koordinaten_tisch_links = []
    x_koordinaten_tisch_links.append(x_koordinaten_tisch_links_unten)
    x_koordinaten_tisch_links.append(x_koordinaten_tisch_links_oben)

    y_koordinaten_tisch_links = []
    y_koordinaten_tisch_links.append(y_koordinaten_tisch_links_unten)
    y_koordinaten_tisch_links.append(y_koordinaten_tisch_links_oben)

    # Träger 8 - 13 (Wangen bis 1800mm maximaler Saugerabstand)
    x_start = 2400
    y_start = 0

    traegerbreite = 140
    traegerlaenge = 1320
    traegerabstand = 300

    # Träger 8 (1. Träger nach Stufentisch)
    x_koordinate_traeger_8 = []
    x_koordinate_traeger_8.append(x_start)
    x_koordinate_traeger_8.append(x_start + traegerbreite)
    x_koordinate_traeger_8.append(x_start + traegerbreite)
    x_koordinate_traeger_8.append(x_start)
    x_koordinate_traeger_8.append(x_start)

    y_koordinate_traeger_8 = []
    y_koordinate_traeger_8.append(y_start)
    y_koordinate_traeger_8.append(y_start)
    y_koordinate_traeger_8.append(traegerlaenge)
    y_koordinate_traeger_8.append(traegerlaenge)
    y_koordinate_traeger_8.append(y_start)

    # Träger 9 (1. Träger nach Stufentisch)
    x_start = x_start + traegerabstand
    x_koordinate_traeger_9 = []
    x_koordinate_traeger_9.append(x_start)
    x_koordinate_traeger_9.append(x_start + traegerbreite)
    x_koordinate_traeger_9.append(x_start + traegerbreite)
    x_koordinate_traeger_9.append(x_start)
    x_koordinate_traeger_9.append(x_start)

    y_koordinate_traeger_9 = []
    y_koordinate_traeger_9.append(y_start)
    y_koordinate_traeger_9.append(y_start)
    y_koordinate_traeger_9.append(traegerlaenge)
    y_koordinate_traeger_9.append(traegerlaenge)
    y_koordinate_traeger_9.append(y_start)

    # Träger 10 (1. Träger nach Stufentisch)
    x_start = x_start + traegerabstand
    x_koordinate_traeger_10 = []
    x_koordinate_traeger_10.append(x_start)
    x_koordinate_traeger_10.append(x_start + traegerbreite)
    x_koordinate_traeger_10.append(x_start + traegerbreite)
    x_koordinate_traeger_10.append(x_start)
    x_koordinate_traeger_10.append(x_start)

    y_koordinate_traeger_10 = []
    y_koordinate_traeger_10.append(y_start)
    y_koordinate_traeger_10.append(y_start)
    y_koordinate_traeger_10.append(traegerlaenge)
    y_koordinate_traeger_10.append(traegerlaenge)
    y_koordinate_traeger_10.append(y_start)

    # Träger 11 (1. Träger nach Stufentisch)
    x_start = x_start + traegerabstand
    x_koordinate_traeger_11 = []
    x_koordinate_traeger_11.append(x_start)
    x_koordinate_traeger_11.append(x_start + traegerbreite)
    x_koordinate_traeger_11.append(x_start + traegerbreite)
    x_koordinate_traeger_11.append(x_start)
    x_koordinate_traeger_11.append(x_start)

    y_koordinate_traeger_11 = []
    y_koordinate_traeger_11.append(y_start)
    y_koordinate_traeger_11.append(y_start)
    y_koordinate_traeger_11.append(traegerlaenge)
    y_koordinate_traeger_11.append(traegerlaenge)
    y_koordinate_traeger_11.append(y_start)

    # Träger 12 (1. Träger nach Stufentisch)
    x_start = x_start + traegerabstand
    x_koordinate_traeger_12 = []
    x_koordinate_traeger_12.append(x_start)
    x_koordinate_traeger_12.append(x_start + traegerbreite)
    x_koordinate_traeger_12.append(x_start + traegerbreite)
    x_koordinate_traeger_12.append(x_start)
    x_koordinate_traeger_12.append(x_start)

    y_koordinate_traeger_12 = []
    y_koordinate_traeger_12.append(y_start)
    y_koordinate_traeger_12.append(y_start)
    y_koordinate_traeger_12.append(traegerlaenge)
    y_koordinate_traeger_12.append(traegerlaenge)
    y_koordinate_traeger_12.append(y_start)

    # Träger 13 (1. Träger nach Stufentisch)
    x_start = x_start + traegerabstand
    x_koordinate_traeger_13 = []
    x_koordinate_traeger_13.append(x_start)
    x_koordinate_traeger_13.append(x_start + traegerbreite)
    x_koordinate_traeger_13.append(x_start + traegerbreite)
    x_koordinate_traeger_13.append(x_start)
    x_koordinate_traeger_13.append(x_start)

    y_koordinate_traeger_13 = []
    y_koordinate_traeger_13.append(y_start)
    y_koordinate_traeger_13.append(y_start)
    y_koordinate_traeger_13.append(traegerlaenge)
    y_koordinate_traeger_13.append(traegerlaenge)
    y_koordinate_traeger_13.append(y_start)

    # Träger in Liste zusammenfassen
    x_koordinaten_traeger = []
    x_koordinaten_traeger.append(x_koordinate_traeger_8)
    x_koordinaten_traeger.append(x_koordinate_traeger_9)
    x_koordinaten_traeger.append(x_koordinate_traeger_10)
    x_koordinaten_traeger.append(x_koordinate_traeger_11)
    x_koordinaten_traeger.append(x_koordinate_traeger_12)
    x_koordinaten_traeger.append(x_koordinate_traeger_13)

    y_koordinaten_traeger = []
    y_koordinaten_traeger.append(y_koordinate_traeger_8)
    y_koordinaten_traeger.append(y_koordinate_traeger_9)
    y_koordinaten_traeger.append(y_koordinate_traeger_10)
    y_koordinaten_traeger.append(y_koordinate_traeger_11)
    y_koordinaten_traeger.append(y_koordinate_traeger_12)
    y_koordinaten_traeger.append(y_koordinate_traeger_13)

    # Tisch Rechts Unten
    x_koordinaten_tisch_rechts_unten = []
    y_koordinaten_tisch_rechts_unten = []

    x_koordinaten_tisch_rechts_unten.append(4200)
    x_koordinaten_tisch_rechts_unten.append(4200+1650)
    x_koordinaten_tisch_rechts_unten.append(4200+1650)
    x_koordinaten_tisch_rechts_unten.append(4200+1650-685)
    x_koordinaten_tisch_rechts_unten.append(4200+675)
    x_koordinaten_tisch_rechts_unten.append(4200)
    x_koordinaten_tisch_rechts_unten.append(4200)

    y_koordinaten_tisch_rechts_unten.append(0)
    y_koordinaten_tisch_rechts_unten.append(0)
    y_koordinaten_tisch_rechts_unten.append(560)
    y_koordinaten_tisch_rechts_unten.append(560)
    y_koordinaten_tisch_rechts_unten.append(420)
    y_koordinaten_tisch_rechts_unten.append(420)
    y_koordinaten_tisch_rechts_unten.append(0)

    # Tisch Rechts Oben
    x_koordinaten_tisch_rechts_oben = []
    y_koordinaten_tisch_rechts_oben = []

    x_koordinaten_tisch_rechts_oben.append(4200)
    x_koordinaten_tisch_rechts_oben.append(4200 + 685)
    x_koordinaten_tisch_rechts_oben.append(4200 + 1650 - 675)
    x_koordinaten_tisch_rechts_oben.append(4200 + 1650)
    x_koordinaten_tisch_rechts_oben.append(4200 + 1650)
    x_koordinaten_tisch_rechts_oben.append(4200)
    x_koordinaten_tisch_rechts_oben.append(4200)

    y_koordinaten_tisch_rechts_oben.append(460)
    y_koordinaten_tisch_rechts_oben.append(460)
    y_koordinaten_tisch_rechts_oben.append(600)
    y_koordinaten_tisch_rechts_oben.append(600)
    y_koordinaten_tisch_rechts_oben.append(600 + 240)
    y_koordinaten_tisch_rechts_oben.append(600 + 240)
    y_koordinaten_tisch_rechts_oben.append(460)

    # Tisch Rechts zusammenfassen
    x_koordinaten_tisch_rechts = []
    x_koordinaten_tisch_rechts.append(x_koordinaten_tisch_rechts_unten)
    x_koordinaten_tisch_rechts.append(x_koordinaten_tisch_rechts_oben)

    y_koordinaten_tisch_rechts = []
    y_koordinaten_tisch_rechts.append(y_koordinaten_tisch_rechts_unten)
    y_koordinaten_tisch_rechts.append(y_koordinaten_tisch_rechts_oben)

    return(x_koordinaten_tisch_links, y_koordinaten_tisch_links, x_koordinaten_traeger, y_koordinaten_traeger, x_koordinaten_tisch_rechts, y_koordinaten_tisch_rechts)


def x_abstand_maximum(sauger, abstand, x_koordinaten_mittelpunkt, x_koordinaten_int,  y_koordinaten_normalisiert, y_koordinaten_oberkante):

    # Saugerposition (Mittelpunktkoordinate) für Sauger 1 und Sauger 6 in der Wangenkontur berechnen und den Abstand in X berechnen
    # Sauger_1 Position berechnen (Erster von Links)
    position_sauger_1 = 0  # Wert ist der Index auf der Mittelpunktlinie!
    counter = 1
    abstand_soll = 0

    try:
        while abstand_soll < (int((sauger/2)) + abstand):
            abstand_soll = y_koordinaten_oberkante[counter] - \
                y_koordinaten_normalisiert[counter]
            counter += 1

        position_sauger_1 = counter + 100

        # Sauger_6 Position berechnen (Erster von Rechts)
        position_sauger_6 = 0  # Wert ist der Index auf der Mittelpunktlinie!
        counter = len(x_koordinaten_mittelpunkt)-1
        abstand_soll = 0

        while abstand_soll < (int((sauger/2)) + abstand):
            abstand_soll = y_koordinaten_oberkante[counter] - \
                y_koordinaten_normalisiert[counter]
            counter -= 1

        position_sauger_6 = counter - 100

        x_abstand_sauger = x_koordinaten_mittelpunkt[position_sauger_6] - \
            x_koordinaten_mittelpunkt[position_sauger_1]

        # Saugerkoordinaten von Index in X Wert umrechnen
        position_sauger_1 = x_koordinaten_mittelpunkt[position_sauger_1]
        position_sauger_6 = x_koordinaten_mittelpunkt[position_sauger_6]

        zwang_auswahl = False

    except IndexError:
        # Wange ist zu klein für normale X-Abstand berechnung
        # X - Abstand normalisieren für Tisch 0
        position_sauger_1 = min(x_koordinaten_int) + int(sauger/2)
        position_sauger_6 = max(x_koordinaten_int) - int(sauger/2)

        x_abstand_sauger = max(x_koordinaten_int) - min(x_koordinaten_int)
        zwang_auswahl = True

    if x_abstand_sauger < 600:
        position_sauger_1 = min(x_koordinaten_int) + int(sauger/2)
        position_sauger_6 = max(x_koordinaten_int) - int(sauger/2)

        x_abstand_sauger = max(x_koordinaten_int) - min(x_koordinaten_int)
        zwang_auswahl = True

    return(x_abstand_sauger, position_sauger_1, position_sauger_6, zwang_auswahl)


def tisch_auswahl(x_abstand_sauger, zwang_auswahl):
    # Mit dem X Abstand der Sauger 1 und 6 den notwendigen Tisch auswählen
    # Tisch 0 - Stufentisch Links (Kleine Wangen: x_abstand_sauger <=  600mm)
    # Tisch 1 - Träger 8 - 13 (Normale Wangen: x_abstand_sauger <= 1500)
    # Tisch 2 - Stufentisch Links + Träger 8 - 13 (Große Wangen: x_abstand_sauger <= 3300)
    # Tisch 3 - Stufentisch Links + Träger 8 - 13 + Stufentisch Rechts (Sehr große Wangen <= X Hub Max)

    if x_abstand_sauger <= 600 or zwang_auswahl:
        auswahl_tisch = 0
    elif x_abstand_sauger <= 1765:
        auswahl_tisch = 1
    elif x_abstand_sauger <= 3300:
        auswahl_tisch = 2
    else:
        auswahl_tisch = 3

    return(auswahl_tisch)


def position_sauger_tisch_1(sauger, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger):

    # X Abstand auf maximalen möglichen Abstand herabsetzten
    # 3 Träger
    if x_abstand_sauger < 900:
        x_abstand_offset = x_abstand_sauger - 600
    # 4 Träger
    elif x_abstand_sauger < 1200:
        x_abstand_offset = x_abstand_sauger - 900
    # 5 Träger
    elif x_abstand_sauger < 1500:
        x_abstand_offset = x_abstand_sauger - 1200
    # 6 Träger
    else:
        x_abstand_offset = x_abstand_sauger - 1500

    # Neue Saugerpositionen in X berechnen
    position_sauger_1_offset = position_sauger_1 + int(x_abstand_offset/2)
    position_sauger_6_offset = position_sauger_6 - int(x_abstand_offset/2)

    # X Koordinaten auf der Mittelpunktachse suchen (Um Offset einrücken)
    for i in x_koordinaten_mittelpunkt:
        if i == position_sauger_1_offset:
            position_sauger_1_x = i
            position_sauger_1_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt.index(
                i)]

    for i in x_koordinaten_mittelpunkt:
        if i == position_sauger_6_offset:
            position_sauger_6_x = i
            position_sauger_6_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt.index(
                i)]

    # Position von Sauger 1 auf Träger 8 suchen
    mittelpunkt_traeger_8 = 2470

    # Offset berechnen
    x_offset = mittelpunkt_traeger_8 - position_sauger_1_x

    # Neuen Saugerpositionen berechnen (Index von x_koordinaten_mittelpunkt)
    position_sauger_1_x_offset = position_sauger_1_x + x_offset
    position_sauger_6_x_offset = position_sauger_6_x + x_offset

    # Neue Wangenkontur und Mittelpunktlinie berechnen
    x_koordinaten_offset = []
    x_koordinaten_mittelpunkt_offset = []

    for i in x_koordinaten_int:
        x_koordinaten_offset.append(i + x_offset)

    for i in x_koordinaten_mittelpunkt:
        x_koordinaten_mittelpunkt_offset.append(i + x_offset)

    # Saugerpositionsvarianten berechnen
    sauger_halb = int(sauger/2)

    if x_abstand_sauger < 900:
        # Sauger 2 und 3 berechnen (beide auf Träger 9)
        position_sauger_2_x = position_sauger_1_x_offset + 300  # Abstand der Träger
        position_sauger_3_x = position_sauger_1_x_offset + 300

        position_sauger_2_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_2_x)] + sauger_halb
        position_sauger_3_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_3_x)] - sauger_halb

        # Y Abstand von Sauger 1 und Sauger 6 zur Oberkante ermitteln
        # Abstand von Sauger 1 linke Kante Mittelpunkt zur Y Oberkante
        y_position_mittelpunkt = position_sauger_1_y - sauger_halb
        y_position_oberkante = y_koordinaten_oberkante[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_1_x_offset - sauger_halb)]

        abstand_sauger_1 = int(y_position_oberkante - y_position_mittelpunkt)

        # Abstand von Sauger 6 rechte Kante Mittelpunkt zur Y Oberkante
        y_position_mittelpunkt = position_sauger_6_y - sauger_halb
        y_position_oberkante = y_koordinaten_oberkante[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_6_x_offset + sauger_halb)]

        abstand_sauger_6 = int(y_position_oberkante - y_position_mittelpunkt)

        if abstand_sauger_1 or abstand_sauger_6 >= 140:
            # Sauger 4 zu Sauger 1 oder Sauger 6 wenn genug Platz ist (Sauger 5 über Sauger 4 legen)
            # Abstand Sauger 1 ist größer als Sauger 6
            if abstand_sauger_1 >= abstand_sauger_6:
                # Sauger 1 nach unten Rücken
                position_sauger_1_y = position_sauger_1_y - sauger_halb
                # Sauger 4 darüberr platzieren
                position_sauger_4_x = position_sauger_1_x_offset
                position_sauger_5_x = position_sauger_1_x_offset

                position_sauger_4_y = position_sauger_1_y + sauger_halb * 2
                position_sauger_5_y = position_sauger_1_y + sauger_halb * 2

            # Abstand Sauger 1 ist kleiner als Sauger 6
            elif abstand_sauger_1 < abstand_sauger_6:
                # Sauger 6 nach unten Rücken
                position_sauger_6_y = position_sauger_6_y - sauger_halb
                # Sauger 4 darüber platzieren
                position_sauger_4_x = position_sauger_6_x_offset
                position_sauger_5_x = position_sauger_6_x_offset

                position_sauger_4_y = position_sauger_6_y + sauger_halb * 2
                position_sauger_5_y = position_sauger_6_y + sauger_halb * 2

        # Beide Seiten haben keinen Platz für 2 Sauger
        else:
            # Sauger 4 und 5 über Sauger 2 und 3 legen
            position_sauger_4_x = position_sauger_1_x_offset + 300
            position_sauger_5_x = position_sauger_1_x_offset + 300

            position_sauger_4_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
                position_sauger_4_x)] + sauger_halb
            position_sauger_5_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
                position_sauger_5_x)] - sauger_halb

    elif x_abstand_sauger < 1200:
        # Sauger 2 und 3 berechnen (beide auf Träger 9)
        position_sauger_2_x = position_sauger_1_x_offset + 300  # Abstand der Träger
        position_sauger_3_x = position_sauger_1_x_offset + 300

        position_sauger_2_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_2_x)] + sauger_halb
        position_sauger_3_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_3_x)] - sauger_halb

        # Sauger 4 und 5 berechnen (beide auf Träger 10)
        position_sauger_4_x = position_sauger_1_x_offset + 600  # Abstand der Träger
        position_sauger_5_x = position_sauger_1_x_offset + 600

        position_sauger_4_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_4_x)] + sauger_halb
        position_sauger_5_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_5_x)] - sauger_halb

    elif x_abstand_sauger < 1500:
        # Sauger 2 (Träger 9)
        position_sauger_2_x = position_sauger_1_x_offset + 300  # Abstand der Träger
        position_sauger_2_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_2_x)]

        # Sauger 3 und 4 (Beide auf Träger 10)
        position_sauger_3_x = position_sauger_1_x_offset + 600
        position_sauger_4_x = position_sauger_1_x_offset + 600

        position_sauger_3_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_3_x)] + sauger_halb
        position_sauger_4_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_4_x)] - sauger_halb

        # Sauger 5 (Träger 11)
        position_sauger_5_x = position_sauger_1_x_offset + 900
        position_sauger_5_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_5_x)]

    else:
        # Sauger 2 (Träger 9)
        position_sauger_2_x = position_sauger_1_x_offset + 300  # Abstand der Träger
        position_sauger_2_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_2_x)]

        # Sauger 3 (Träger 10)
        position_sauger_3_x = position_sauger_1_x_offset + 600
        position_sauger_3_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_3_x)]

        # Sauger 4 (Träger 11)
        position_sauger_4_x = position_sauger_1_x_offset + 900
        position_sauger_4_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_4_x)]

        # Sauger 5 (Träger 12)
        position_sauger_5_x = position_sauger_1_x_offset + 1200
        position_sauger_5_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_5_x)]

    # Liste mit Saugerkoordinaten definieren und Saugermittelpunkte anhängen
    positionen_sauger_x = []
    positionen_sauger_y = []

    positionen_sauger_x.append(position_sauger_1_x_offset)
    positionen_sauger_x.append(position_sauger_2_x)
    positionen_sauger_x.append(position_sauger_3_x)
    positionen_sauger_x.append(position_sauger_4_x)
    positionen_sauger_x.append(position_sauger_5_x)
    positionen_sauger_x.append(position_sauger_6_x_offset)

    positionen_sauger_y.append(position_sauger_1_y)
    positionen_sauger_y.append(position_sauger_2_y)
    positionen_sauger_y.append(position_sauger_3_y)
    positionen_sauger_y.append(position_sauger_4_y)
    positionen_sauger_y.append(position_sauger_5_y)
    positionen_sauger_y.append(position_sauger_6_y)

    return(x_koordinaten_offset, positionen_sauger_x, positionen_sauger_y, x_offset, x_koordinaten_mittelpunkt_offset)


def sauger_positionen_berechnen(sauger, auswahl_tisch, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, y_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger):

    y_offset = 0

    if auswahl_tisch == 0:
        x_koordinaten_offset, y_koordinaten_int, positionen_sauger_x, positionen_sauger_y, x_offset, y_offset, x_koordinaten_mittelpunkt_offset = position_sauger_tisch_0(
            sauger, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, y_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger)

    elif auswahl_tisch == 1:
        x_koordinaten_offset, positionen_sauger_x, positionen_sauger_y, x_offset, x_koordinaten_mittelpunkt_offset = position_sauger_tisch_1(
            sauger, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger)

    elif auswahl_tisch == 2:
        x_koordinaten_offset, y_koordinaten_int, positionen_sauger_x, positionen_sauger_y, x_offset, y_offset, x_koordinaten_mittelpunkt_offset = position_sauger_tisch_2(
            sauger, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, y_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger)

    elif auswahl_tisch == 3:
        x_koordinaten_offset, y_koordinaten_int, positionen_sauger_x, positionen_sauger_y, x_offset, y_offset, x_koordinaten_mittelpunkt_offset = position_sauger_tisch_3(
            sauger, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, y_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger)

    return(x_koordinaten_offset, y_koordinaten_int, positionen_sauger_x, positionen_sauger_y, x_offset, y_offset, x_koordinaten_mittelpunkt_offset)


def wange_plotten(auswahl_tisch, wange, sauger, x_offset, y_offset, x_koordinaten_offset, y_koordinaten_int, x_sauger, y_sauger, x_koordinaten_tisch_links, y_koordinaten_tisch_links, x_koordinaten_traeger, y_koordinaten_traeger, x_koordinaten_tisch_rechts, y_koordinaten_tisch_rechts, platte_koordinaten):

    plt.figure(figsize=(11.69, 8.27))

    # Kleine Wangen Tisch 0
    if auswahl_tisch == 0:

        plt.subplot(2, 1, 1)
        plt.plot(x_koordinaten_tisch_links[0], y_koordinaten_tisch_links[0])
        plt.plot(x_koordinaten_tisch_links[1], y_koordinaten_tisch_links[1])

    # Normale Wangen Tisch 1
    elif auswahl_tisch == 1:

        # Träger 8 - 13
        plt.subplot(2, 1, 1)
        plt.plot(x_koordinaten_traeger[0], y_koordinaten_traeger[0])
        plt.plot(x_koordinaten_traeger[1], y_koordinaten_traeger[1])
        plt.plot(x_koordinaten_traeger[2], y_koordinaten_traeger[2])
        plt.plot(x_koordinaten_traeger[3], y_koordinaten_traeger[3])
        plt.plot(x_koordinaten_traeger[4], y_koordinaten_traeger[4])
        plt.plot(x_koordinaten_traeger[5], y_koordinaten_traeger[5])

    # Große Wangen Tisch 2
    elif auswahl_tisch == 2:

        # Stufentisch Links
        plt.subplot(2, 1, 1)
        plt.plot(x_koordinaten_tisch_links[0], y_koordinaten_tisch_links[0])
        plt.plot(x_koordinaten_tisch_links[1], y_koordinaten_tisch_links[1])

        # Träger 8 - 13
        plt.subplot(2, 1, 1)
        plt.plot(x_koordinaten_traeger[0], y_koordinaten_traeger[0])
        plt.plot(x_koordinaten_traeger[1], y_koordinaten_traeger[1])
        plt.plot(x_koordinaten_traeger[2], y_koordinaten_traeger[2])
        plt.plot(x_koordinaten_traeger[3], y_koordinaten_traeger[3])
        plt.plot(x_koordinaten_traeger[4], y_koordinaten_traeger[4])
        plt.plot(x_koordinaten_traeger[5], y_koordinaten_traeger[5])

    # Sehr große Wangen Tisch 3
    elif auswahl_tisch == 3:

        # Stufentisch Links
        plt.subplot(2, 1, 1)
        plt.plot(x_koordinaten_tisch_links[0], y_koordinaten_tisch_links[0])
        plt.plot(x_koordinaten_tisch_links[1], y_koordinaten_tisch_links[1])

        # Träger 8 - 13
        plt.subplot(2, 1, 1)
        plt.plot(x_koordinaten_traeger[0], y_koordinaten_traeger[0])
        plt.plot(x_koordinaten_traeger[1], y_koordinaten_traeger[1])
        plt.plot(x_koordinaten_traeger[2], y_koordinaten_traeger[2])
        plt.plot(x_koordinaten_traeger[3], y_koordinaten_traeger[3])
        plt.plot(x_koordinaten_traeger[4], y_koordinaten_traeger[4])
        plt.plot(x_koordinaten_traeger[5], y_koordinaten_traeger[5])

        # Stufentisch Rechts
        plt.subplot(2, 1, 1)
        plt.plot(x_koordinaten_tisch_rechts[0], y_koordinaten_tisch_rechts[0])
        plt.plot(x_koordinaten_tisch_rechts[1], y_koordinaten_tisch_rechts[1])

    # Wangenkoordinaten
    plt.subplot(2, 1, 2)
    plt.plot(x_koordinaten_offset, y_koordinaten_int)

    # Plattenkoordinaten
    plt.subplot(2, 1, 2)
    plt.plot(platte_koordinaten[0], platte_koordinaten[1])

    # Saugerkoordinaten
    plt.subplot(2, 1, 1)
    plt.plot(x_sauger[0], y_sauger[0])
    plt.plot(x_sauger[1], y_sauger[1])
    plt.plot(x_sauger[2], y_sauger[2])
    plt.plot(x_sauger[3], y_sauger[3])
    plt.plot(x_sauger[4], y_sauger[4])
    plt.plot(x_sauger[5], y_sauger[5])

    plt.subplot(2, 1, 2)
    plt.plot(x_sauger[0], y_sauger[0])
    plt.plot(x_sauger[1], y_sauger[1])
    plt.plot(x_sauger[2], y_sauger[2])
    plt.plot(x_sauger[3], y_sauger[3])
    plt.plot(x_sauger[4], y_sauger[4])
    plt.plot(x_sauger[5], y_sauger[5])

    # Bemaßung
    abstand = int(sauger/2)

    # Kleine Wangen Tisch 0
    if auswahl_tisch == 0:
        #Sauger - Tisch
        plt.subplot(2, 1, 1)
        # Sauger 1
        # Vertikal
        bemaßung = str(int(round(min(y_sauger[0])/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
            min(x_sauger[0]) + abstand, -abstand))

        # Horizontal
        bemaßung = str(int(round((min(x_sauger[0])-600)/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
            600 - abstand*1.5, min(y_sauger[0])))

        #Sauger - Wange
        plt.subplot(2, 1, 2)
        # Sauger 1
        # Vertikal
        bemaßung = str(
            int(round((min(y_sauger[0]) - min(platte_koordinaten[1]))/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
            min(x_sauger[0]), min(platte_koordinaten[1]) - abstand))

        # Horizontal
        bemaßung = str(
            int(round((min(x_sauger[0]) - min(platte_koordinaten[0]))/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
            min(platte_koordinaten[0]) - abstand, min(y_sauger[0])))

        # Nullpunktverschiebung
        plt.subplot(2, 1, 1)
        plt.text(600, 1000, 'X: ' + str(x_offset))
        plt.text(600, 900, 'Y: ' + str(y_offset))

        # Beschriftung
        if wange == 0:
            plt.text(2050, 1000, 'Wange 1')
        elif wange == 1:
            plt.text(2050, 1000, 'Wange 2')
        elif wange == 2:
            plt.text(2050, 1000, 'Wange 3')
        elif wange == 3:
            plt.text(2050, 1000, 'Wange 4')
        elif wange == 4:
            plt.text(2050, 1000, 'Wange 5')
        elif wange == 5:
            plt.text(2050, 1000, 'Wange 6')

    # Normale Wangen Tisch 1
    elif auswahl_tisch == 1:
        # 3 Träger - Sauger 1,3,6
        if x_abstand_sauger < 900:
            #Sauger - Tisch
            plt.subplot(2, 1, 1)
            # Sauger 1
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[0])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(x_sauger[0]) + abstand, -abstand))

            # Sauger 3
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[2])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[2]), min(
                y_sauger[2])), xytext=(min(x_sauger[2]), -abstand))

            # Sauger 6
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[5])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(
                y_sauger[5])), xytext=(min(x_sauger[5]), -abstand))

            #Sauger - Wange
            plt.subplot(2, 1, 2)
            # Sauger 1
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[0]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(x_sauger[0]), min(platte_koordinaten[1]) - abstand))

            # Horizontal
            bemaßung = str(
                int(round((min(x_sauger[0]) - min(platte_koordinaten[0]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(platte_koordinaten[0]) - abstand, min(y_sauger[0])))

            # Sauger 6
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[5]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(y_sauger[5])), xytext=(
                min(x_sauger[5]), min(platte_koordinaten[1])))

        # 4 Träger - Sauger 1,3,5,6
        elif x_abstand_sauger < 1200:
            #Sauger - Tisch
            plt.subplot(2, 1, 1)
            # Sauger 1
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[0])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(
                y_sauger[0])), xytext=(min(x_sauger[0]), -abstand))

            # Sauger 3
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[2])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[2]), min(
                y_sauger[2])), xytext=(min(x_sauger[2]), -abstand))

            # Sauger 5
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[4])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[4]), min(
                y_sauger[4])), xytext=(min(x_sauger[4]), -abstand))

            # Sauger 6
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[5])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(
                y_sauger[5])), xytext=(min(x_sauger[5]), -abstand))

            #Sauger - Wange
            plt.subplot(2, 1, 2)
            # Sauger 1
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[0]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(x_sauger[0]), min(platte_koordinaten[1]) - abstand))

            # Horizontal
            bemaßung = str(
                int(round((min(x_sauger[0]) - min(platte_koordinaten[0]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(platte_koordinaten[0]) - abstand, min(y_sauger[0])))

            # Sauger 6
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[5]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(y_sauger[5])), xytext=(
                min(x_sauger[5]), min(platte_koordinaten[1]) - abstand))

        # 5 Träger - Sauger 1,2,4,5,6
        elif x_abstand_sauger < 1500:
            #Sauger - Tisch
            plt.subplot(2, 1, 1)
            # Sauger 1
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[0])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(
                y_sauger[0])), xytext=(min(x_sauger[0]), -abstand))

            # Sauger 2
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[1])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[1]), min(
                y_sauger[1])), xytext=(min(x_sauger[1]), -abstand))

            # Sauger 4
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[3])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[3]), min(
                y_sauger[3])), xytext=(min(x_sauger[3]), -abstand))

            # Sauger 5
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[4])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[4]), min(
                y_sauger[4])), xytext=(min(x_sauger[4]), -abstand))

            # Sauger 6
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[5])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(
                y_sauger[5])), xytext=(min(x_sauger[5]), -abstand))

            #Sauger - Wange
            plt.subplot(2, 1, 2)
            # Sauger 1
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[0]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(x_sauger[0]), min(platte_koordinaten[1]) - abstand))

            # Horizontal
            bemaßung = str(
                int(round((min(x_sauger[0]) - min(platte_koordinaten[0]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(platte_koordinaten[0]) - abstand, min(y_sauger[0])))

            # Sauger 6
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[5]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(y_sauger[5])), xytext=(
                min(x_sauger[5]), min(platte_koordinaten[1]) - abstand))

        # 6 Träger - Sauger 1,2,3,4,5,6
        else:
            #Sauger - Tisch
            plt.subplot(2, 1, 1)
            # Sauger 1
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[0])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(
                y_sauger[0])), xytext=(min(x_sauger[0]), -abstand))

            # Sauger 2
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[1])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[1]), min(
                y_sauger[1])), xytext=(min(x_sauger[1]), -abstand))

            # Sauger 3
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[2])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[2]), min(
                y_sauger[2])), xytext=(min(x_sauger[2]), -abstand))

            # Sauger 4
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[3])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[3]), min(
                y_sauger[3])), xytext=(min(x_sauger[3]), -abstand))

            # Sauger 5
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[4])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[4]), min(
                y_sauger[4])), xytext=(min(x_sauger[4]), -abstand))

            # Sauger 6
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[5])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(
                y_sauger[5])), xytext=(min(x_sauger[5]), -abstand))

            #Sauger - Wange
            plt.subplot(2, 1, 2)
            # Sauger 1
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[0]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(x_sauger[0]), min(platte_koordinaten[1]) - abstand))

            # Horizontal
            bemaßung = str(
                int(round((min(x_sauger[0]) - min(platte_koordinaten[0]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(platte_koordinaten[0]) - abstand, min(y_sauger[0])))

            # Sauger 6
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[5]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(y_sauger[5])), xytext=(
                min(x_sauger[5]), min(platte_koordinaten[1]) - abstand))

        # Nullpunktverschiebung
        plt.subplot(2, 1, 1)
        plt.text(2400, 1700, 'X: ' + str(x_offset))
        plt.text(2400, 1600, 'Y: ' + str(y_offset))

        # Beschriftung
        if wange == 0:
            plt.text(3800, 1700, 'Wange 1')
        elif wange == 1:
            plt.text(3800, 1700, 'Wange 2')
        elif wange == 2:
            plt.text(3800, 1700, 'Wange 3')
        elif wange == 3:
            plt.text(3800, 1700, 'Wange 4')
        elif wange == 4:
            plt.text(3800, 1700, 'Wange 5')
        elif wange == 5:
            plt.text(3800, 1700, 'Wange 6')

    elif auswahl_tisch == 2:
        if x_abstand_sauger < 2100:
            #Sauger - Tisch
            plt.subplot(2, 1, 1)
            # Sauger 1
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[0])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(
                y_sauger[0])), xytext=(min(x_sauger[0]), -abstand))

            # Horizontal
            bemaßung = str(int(round((min(x_sauger[0])-600)/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                600 - abstand*1.5, min(y_sauger[0])))

            # Sauger 2
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[1])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[1]), min(
                y_sauger[1])), xytext=(min(x_sauger[1]), -abstand))

            # Sauger 3
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[2])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[2]), min(
                y_sauger[2])), xytext=(min(x_sauger[2]), -abstand))

            # Sauger 5
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[4])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[4]), min(
                y_sauger[4])), xytext=(min(x_sauger[4]), -abstand))

            # Sauger 6
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[5])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(
                y_sauger[5])), xytext=(min(x_sauger[5]), -abstand))

            #Sauger - Wange
            plt.subplot(2, 1, 2)
            # Sauger 1
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[0]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(x_sauger[0]), min(platte_koordinaten[1]) - abstand))

            # Horizontal
            bemaßung = str(
                int(round((min(x_sauger[0]) - min(platte_koordinaten[0]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(platte_koordinaten[0]) - abstand*1.5, min(y_sauger[0])))

            # Sauger 6
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[5]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(y_sauger[5])), xytext=(
                min(x_sauger[5]), min(platte_koordinaten[1]) - abstand))

        else:
            #Sauger - Tisch
            plt.subplot(2, 1, 1)
            # Sauger 1
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[0])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(
                y_sauger[0])), xytext=(min(x_sauger[0]), -abstand))

            # Horizontal
            bemaßung = str(int(round((min(x_sauger[0])-600)/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                600 - abstand*1.5, min(y_sauger[0])))

            # Sauger 2
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[1])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[1]), min(
                y_sauger[1])), xytext=(min(x_sauger[1]), -abstand))

            # Sauger 3
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[2])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[2]), min(
                y_sauger[2])), xytext=(min(x_sauger[2]), -abstand))

            # Sauger 4
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[3])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[3]), min(
                y_sauger[3])), xytext=(min(x_sauger[3]), -abstand))

            # Sauger 5
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[4])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[4]), min(
                y_sauger[4])), xytext=(min(x_sauger[4]), -abstand))

            # Sauger 6
            # Vertikal
            bemaßung = str(int(round(min(y_sauger[5])/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(
                y_sauger[5])), xytext=(min(x_sauger[5]), -abstand))

            #Sauger - Wange
            plt.subplot(2, 1, 2)
            # Sauger 1
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[0]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(x_sauger[0]), min(platte_koordinaten[1]) - abstand))

            # Horizontal
            bemaßung = str(
                int(round((min(x_sauger[0]) - min(platte_koordinaten[0]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
                min(platte_koordinaten[0]) - abstand*1.5, min(y_sauger[0])))

            # Sauger 6
            # Vertikal
            bemaßung = str(
                int(round((min(y_sauger[5]) - min(platte_koordinaten[1]))/10, 0)))
            plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(y_sauger[5])), xytext=(
                min(x_sauger[5]), min(platte_koordinaten[1]) - abstand))

        # Nullpunktverschiebung
        plt.subplot(2, 1, 1)
        plt.text(600, 1700, 'X: ' + str(x_offset))
        plt.text(600, 1600, 'Y: ' + str(y_offset))

        # Beschriftung
        if wange == 0:
            plt.text(3500, 1700, 'Wange 1')
        elif wange == 1:
            plt.text(3500, 1700, 'Wange 2')
        elif wange == 2:
            plt.text(3500, 1700, 'Wange 3')
        elif wange == 3:
            plt.text(3500, 1700, 'Wange 4')
        elif wange == 4:
            plt.text(3500, 1700, 'Wange 5')
        elif wange == 5:
            plt.text(3500, 1700, 'Wange 6')

    elif auswahl_tisch == 3:
        #Sauger - Tisch
        plt.subplot(2, 1, 1)
        # Sauger 1
        # Vertikal
        bemaßung = str(int(round(min(y_sauger[0])/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(
            y_sauger[0])), xytext=(min(x_sauger[0]), -abstand))

        # Horizontal
        bemaßung = str(int(round((min(x_sauger[0])-600)/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
            600 - abstand*1.8, min(y_sauger[0])))

        # Sauger 2
        # Vertikal
        bemaßung = str(int(round(min(y_sauger[1])/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[1]), min(
            y_sauger[1])), xytext=(min(x_sauger[1]), -abstand))

        # Sauger 3
        # Vertikal
        bemaßung = str(int(round(min(y_sauger[2])/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[2]), min(
            y_sauger[2])), xytext=(min(x_sauger[2]), -abstand))

        # Sauger 4
        # Vertikal
        bemaßung = str(int(round(min(y_sauger[3])/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[3]), min(
            y_sauger[3])), xytext=(min(x_sauger[3]), -abstand))

        # Sauger 5
        # Vertikal
        bemaßung = str(int(round(min(y_sauger[4])/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[4]), min(
            y_sauger[4])), xytext=(min(x_sauger[4]), -abstand))

        # Sauger 6
        # Vertikal
        bemaßung = str(int(round(min(y_sauger[5])/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(
            y_sauger[5])), xytext=(min(x_sauger[5]), -abstand))

        #Sauger - Wange
        plt.subplot(2, 1, 2)
        # Sauger 1
        # Vertikal
        bemaßung = str(
            int(round((min(y_sauger[0]) - min(platte_koordinaten[1]))/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
            min(x_sauger[0]), min(platte_koordinaten[1]) - abstand))

        # Horizontal
        bemaßung = str(
            int(round((min(x_sauger[0]) - min(platte_koordinaten[0]))/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[0]), min(y_sauger[0])), xytext=(
            min(platte_koordinaten[0]) - abstand*1.8, min(y_sauger[0])))

        # Sauger 6
        # Vertikal
        bemaßung = str(
            int(round((min(y_sauger[5]) - min(platte_koordinaten[1]))/10, 0)))
        plt.annotate(bemaßung, xy=(min(x_sauger[5]), min(y_sauger[5])), xytext=(
            min(x_sauger[5]), min(platte_koordinaten[1]) - abstand))

        # Nullpunktverschiebung
        plt.subplot(2, 1, 1)
        plt.text(600, 1700, 'X: ' + str(x_offset))
        plt.text(600, 1600, 'Y: ' + str(y_offset))

        # Beschriftung
        if wange == 0:
            plt.text(4800, 1700, 'Wange 1')
        elif wange == 1:
            plt.text(4800, 1700, 'Wange 2')
        elif wange == 2:
            plt.text(4800, 1700, 'Wange 3')
        elif wange == 3:
            plt.text(4800, 1700, 'Wange 4')
        elif wange == 4:
            plt.text(4800, 1700, 'Wange 5')
        elif wange == 5:
            plt.text(4800, 1700, 'Wange 6')

    # Einstellungen für Darstellung
    plt.subplot(2, 1, 1)
    plt.axis("off")   # turns off axes

    plt.subplot(2, 1, 2)
    plt.axis("off")   # turns off axes

    # PDF ausgeben
    # Beschriftung
    if wange == 0:
        plt.savefig("Wange1.pdf")
    elif wange == 1:
        plt.savefig("Wange2.pdf")
    elif wange == 2:
        plt.savefig("Wange3.pdf")
    elif wange == 3:
        plt.savefig("Wange4.pdf")
    elif wange == 4:
        plt.savefig("Wange5.pdf")
    elif wange == 5:
        plt.savefig("Wange6.pdf")


def position_sauger_tisch_2(sauger, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, y_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger):

    # Maximal möglichen Träger auswählen
    # Träger 9 - X-Abstand = 2100 - 1765
    mittelpunkt_traeger_9 = 2770
    mittelpunkt_traeger_10 = 2770 + 300
    mittelpunkt_traeger_11 = 2770 + 600
    mittelpunkt_traeger_12 = 2770 + 900
    mittelpunkt_traeger_13 = 2770 + 1200

    if x_abstand_sauger < 2100:
        x_offset = mittelpunkt_traeger_9 - position_sauger_6

    elif x_abstand_sauger < 2400:
        x_offset = mittelpunkt_traeger_10 - position_sauger_6

    elif x_abstand_sauger < 2700:
        x_offset = mittelpunkt_traeger_11 - position_sauger_6

    elif x_abstand_sauger < 3000:
        x_offset = mittelpunkt_traeger_12 - position_sauger_6

    elif x_abstand_sauger < 3300:
        x_offset = mittelpunkt_traeger_13 - position_sauger_6

    for i in x_koordinaten_mittelpunkt:
        if i == position_sauger_1:
            position_sauger_1_x = i
            position_sauger_1_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt.index(
                i)]

    for i in x_koordinaten_mittelpunkt:
        if i == position_sauger_6:
            position_sauger_6_x = i
            position_sauger_6_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt.index(
                i)]

    # Neue Wangenkoordinate berechnen
    x_koordinaten_offset = []
    x_koordinaten_mittelpunkt_offset = []

    for i in x_koordinaten_int:
        x_koordinaten_offset.append(i + x_offset)

    for i in x_koordinaten_mittelpunkt:
        x_koordinaten_mittelpunkt_offset.append(i + x_offset)

    # Neue Saugerpositionen für Sauger 6  und 1 berechnen
    position_sauger_6_x_offset = position_sauger_6_x + x_offset
    position_sauger_1_x_offset = position_sauger_1_x + x_offset

    # Restliche Saugerkoordinaten berechen
    sauger_halb = int(sauger/2)

    if x_abstand_sauger < 2100:
        # Position für Sauger 4 und 5 (Beide auf Träger 8)
        position_sauger_4_x = position_sauger_6_x_offset - 300  # Abstand der Träger
        position_sauger_5_x = position_sauger_6_x_offset - 300

        position_sauger_4_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_4_x)] + sauger_halb
        position_sauger_5_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_5_x)] - sauger_halb

    else:
        # Position für Sauger 4 und 5
        position_sauger_4_x = position_sauger_6_x_offset - 600  # Abstand der Träger
        position_sauger_5_x = position_sauger_6_x_offset - 300

        position_sauger_4_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_4_x)]
        position_sauger_5_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
            position_sauger_5_x)]

    # Position für Sauger 2 und 3
    # Sauger 2
    abstand_soll = 0
    position_sauger_1 = x_koordinaten_mittelpunkt.index(position_sauger_1_x)
    counter = position_sauger_1

    while abstand_soll < (sauger + 5):
        abstand_soll = x_koordinaten_mittelpunkt_offset[counter] - \
            x_koordinaten_mittelpunkt_offset[position_sauger_1]
        counter += 1

    position_sauger_2 = counter
    position_sauger_2_x = x_koordinaten_mittelpunkt_offset[position_sauger_2]
    position_sauger_2_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
        position_sauger_2_x)]

    # Sauger 3
    abstand_soll = 0
    counter = position_sauger_2

    while abstand_soll < (sauger + 5):
        abstand_soll = x_koordinaten_mittelpunkt[counter] - \
            x_koordinaten_mittelpunkt[position_sauger_2]
        counter += 1

    position_sauger_3 = counter
    position_sauger_3_x = x_koordinaten_mittelpunkt_offset[position_sauger_3]
    position_sauger_3_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
        position_sauger_3_x)]

    # Liste mit Saugerkoordinaten definieren und Saugermittelpunkte anhängen
    positionen_sauger_x = []
    positionen_sauger_y = []

    positionen_sauger_x.append(position_sauger_1_x_offset)
    positionen_sauger_x.append(position_sauger_2_x)
    positionen_sauger_x.append(position_sauger_3_x)
    positionen_sauger_x.append(position_sauger_4_x)
    positionen_sauger_x.append(position_sauger_5_x)
    positionen_sauger_x.append(position_sauger_6_x_offset)

    positionen_sauger_y.append(position_sauger_1_y)
    positionen_sauger_y.append(position_sauger_2_y)
    positionen_sauger_y.append(position_sauger_3_y)
    positionen_sauger_y.append(position_sauger_4_y)
    positionen_sauger_y.append(position_sauger_5_y)
    positionen_sauger_y.append(position_sauger_6_y)

    # Y-Offset berechnen wenn Sauger 1-3 über dem Spalt am Stufentisch platziert sind
    positionen_sauger_links_y = []
    positionen_sauger_links_y.append(position_sauger_1_y)
    positionen_sauger_links_y.append(position_sauger_2_y)
    positionen_sauger_links_y.append(position_sauger_3_y)

    maximale_hoehe = max(positionen_sauger_links_y) + sauger_halb
    minimale_hoehe = min(positionen_sauger_links_y) - sauger_halb

    if maximale_hoehe >= 600 and minimale_hoehe < 600:
        y_offset = 600 - minimale_hoehe
    else:
        y_offset = 0

    # Neue Y-Koordinaten für Wange berechnen

    for i in range(len(y_koordinaten_int)):
        y_koordinaten_int[i] = y_koordinaten_int[i] + y_offset

    # Neue Y-Saugerkoordinaten berechnen
    positionen_sauger_y = []
    positionen_sauger_y.append(position_sauger_1_y + y_offset)
    positionen_sauger_y.append(position_sauger_2_y + y_offset)
    positionen_sauger_y.append(position_sauger_3_y + y_offset)
    positionen_sauger_y.append(position_sauger_4_y + y_offset)
    positionen_sauger_y.append(position_sauger_5_y + y_offset)
    positionen_sauger_y.append(position_sauger_6_y + y_offset)

    return(x_koordinaten_offset, y_koordinaten_int, positionen_sauger_x, positionen_sauger_y, x_offset, y_offset, x_koordinaten_mittelpunkt_offset)


def position_sauger_tisch_3(sauger, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, y_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger):

    for i in x_koordinaten_mittelpunkt:
        if i == position_sauger_1:
            position_sauger_1_x = i
            position_sauger_1_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt.index(
                i)]

    for i in x_koordinaten_mittelpunkt:
        if i == position_sauger_6:
            position_sauger_6_x = i
            position_sauger_6_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt.index(
                i)]

    x_offset = 0

    # Neue Wangenkoordinate berechnen
    x_koordinaten_offset = []
    x_koordinaten_mittelpunkt_offset = []

    for i in x_koordinaten_int:
        x_koordinaten_offset.append(i + x_offset)

    for i in x_koordinaten_mittelpunkt:
        x_koordinaten_mittelpunkt_offset.append(i + x_offset)

    # Neue Saugerpositionen für Sauger 6  und 1 berechnen
    position_sauger_6_x_offset = position_sauger_6_x + x_offset
    position_sauger_1_x_offset = position_sauger_1_x + x_offset

    # Restliche Saugerkoordinaten berechen
    sauger_halb = int(sauger/2)

    # Position für Sauger 2 und 3
    # Sauger 2
    abstand_soll = 0
    position_sauger_1 = x_koordinaten_mittelpunkt.index(position_sauger_1_x)
    counter = position_sauger_1

    while abstand_soll < (sauger + 5):
        abstand_soll = x_koordinaten_mittelpunkt_offset[counter] - \
            x_koordinaten_mittelpunkt_offset[position_sauger_1]
        counter += 1

    position_sauger_2 = counter
    position_sauger_2_x = x_koordinaten_mittelpunkt_offset[position_sauger_2]
    position_sauger_2_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
        position_sauger_2_x)]

    # Sauger 3
    abstand_soll = 0
    counter = position_sauger_2

    while abstand_soll < (sauger + 5):
        abstand_soll = x_koordinaten_mittelpunkt[counter] - \
            x_koordinaten_mittelpunkt[position_sauger_2]
        counter += 1

    position_sauger_3 = counter
    position_sauger_3_x = x_koordinaten_mittelpunkt_offset[position_sauger_3]
    position_sauger_3_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
        position_sauger_3_x)]

    # Positionen für Sauger 4 und 5
    # Sauger 5
    abstand_soll = 0
    position_sauger_6 = x_koordinaten_mittelpunkt.index(position_sauger_6_x)
    counter = position_sauger_6

    while abstand_soll < (sauger + 5):
        abstand_soll = x_koordinaten_mittelpunkt_offset[position_sauger_6] - \
            x_koordinaten_mittelpunkt_offset[counter]
        counter -= 1

    position_sauger_5 = counter
    position_sauger_5_x = x_koordinaten_mittelpunkt_offset[position_sauger_5]
    position_sauger_5_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
        position_sauger_5_x)]

    # Sauger 4
    abstand_soll = 0
    counter = position_sauger_5

    while abstand_soll < (sauger + 5):
        abstand_soll = x_koordinaten_mittelpunkt_offset[position_sauger_5] - \
            x_koordinaten_mittelpunkt_offset[counter]
        counter -= 1

    position_sauger_4 = counter
    position_sauger_4_x = x_koordinaten_mittelpunkt_offset[position_sauger_4]
    position_sauger_4_y = y_koordinaten_normalisiert[x_koordinaten_mittelpunkt_offset.index(
        position_sauger_4_x)]

    # Liste mit Saugerkoordinaten definieren und Saugermittelpunkte anhängen
    positionen_sauger_x = []
    positionen_sauger_y = []

    positionen_sauger_x.append(position_sauger_1_x_offset)
    positionen_sauger_x.append(position_sauger_2_x)
    positionen_sauger_x.append(position_sauger_3_x)
    positionen_sauger_x.append(position_sauger_4_x)
    positionen_sauger_x.append(position_sauger_5_x)
    positionen_sauger_x.append(position_sauger_6_x_offset)

    positionen_sauger_y.append(position_sauger_1_y)
    positionen_sauger_y.append(position_sauger_2_y)
    positionen_sauger_y.append(position_sauger_3_y)
    positionen_sauger_y.append(position_sauger_4_y)
    positionen_sauger_y.append(position_sauger_5_y)
    positionen_sauger_y.append(position_sauger_6_y)

    y_offset = 0

    return(x_koordinaten_offset, y_koordinaten_int, positionen_sauger_x, positionen_sauger_y, x_offset, y_offset, x_koordinaten_mittelpunkt_offset)


def platte_zeichnen(x_koordinaten_offset, y_koordinaten_int):

    # Platte um die Wangenkontur zeichnen
    x_min = min(x_koordinaten_offset)
    x_max = max(x_koordinaten_offset)
    y_min = min(y_koordinaten_int)
    y_max = max(y_koordinaten_int)

    platte_koordinaten = []
    platte_koordinaten_x = []
    platte_koordinaten_y = []

    platte_koordinaten_x.append(x_min)
    platte_koordinaten_x.append(x_max)
    platte_koordinaten_x.append(x_max)
    platte_koordinaten_x.append(x_min)
    platte_koordinaten_x.append(x_min)

    platte_koordinaten_y.append(y_min)
    platte_koordinaten_y.append(y_min)
    platte_koordinaten_y.append(y_max)
    platte_koordinaten_y.append(y_max)
    platte_koordinaten_y.append(y_min)

    platte_koordinaten.append(platte_koordinaten_x)
    platte_koordinaten.append(platte_koordinaten_y)

    return(platte_koordinaten)


def position_sauger_tisch_0(sauger, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, y_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger):

    # Platz für 4 Sauger
    if x_abstand_sauger < sauger * 5:
        # Sauger 1
        position_sauger_1_x = position_sauger_1 + \
            ((x_abstand_sauger - sauger * 4) / 2)
        position_sauger_1_y = min(
            y_koordinaten_int) + ((max(y_koordinaten_int) - min(y_koordinaten_int)) / 2)

        # Sauger 2
        position_sauger_2_x = position_sauger_1_x + sauger
        position_sauger_2_y = position_sauger_1_y

        # Sauger 3
        position_sauger_3_x = position_sauger_2_x + sauger
        position_sauger_3_y = position_sauger_1_y

        # Sauger 4 = Sauger 3
        position_sauger_4_x = position_sauger_2_x + sauger
        position_sauger_4_y = position_sauger_1_y

        # Sauger 5 = Sauger 3
        position_sauger_5_x = position_sauger_2_x + sauger
        position_sauger_5_y = position_sauger_1_y

        # Sauger 6
        position_sauger_6_x = position_sauger_6 - \
            ((x_abstand_sauger - sauger * 4) / 2)
        position_sauger_6_y = position_sauger_1_y

    # Platz für 5 Sauger
    elif x_abstand_sauger < sauger * 6:
        # Sauger 1
        position_sauger_1_x = position_sauger_1 + \
            ((x_abstand_sauger - sauger * 5) / 2)
        position_sauger_1_y = min(
            y_koordinaten_int) + ((max(y_koordinaten_int) - min(y_koordinaten_int)) / 2)

        # Sauger 2
        position_sauger_2_x = position_sauger_1_x + sauger
        position_sauger_2_y = position_sauger_1_y

        # Sauger 3
        position_sauger_3_x = position_sauger_2_x + sauger
        position_sauger_3_y = position_sauger_1_y

        # Sauger 4
        position_sauger_4_x = position_sauger_3_x + sauger
        position_sauger_4_y = position_sauger_1_y

        # Sauger 5 = Sauger 4
        position_sauger_5_x = position_sauger_3_x + sauger
        position_sauger_5_y = position_sauger_1_y

        # Sauger 6
        position_sauger_6_x = position_sauger_6 - \
            ((x_abstand_sauger - sauger * 5) / 2)
        position_sauger_6_y = position_sauger_1_y

    # Platz für 6 Sauger
    else:
        # Sauger 1
        position_sauger_1_x = position_sauger_1 + \
            ((x_abstand_sauger - sauger * 6) / 2)
        position_sauger_1_y = min(
            y_koordinaten_int) + ((max(y_koordinaten_int) - min(y_koordinaten_int)) / 2)

        # Sauger 2
        position_sauger_2_x = position_sauger_1_x + sauger
        position_sauger_2_y = position_sauger_1_y

        # Sauger 3
        position_sauger_3_x = position_sauger_2_x + sauger
        position_sauger_3_y = position_sauger_1_y

        # Sauger 4
        position_sauger_4_x = position_sauger_3_x + sauger
        position_sauger_4_y = position_sauger_1_y

        # Sauger 5
        position_sauger_5_x = position_sauger_4_x + sauger
        position_sauger_5_y = position_sauger_1_y

        # Sauger 6
        position_sauger_6_x = position_sauger_6 - \
            ((x_abstand_sauger - sauger * 6) / 2)
        position_sauger_6_y = position_sauger_1_y

    # Liste mit Saugerkoordinaten definieren und Saugermittelpunkte anhängen
    positionen_sauger_x = []
    positionen_sauger_y = []

    positionen_sauger_x.append(position_sauger_1_x)
    positionen_sauger_x.append(position_sauger_2_x)
    positionen_sauger_x.append(position_sauger_3_x)
    positionen_sauger_x.append(position_sauger_4_x)
    positionen_sauger_x.append(position_sauger_5_x)
    positionen_sauger_x.append(position_sauger_6_x)

    positionen_sauger_y.append(position_sauger_1_y)
    positionen_sauger_y.append(position_sauger_2_y)
    positionen_sauger_y.append(position_sauger_3_y)
    positionen_sauger_y.append(position_sauger_4_y)
    positionen_sauger_y.append(position_sauger_5_y)
    positionen_sauger_y.append(position_sauger_6_y)

    # Neue Wangenkoordinate berechnen
    x_offset = 0
    y_offset = 0

    x_koordinaten_offset = []
    x_koordinaten_mittelpunkt_offset = []

    for i in x_koordinaten_int:
        x_koordinaten_offset.append(i + x_offset)

    for i in x_koordinaten_mittelpunkt:
        x_koordinaten_mittelpunkt_offset.append(i + x_offset)

    return(x_koordinaten_offset, y_koordinaten_int, positionen_sauger_x, positionen_sauger_y, x_offset, y_offset, x_koordinaten_mittelpunkt_offset)


# Treiber

# Groeße der Sauger
sauger = 120
abstand = 70

gcode = import_gcode()

# Wangen aus der G-Code Datei aussortieren und in liste_wangen schreiben
liste_wangen = wangen_suchen(gcode)

for i in range(len(liste_wangen)):
    # X und Y Koordinaten aus liste_wangen für eine einzelne ausgewählte Wange aussortieren
    x_koordinaten, y_koordinaten = wangen_select(i, liste_wangen)

    # X und Y Koordinaten mit Abstand 1mm ausfüllen und Wangenkontur nachberechnen
    x_koordinaten_nachgezeichnet, y_koordinaten_nachgezeichnet = wangenkontur_nachzeichnen(
        x_koordinaten, y_koordinaten)

    # Mittelpunktlinie der Wange ausrechnen
    x_koordinaten_mittelpunkt, x_koordinaten_int, y_koordinaten_int, y_koordinaten_normalisiert, y_koordinaten_min_max = wangenkontur_mittelpunkt(
        x_koordinaten_nachgezeichnet, y_koordinaten_nachgezeichnet)

    # Oberkante der Wangenkontur ausrechnen
    y_koordinaten_oberkante = wangenkontur_oberkante(
        x_koordinaten_int, y_koordinaten_int, y_koordinaten_min_max)

    # Maximalen Abstand in X der Sauger 1 und 6 berechnen
    x_abstand_sauger, position_sauger_1, position_sauger_6, zwang_auswahl = x_abstand_maximum(
        sauger, abstand, x_koordinaten_mittelpunkt, x_koordinaten_int, y_koordinaten_normalisiert, y_koordinaten_oberkante)

    # Tischoption anhand des X Abstands auswählen
    auswahl_tisch = tisch_auswahl(x_abstand_sauger, zwang_auswahl)

    # Saugerpositionen am Tisch berechnen und Wange nachrücken
    x_koordinaten_offset, y_koordinaten_int, positionen_sauger_x, positionen_sauger_y, x_offset, y_offset, x_koordinaten_mittelpunkt_offset = sauger_positionen_berechnen(
        sauger, auswahl_tisch, x_koordinaten_mittelpunkt, y_koordinaten_normalisiert, x_koordinaten_int, y_koordinaten_int, position_sauger_1, position_sauger_6, x_abstand_sauger)

    # Saugerkonturen berechnen
    x_sauger, y_sauger = sauger_kontur(
        sauger, positionen_sauger_x, positionen_sauger_y)

    # Tische berechnen
    x_koordinaten_tisch_links, y_koordinaten_tisch_links, x_koordinaten_traeger, y_koordinaten_traeger, x_koordinaten_tisch_rechts, y_koordinaten_tisch_rechts = tische_berechnen()

    # Platte berechnen
    platte_koordinaten = platte_zeichnen(
        x_koordinaten_offset, y_koordinaten_int)

    # Bemaßen und Wange plotten
    wange_plotten(auswahl_tisch, i, sauger,  x_offset, y_offset, x_koordinaten_offset, y_koordinaten_int, x_sauger, y_sauger, x_koordinaten_tisch_links,
                  y_koordinaten_tisch_links, x_koordinaten_traeger, y_koordinaten_traeger, x_koordinaten_tisch_rechts, y_koordinaten_tisch_rechts, platte_koordinaten)
