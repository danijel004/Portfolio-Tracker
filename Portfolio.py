import csv
from operator import truediv

import yfinance as yf
from matplotlib import pyplot as plt
from datetime import timedelta,date
from Aktie import Aktie
from math import prod


class Portfolio:
    def __init__(self,name,beschreibung = ""):
        self.name = name
        self.beschreibung = beschreibung
        self.portfolio = []
        self.gesamteDoku = []

    def kauf(self,name,kürzel,anteile,datum,preis = None): #funktioniert komplett
        while yf.Ticker(kürzel).history().empty:
            kürzel = input("Geben sie den richigen Kürzel ein")
        for i in range(len(self.portfolio)):
            current = self.portfolio[i]
            if current.kürzel == kürzel:
                current.kaufen(anteile,datum,preis)
                return

        temp = Aktie(name, kürzel)
        temp.kaufen(anteile,datum,preis)
        self.portfolio.append(temp)
        return

    def verkauf(self,nam,ante,datum):
        for i in range(len(self.portfolio)):
            current = self.portfolio[i]
            if current.name == nam:
                if  current.getAnteile() < ante:
                    raise ValueError("Es sollen Mehr Anteile verkauft werden als zur Verfügung stehen")
                else:
                    current.verkaufen(ante,datum) #hier wird der fehler der eigentlich geworfen werden sollte nicht geworfen
        return "Kein Eintrag zu Aktie gefunden"

    def getPortfolioWert(self):
        wert = sum([x.get_wert() for x in self.portfolio if x.get_anteile()>0])
        return wert
    def portf_ansicht(self):
        signs = []
        weights = []
        for i in range(len(self.portfolio)):
            current = self.portfolio[i]
            if current.anteile > 0:
                current_wert = float(current.anteile*current.aktuellerKurs())
                temp = (current.name,round(current_wert,2))
                signs.append(temp[0])
                weights.append(float(round(temp[1],2)))
        plt.pie(weights, labels = signs,autopct="%2.2f%%")
        plt.show()
        return signs,weights

    def portfo_infos(self):
        out = ""
        for i in range(len(self.portfolio)):
            current = self.portfolio[i]
            if current.anteile>0:
                out+= current.get_info()+"\n"
        return out

    def getGesamteDoku(self):
        old = list()
        ergebnis = list()
        for i in range(len(self.portfolio)):
            current = self.portfolio[i].dokumentation
            ergebnis = current + old
            old = ergebnis
        sorted_e = sorted(ergebnis, key=lambda item:item["Datum"])
        self.gesamteDoku = sorted_e
        return sorted_e

    def twr_rechnen(self):
        renditen = []
        port_zu_zeit_x = []
        self.getGesamteDoku()
        startwert = 0

        for i, current in enumerate(self.gesamteDoku):
            datum = current["Datum"]

            if i == 0:

                Portfolio.twr_helper(port_zu_zeit_x, current["Ticker"], current["Anteile"])
                startwert += (float(Portfolio.helperKursAnX(current["Ticker"], current["Datum"])) * current["Anteile"])
            else:


                akt_wert = sum(
                    x["Anteile"] * Portfolio.helperKursAnX(x["Ticker"], datum - timedelta(days=0))
                    for x in port_zu_zeit_x
                )

                rendi = akt_wert / startwert - 1
                renditen.append(float(rendi))


                if current["Typ"] == "Kauf":
                    Portfolio.twr_helper(port_zu_zeit_x, current["Ticker"], current["Anteile"])
                    startwert = akt_wert + (float(Portfolio.helperKursAnX(current["Ticker"], current["Datum"])) * current[
                        "Anteile"])
                else:
                    Portfolio.twr_helper(port_zu_zeit_x, current["Ticker"], current["Anteile"], True)
                    startwert = akt_wert - (float(Portfolio.helperKursAnX(current["Ticker"], current["Datum"])) * current[
                        "Anteile"])

        if port_zu_zeit_x:
            akt_wert = sum(
                x["Anteile"] * Portfolio.helperKursAnX(x["Ticker"], date.today())
                for x in port_zu_zeit_x
            )
            startwert_letzte = sum(
                x["Anteile"] * Portfolio.helperKursAnX(x["Ticker"], self.gesamteDoku[-1]["Datum"])
                for x in port_zu_zeit_x
            )
            rendi = akt_wert / startwert_letzte - 1
            renditen.append(float(rendi))
        twr = Portfolio.twrGeometrVerknüpfung(renditen)

        return twr
    def get_twr(self):
        twr = self.twr_rechnen()
        print(f"Der aktuelle TWR Wert ihres Depots ist {twr * 100:.2f}%")

    def getMyCAGR(self):
        # (1+TWR)1/n-1
        twr = self.twr_rechnen()
        n = self.n_calcForCAGR()
        expo = 1/n
        cagr= ((1+twr)**expo) -1
        return cagr

    def getCAGRText(self):
        cagr = self.getMyCAGR()
        return f"Der CAGR ihres Portfolio beträgt: {cagr}%\nDas sind somit {round(cagr * 100, 2)}% pro Jahr"
    def n_calcForCAGR(self):
        temp = self.getGesamteDoku()
        first_day = temp[0]["Datum"]
        diff = (date.today() - first_day).days
        return diff/365 #type float in Jahren

    @staticmethod
    def twrGeometrVerknüpfung(renditen):
        temp = prod([r + 1 for r in renditen])

        return temp -1

    @staticmethod
    def helperKursAnX(ticker, datum):
        df = yf.Ticker(ticker).history(
            start=datum - timedelta(days=5),
            end=datum + timedelta(days=1),
            auto_adjust=True
        )
        if df.empty:
            df_all = yf.Ticker(ticker).history(period="max", auto_adjust=True)
            return df_all["Close"].iloc[-1]
        return df["Close"].iloc[-1]

    def get_subperioden_startwert(self, portfolio, current):
        startwert = 0
        for x in portfolio:
            kurs = Portfolio.helperKursAnX(x["Ticker"], current["Datum"] - timedelta(days=1))
            startwert += x["Anteile"] * kurs
        return startwert

    @staticmethod
    def twr_helper(porto, kürzel, anteile, isVerkauf=False):
        eintrag = next((item for item in porto if item["Ticker"] == kürzel), None)
        if eintrag:
            if isVerkauf:
                eintrag["Anteile"] -= anteile
            else:
                eintrag["Anteile"] += anteile
        else:
            porto.append({"Ticker": kürzel, "Anteile": anteile})
    def getPortfolioTicker(self):
        names = [aktie.kürzel for aktie in self.portfolio if aktie.anteile] #selbst wenn 0 geht nur addieren
        return names

    @staticmethod
    def isKauf(typ):
        if typ == "Kauf":
            return True
        else:
            return False


    def readingCSV(self,path):
        with open(path) as f:
            csv_reader = csv.reader(f,delimiter=";")
            line_count = 0
            for row in csv_reader:

                if(line_count == 0):
                    line_count +=1#festes System
                    continue
                if row[1] in self.getPortfolioTicker() : #existiert

                    self.csvTransaktionHelper(row,line_count)
                    """if row[2] == "Kauf":
                        if len(row) > 5:
                            self.kauf(row[0],row[1],row[3],row[4],row[5])
                        else:
                            self.kauf(row[0], row[1], row[3], row[4])
                    if row[2] == "Verkauf":
                        self.verkauf(row[0],row[3],row[4])"""

                else:
                    if row[2] != "Kauf":
                        print(f"Zeile {line_count} wurde wegen fehlerhafter eingabe nciht berücksichtigt")
                        continue
                    else:
                        self.csvTransaktionHelper(row,line_count)
                line_count+=1


    def csvTransaktionHelper(self,row,zeile):
        if row[2] == "Kauf":
            if yf.Ticker(row[1]).history().empty:
                print(f"Die Transaktion in Zeile {zeile} ist fehlerhaft und wurde ausgelassen ")
            else:
                if len(row) > 5:
                    self.kauf(row[0], row[1], float(row[3]), row[4], float(row[5]))
                else:
                    self.kauf(row[0], row[1], float(row[3]), row[4])
        if row[2] == "Verkauf":
            self.verkauf(row[0], float(row[3]),row[4])

    def getPortfolio(self):
        return self.portfolio

if __name__ == "__main__":
    p1 = Portfolio("erstes Portfolio")
    p1.readingCSV("/Users/dado/Documents/Selbststudium/Python lernen/MoneyTracker/examplePortfolio.csv")
    print(p1.portfo_infos())

