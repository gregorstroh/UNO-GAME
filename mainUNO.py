class Karte:
    """
    Repräsentiert eine UNO-Karte mit einer Farbe und einem Wert.
    """

    def __init__(self, farbe, wert):
        """
        Initialisiert eine neue Karte.

        Parameter:
            farbe (str): Die Farbe der Karte.
            wert (str): Der Wert der Karte.
        """
        self.farbe = farbe
        self.wert = wert

    def __str__(self):
        """Gibt eine lesbare Darstellung der Karte zurück."""
        return f"{self.farbe} {self.wert}" if self.farbe else self.wert


class Spieler:
    """
    Repräsentiert einen Spieler im UNO-Spiel.
    """

    def __init__(self, name):
        """
        Initialisiert einen neuen Spieler.

        Parameter:
            name (str): Der Name des Spielers.
        """
        self.name = name
        self.hand = []

    def ziehen(self, karten_haufen, anzahl=1):
        """
        Zieht eine bestimmte Anzahl von Karten aus dem Deck.

        Parameter:
            karten_haufen (KartenHaufen): Das Deck, aus dem die Karten gezogen werden.
            anzahl (int): Die Anzahl der zu ziehenden Karten.
        """
        for _ in range(anzahl):
            karte = karten_haufen.ziehe_karte()
            if karte:
                self.hand.append(karte)

    def spiele_karte(self, karte_index):
        """
        Spielt eine Karte aus der Hand des Spielers.

        Parameter:
            karte_index (int): Der Index der zu spielenden Karte.

        Rückgabe:
            Karte: Die gespielte Karte oder None, wenn der Index ungültig ist.
        """
        if 0 <= karte_index < len(self.hand):
            return self.hand.pop(karte_index)
        return None

    def zeige_hand(self):
        """Gibt die Hand des Spielers als lesbare Strings zurück."""
        return [str(karte) for karte in self.hand]


class Bot(Spieler):
    """
    Repräsentiert einen Bot-Spieler im UNO-Spiel.
    """

    def spiele_zug(self, oberste_karte):
        """
        Führt den Zug des Bot-Spielers aus.

        Parameter:
            oberste_karte (Karte): Die oberste Karte auf dem Ablagestapel.

        Rückgabe:
            Karte: Die gespielte Karte oder None, wenn keine Karte gespielt werden kann.
        """
        spielbare_karten = [i for i, karte in enumerate(self.hand) if self.kann_spielen(karte, oberste_karte)]
        if spielbare_karten:
            for index in spielbare_karten:
                if self.hand[index].wert in ["Wild", "WildDrawFour"]:
                    # Wähle die Farbe mit den meisten Karten
                    farben_zählen = {farbe: 0 for farbe in KartenHaufen.FARBEN}
                    for karte in self.hand:
                        if karte.farbe in farben_zählen:
                            farben_zählen[karte.farbe] += 1

                    gewählte_farbe = max(farben_zählen, key=farben_zählen.get)
                    print(f"{self.name} wählt die Farbe: {gewählte_farbe} für {self.hand[index]}")
                    oberste_karte.farbe = gewählte_farbe  # Setze die Farbe der obersten Karte
                    return self.spiele_karte(index)

            # Spiele die erste spielbare Karte
            return self.spiele_karte(spielbare_karten[0])
        return None  # Keine Karte zu spielen

    def kann_spielen(self, karte, oberste_karte):
        """
        Überprüft, ob der Bot eine bestimmte Karte spielen kann.

        Parameter:
            karte (Karte): Die Karte, die gespielt werden soll.
            oberste_karte (Karte): Die oberste Karte auf dem Ablagestapel.

        Rückgabe:
            bool: True, wenn die Karte gespielt werden kann, andernfalls False.
        """
        return (karte.farbe == oberste_karte.farbe or 
                karte.wert == oberste_karte.wert or 
                karte.wert in ["Wild", "WildDrawFour"])


class KartenHaufen:
    """
    Repräsentiert das Deck von UNO-Karten.
    """

    FARBEN = ["Rot", "Blau", "Grün", "Gelb"]
    WERTE = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "Skip", "DrawTwo"]

    def __init__(self):
        """
        Initialisiert den Kartenhaufen und erstellt das Deck.
        """
        self.karten = self.erzeuge_deck()

    def erzeuge_deck(self):
        """Erstellt ein vollständiges Deck von UNO-Karten."""
        deck = [Karte(farbe, wert) for farbe in self.FARBEN for wert in self.WERTE]
        deck.extend([Karte(None, "Wild") for _ in range(4)])
        deck.extend([Karte(None, "WildDrawFour") for _ in range(4)])
        return deck

    def mischen(self):
        """Mischt die Karten im Deck."""
        import random
        random.shuffle(self.karten)

    def ziehe_karte(self):
        """
        Zieht die oberste Karte vom Deck.

        Rückgabe:
            Karte: Die gezogene Karte oder None, wenn das Deck leer ist.
        """
        return self.karten.pop() if self.karten else None


class HauptSpiel:
    """
    Repräsentiert das Hauptspiel und steuert den Spielablauf.
    """

    def __init__(self):
        """
        Initialisiert das Hauptspiel und die Spielparameter.
        """
        self.karten_haufen = KartenHaufen()
        self.spieler = []
        self.oberste_karte = None
        self.aktueller_spieler = 0
        self.spiel_laeuft = True

    def spiel_starten(self):
        """Startet das Spiel und initialisiert die Spieler."""
        self.karten_haufen.mischen()
        spieler_typ = input("Möchtest du gegen einen (1) Spieler oder (2) Bot spielen? ")
        spieler_name = input("Gib deinen Namen ein: ")
        self.spieler.append(Spieler(spieler_name))

        if spieler_typ == "1":
            self.spieler.append(Spieler("Spieler 2"))
        elif spieler_typ == "2":
            self.spieler.append(Bot("Bot"))

        for spieler in self.spieler:
            spieler.ziehen(self.karten_haufen, 7)

        # Stelle sicher, dass die oberste Karte eine normale Farbkarte ist
        while True:
            self.oberste_karte = self.karten_haufen.ziehe_karte()
            if self.oberste_karte and self.oberste_karte.wert in KartenHaufen.WERTE[:-4]:  # Alle Werte außer Wild und WildDrawFour
                break

    def zeige_spielstand(self):
        """Gibt den aktuellen Spielstand aus."""
        aktueller_spieler = self.spieler[self.aktueller_spieler]
        print(f"Oberste Karte: {self.oberste_karte}")
        print(f"{aktueller_spieler.name}, deine Karten sind:")
        for index, karte in enumerate(aktueller_spieler.hand):
            print(f"{index + 1}: {karte}")  # +1 für benutzerfreundliche Anzeige

    def karte_spielen(self):
        """
        Führt den Spielzug des aktuellen Spielers aus, einschließlich Spiel- und Ziehlogik.
        """
        aktueller_spieler = self.spieler[self.aktueller_spieler]
        print("************************************************************")
        print(f"{aktueller_spieler.name} ist dran.")
        self.zeige_spielstand()

        ueberspringen_nächster_spieler = False

        if isinstance(aktueller_spieler, Bot):
            gespielte_karte = aktueller_spieler.spiele_zug(self.oberste_karte)
            if gespielte_karte:
                print(f"{aktueller_spieler.name} hat {gespielte_karte} gespielt.")
                self.oberste_karte = gespielte_karte
                ueberspringen_nächster_spieler = self.behandle_spezielle_kartenaktionen(gespielte_karte, aktueller_spieler)
            else:
                self.behandle_ziehen(aktueller_spieler)
        else:
            spielbare_karten = [i for i, karte in enumerate(aktueller_spieler.hand) if self.kann_spielen(karte)]

            if spielbare_karten:
                gewählte_karte_index = self.get_valid_card_index(aktueller_spieler, spielbare_karten)
                gespielte_karte = aktueller_spieler.spiele_karte(gewählte_karte_index)
                print(f"{aktueller_spieler.name} hat {gespielte_karte} gespielt.")
                self.oberste_karte = gespielte_karte
                ueberspringen_nächster_spieler = self.behandle_spezielle_kartenaktionen(gespielte_karte, aktueller_spieler)
            else:
                self.behandle_ziehen(aktueller_spieler)

        if not ueberspringen_nächster_spieler:
            self.aktueller_spieler = 1 - self.aktueller_spieler

    def get_valid_card_index(self, aktueller_spieler, spielbare_karten):
        """
        Fragt den Benutzer nach dem Index der Karte, die er spielen möchte.

        Parameter:
            aktueller_spieler (Spieler): Der aktuelle Spieler.
            spielbare_karten (list): Liste der spielbaren Kartenindizes.

        Rückgabe:
            int: Der Index der gewählten Karte.
        """
        while True:
            try:
                gewählte_karte_index = int(input("Gib die Nummer der Karte ein, die du spielen möchtest (1 für die erste Karte): ")) - 1
                if gewählte_karte_index in spielbare_karten:
                    return gewählte_karte_index
                else:
                    print("Diese Karte kann nicht gespielt werden, versuche es erneut.")
            except ValueError:
                print("Bitte gib eine gültige Zahl ein.")

    def behandle_spezielle_kartenaktionen(self, gespielte_karte, aktueller_spieler):
        """
        Behandelt spezielle Kartenaktionen wie 'Skip', 'Reverse', 'Wild', 'WildDrawFour' und 'DrawTwo'.

        Parameter:
            gespielte_karte (Karte): Die Karte, die gespielt wurde.
            aktueller_spieler (Spieler): Der Spieler, der die Karte gespielt hat.

        Rückgabe:
            bool: Gibt zurück, ob der nächste Spieler übersprungen werden soll.
        """
        ueberspringen_nächster_spieler = False
        if gespielte_karte.wert == "Skip":
            print(f"{self.spieler[1 - self.aktueller_spieler].name} wird übersprungen!")
            ueberspringen_nächster_spieler = True
        elif gespielte_karte.wert == "Reverse":
            print("Richtung umkehren!")
            # Hier könnte die Umkehrlogik implementiert werden
        elif gespielte_karte.wert in ["Wild", "WildDrawFour"]:
            if gespielte_karte.wert == "Wild":
                print(f"{aktueller_spieler.name} hat eine Wild-Karte gespielt.")
            elif gespielte_karte.wert == "WildDrawFour":
                print(f"{aktueller_spieler.name} hat eine WildDrawFour-Karte gespielt.")
                if isinstance(aktueller_spieler, Bot):
                    # Wähle die Farbe mit den meisten Karten
                    farben_zählen = {farbe: 0 for farbe in KartenHaufen.FARBEN}
                    for karte in aktueller_spieler.hand:
                        if karte.farbe in farben_zählen:
                            farben_zählen[karte.farbe] += 1

                    gewählte_farbe = max(farben_zählen, key=farben_zählen.get)
                    print(f"{aktueller_spieler.name} wählt die Farbe: {gewählte_farbe}")
                    self.oberste_karte.farbe = gewählte_farbe  # Setze die Farbe der obersten Karte

            neue_farbe = input("Wähle eine neue Farbe (Rot, Blau, Grün, Gelb): ")
            self.oberste_karte.farbe = neue_farbe
            print(f"Neue Farbe ist: {neue_farbe}")

            if gespielte_karte.wert == "WildDrawFour":
                self.ziehe_karten(4, "WildDrawFour")
        elif gespielte_karte.wert == "DrawTwo":
            self.ziehe_karten(2, "DrawTwo")

        return ueberspringen_nächster_spieler

    def behandle_ziehen(self, aktueller_spieler):
        """
        Behandelt das Ziehen einer Karte durch den aktuellen Spieler.

        Parameter:
            aktueller_spieler (Spieler): Der Spieler, der eine Karte zieht.
        """
        print(f"{aktueller_spieler.name} zieht eine Karte.")
        neue_karte = self.karten_haufen.ziehe_karte()
        if neue_karte:
            aktueller_spieler.hand.append(neue_karte)
            print(f"{aktueller_spieler.name} hat eine Karte gezogen: {neue_karte}")
            if self.kann_spielen(neue_karte):
                print(f"{aktueller_spieler.name} kann die gezogene Karte spielen.")
            else:
                print(f"{aktueller_spieler.name} kann die gezogene Karte nicht spielen.")

    def kann_spielen(self, karte):
        """
        Überprüft, ob eine Karte gespielt werden kann.

        Parameter:
            karte (Karte): Die Karte, die gespielt werden soll.

        Rückgabe:
            bool: True, wenn die Karte gespielt werden kann, andernfalls False.
        """
        return (karte.farbe == self.oberste_karte.farbe or 
                karte.wert == self.oberste_karte.wert or 
                karte.wert in ["Wild", "WildDrawFour"])

    def gewinner_ueberpruefen(self):
        """
        Überprüft, ob ein Spieler gewonnen hat und beendet das Spiel, wenn dies der Fall ist.
        """
        for spieler in self.spieler:
            if not spieler.hand:
                print(f"{spieler.name} hat das Spiel gewonnen!")
                self.spiel_laeuft = False


"Ausführen des Spiels"
uno_spiel = HauptSpiel()
uno_spiel.spiel_starten()

while uno_spiel.spiel_laeuft:
    uno_spiel.karte_spielen()
    uno_spiel.gewinner_ueberpruefen()