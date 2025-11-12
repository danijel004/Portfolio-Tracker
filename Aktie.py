import datetime
from datetime import timedelta,date
from datetime import datetime
from yfinance.exceptions import YFPricesMissingError
import yfinance as yf
import datetime as dt
#acb = average cost basis
class Aktie:
    def __init__(self,name,kürzel):
        self.name = name
        self.kürzel = kürzel
        self.anteile = 0
        self.bestand = [] #veraltet wird nur bei lifo benutzt
        self.buyIn = 0
        self.rendite = 0
        self.performance =""
        self.dokumentation = list() #ggf Klasse Dokumente und dann das als dict und einmal Käufe und einmal Verkäufe


    def kaufen(self,anteile,datum,preis = None):
        if preis is None:
            preis = self.kursAnTagX(self.date_conver(datum))
        else:
            eurousd = yf.Ticker("EURUSD=X")
            dat_con = self.date_conver(datum)
            kurs = eurousd.history(start=dat_con, end= dat_con + timedelta(days = 1))["Close"].iloc[0]
            preis*=kurs
        self.addKauf_zu_Dokumentation(round(preis,2),anteile,datum)
        self.refreshBuyIn_Menge() #buyIN und anteile sind fresh
        self.datenAktualiseren() # werden rendite etc aktuell gehalten
    def get_anteile(self):
        return self.anteile
    def get_wert(self):
        return round(self.anteile * self.aktuellerKurs(),2)


    def aktuellerKurs(self):
        """today = dt.date.today()
        value = yf.download(self.kürzel, today, today + timedelta(days=1),auto_adjust=True)
        return round(value["Close"].iloc[0][self.kürzel],2)"""
        try:
            # Hauptmethode
            kurs = yf.Ticker(self.kürzel).history(period="1d")["Close"].iloc[-1]
        except (YFPricesMissingError, IndexError, KeyError, Exception) as e:
            print(f"Fehler beim Abrufen von history(): {e}")
            try:
                # Fallback: fast_info
                kurs = yf.Ticker(self.kürzel).fast_info.last_price
            except Exception as e2:
                print(f"Auch fast_info fehlgeschlagen: {e2}")
                kurs = None
        return kurs

    def kursAnTagX(self,x):
        value = yf.download(self.kürzel, x, x + timedelta(days=1), auto_adjust=True)
        return round(value["Close"].iloc[0][self.kürzel], 2) #liefert preis
        round(yf.download(self.kürzel, x, x + timedelta(days=1), auto_adjust=True)["Close"].iloc[0][self.kürzel], 2)

    def datenAktualiseren(self):
        try:
            aktuellerKurs = self.aktuellerKurs()
        except YFPricesMissingError as y:
            tck = yf.Ticker(self.kürzel)
            aktuellerKurs = tck.fast_info.last_price

        differenz = aktuellerKurs - self.buyIn
        self.rendite = round(differenz * self.anteile,2)
        self.performance = round(((aktuellerKurs/self.buyIn) -1)*100,2)
    def get_info(self):
        return f"Name: {self.name}\n Anteile: {self.anteile}\n Aktueller Kurs: {self.aktuellerKurs()}\n BuyIn: {self.buyIn}\n Rendite:{self.rendite}\n Performance: {self.performance}%"

    def verkaufen(self,am,dat,isACB = True):
        if am <= 0:
            raise ValueError("Verkaufte Anteile müssen größer 0 sein")

        if isACB:
            self.__verkauf_acb(am, dat)
        else:
            self.__verkauf_Lifo(am, dat)


    def __verkauf_Lifo(self,amount,datum):
        datum_con = self.date_conver(datum)
        if not self.isBörse_aktiv(datum_con):
            return "Börse geschlossen, prüfen sie das Datum erneut"

        if amount > sum([c["Anteile"] for c in self.bestand if datetime.strptime(c["Datum"],"%d-%m-%Y")<=datetime.strptime(datum,"%d-%m-%Y")]): #bricht
            raise ValueError("Du kannst nicht mehr verkaufen als du hast") #funktioniert
        anschaffungs_kosten = 0
        fin_amount = amount
        self.anteile -= fin_amount
        self.bestand = [x for x in self.dokumentation if x["Typ"] == "Kauf"]
        for i in range(len(self.bestand)): #funktioniert => immer nur betrachtet welche man zu Zeitpunkt x hat

            if amount > self.bestand[i]["Anteile"]:
                anschaffungs_kosten += (self.bestand[i]["Anteile"] * self.bestand[i]["Kurs"])
                amount -=self.bestand[i]["Anteile"]
                self.bestand[i]["Anteile"] = 0

            else:
                self.bestand[i]["Anteile"] -= amount
                self.bestand[i]["Anteile"] = round(self.bestand[i]["Anteile"],6)
                anschaffungs_kosten += (amount * self.bestand[i]["Kurs"])
                break
        dokument ={
            "Typ" : "Verkauf",
            "Datum":datum,
            "Anteile":fin_amount,
            "Rendite": round(float(self.kursAnTagX(datum_con))*fin_amount - anschaffungs_kosten,2),
            "Performance": round(((float(self.kursAnTagX(datum_con))*fin_amount - anschaffungs_kosten)/anschaffungs_kosten)*100,2)
        }
        self.dokumentation.append(dokument)
        transaktionen = sorted(self.dokumentation, key=lambda x: x["Datum"])
        self.dokumentation = transaktionen
        updated = [daten for daten in self.bestand if daten["Anteile"] > 0] #funktioniert
        self.bestand = updated
        self.refreshBuyIn_Menge()
        return dokument

    def getAnteile(self):
        return self.anteile


    def __verkauf_acb(self,amount,datum):
        fixed = self.date_conver(datum)
        if not self.isBörse_aktiv(fixed): #teste ob börse zu war
            return "Börse geschlossen, prüfen sie das Datum erneut"

        i = 0
        buyIn_bis_X = 0
        alt_gbw = 0
        anteile_zu_Zeit_X = 0
        while i < len(self.dokumentation) and self.dokumentation[i]["Datum"] <= fixed:
            if self.dokumentation[i]["Typ"] == "Kauf":
                neu_gbw = float(self.dokumentation[i]["Kurs"]) * float(self.dokumentation[i]["Anteile"]) + alt_gbw # neuer gbw
                anteile_zu_Zeit_X += self.dokumentation[i]["Anteile"]
                buyIn_bis_X = neu_gbw / anteile_zu_Zeit_X
                alt_gbw = neu_gbw

            else:
                alt_gbw -= (self.dokumentation[i]["Anteile"] * buyIn_bis_X)
                anteile_zu_Zeit_X -= self.dokumentation[i]["Anteile"]
            i +=1

        if anteile_zu_Zeit_X < amount:
            raise ValueError("Sie wollen mehr verkaufen, als sie zu dem eingegebenen Zeitpunkt besitzen")
        temp = {
            "Ticker": self.kürzel,
            "Typ": "Verkauf",
            "Anteile": amount,
            "Kurs": round(float(self.kursAnTagX(fixed)),2),
            "Datum": fixed,
            "Rendite": round(float((amount*self.kursAnTagX(fixed)) - (amount*buyIn_bis_X)),2),
            "Performance": float((((amount*self.kursAnTagX(fixed)) - (amount*buyIn_bis_X))/(amount*buyIn_bis_X)) *100)
        } #verkauf wurde richtig dokumentiert  ===>
        self.dokumentation.append(temp)
        transaktionen = sorted(self.dokumentation, key=lambda x: x["Datum"])
        self.dokumentation = transaktionen
        self.refreshBuyIn_Menge()

    def refreshBuyIn_Menge(self):
        i = 0
        buyIn_fresh = 0
        alt_gbw = 0
        akt_anteile = 0

        while i < len(self.dokumentation):
            eintrag = self.dokumentation[i]
            if eintrag["Typ"] == "Kauf":
                alt_gbw += float(eintrag["Kurs"]) * float(eintrag["Anteile"])
                akt_anteile += eintrag["Anteile"]
                buyIn_fresh = alt_gbw / akt_anteile
            else:
                alt_gbw -= eintrag["Anteile"] * buyIn_fresh
                akt_anteile -= eintrag["Anteile"]
            i += 1
        self.buyIn = round(buyIn_fresh,2)
        self.anteile = akt_anteile
    def addKauf_zu_Dokumentation(self,preis,anteile,datum):
        fixed = self.date_conver(datum)
        self.dokumentation.append({
            "Ticker": self.kürzel,
            "Typ": "Kauf",
            "Anteile": float(anteile),
            "Kurs": float(preis),
            "Datum": fixed})
        transaktionen = sorted(self.dokumentation, key=lambda x: x["Datum"])
        self.dokumentation = transaktionen

        return "Den Beleg finden sie in der Dokumentation"

    def date_conver(self,datum):
        splitted = datum.split("-")
        as_date = date(int(splitted[-1]),int(splitted[1]),int(splitted[0]))
        return as_date

    def isBörse_aktiv(self,datum):
        value = yf.download(self.kürzel, datum, datum + timedelta(days=1), auto_adjust=True)
        if value.empty :
            return False
        else:
            return True

    def investiert_vs_aktuell(self):
        investiert = 0
        aktuell = self.anteile * self.aktuellerKurs()
        for i in range(len(self.dokumentation)):
            current = self.dokumentation[i]
            if current["Typ"] == "Kauf":
                investiert += current["Anteile"]* current["Kurs"]
            else:
                investiert -= current["Anteile"] * current["Kurs"]
        return investiert,aktuell
    def __eq__(self,other):
        if not isinstance(other,Aktie):
            return NotImplemented
        return self.name == other.name and self.kürzel == other.kürzel

    def get_Performance(self):
        return round(((self.aktuellerKurs() / float(self.buyIn)) - 1) * 100, 2)
    def get_name(self):
        return self.name
    def get_BuyIn(self):
        return self.buyIn
    def get_anteile(self):
        return self.anteile

if __name__ == "__main__":
    aktie1 = Aktie("Microsoft","MSFT")
    print("Kurs vom 23-10-2024")
    aktie1.kaufen(2,"21-10-2024")
    print(aktie1.kursAnTagX(aktie1.date_conver("23-10-2024")))
    aktie1.kaufen(3,"06-03-2025",435)
    print(aktie1.dokumentation)
    print(aktie1.anteile)
    aktie2 = Aktie("Tesla","TSLA")
