from Aktie import Aktie
from Portfolio import Portfolio

class Performance:
    def __init__(self,porto: Portfolio):
        self.portfolio = porto
        self.akt_twr = self.portfolio.twr_rechnen()
        self.cagr = self.portfolio.getMyCAGR()

    def twr_vergleichen(self):
        user_in = int(input("Geben sie die angegebene Nummer für ihren Benchmark ein, sie vergleichen den TWR:\nS&P 500    => 1\nMSCI World => 2\nMSCI ACWI  => 3\nNASDAQ100  => 4\nDAX        => 5\nIhre Eingabe: "))
        bench = {1:"IVV",
                 2:"URTH",
                 3:"ACWI",
                 4:"QQQ",
                 5:"EXS1.DE"}
        if user_in not in bench.keys():
            raise ValueError("Ihre Nummer steht nicht zur Auswahl")
        twr = self.getBenchTWRValue(bench.get(user_in)) # benchi
        twr_port = self.akt_twr
        diff = (twr_port*100) - (twr*100)

        if diff>0:
            return f"Ihr Portfolio hat den Benchmark um {round(diff,2)}% outperformt\nPortfolio: {round(twr_port*100,2)}%\nBenchmark: {round(twr*100,2)}%"
        else:
            return f"Ihr Portfolio hat den Benchmark um {round(abs(diff),2)}% underperformt\nPortfolio: {round(twr_port*100,2)}%\nBenchmark: {round(twr*100,2)}%"

    def getBenchTWRValue(self,ticker):
        bench = Aktie("temp",ticker)
        doku = self.portfolio.getGesamteDoku()#soll aktuell
        first_day = doku[0]["Datum"]
        kurs_start = bench.kursAnTagX(first_day)
        kurs_ende = bench.aktuellerKurs()
        return (round(kurs_ende,2)/round(kurs_start,2))-1


    def cagr_vergleichen(self):
        user_in = int(input(
            "Geben sie die angegebene Nummer für ihren Benchmark ein,sie vergleichen den CAGR:\nS&P 500    => 1\nMSCI World => 2\nMSCI ACWI  => 3\nNASDAQ100  => 4\nDAX        => 5\nIhre Eingabe: "))
        bench = {1: "IVV",
                 2: "URTH",
                 3: "ACWI",
                 4: "QQQ",
                 5: "EXS1.DE"}
        if user_in not in bench.keys():
            raise ValueError("Ihre Nummer steht nicht zur Auswahl")
        cagr_b = self.cagr_berechnen(bench.get(user_in))
        cagr_porto = self.portfolio.getMyCAGR()
        diff = (cagr_porto - cagr_b)*100
        if cagr_porto>cagr_b:
            return f"Ihr Portfolio hat den Benchmark um {round(diff, 2)}% outperformt\nPortfolio: {round(cagr_porto * 100, 2)}%\nBenchmark: {round(cagr_b * 100, 2)}%"
        else:
            return f"Ihr Portfolio hat den Benchmark um {round(abs(diff),2)}% underperformt\nPortfolio: {round(cagr_porto*100,2)}%\nBenchmark: {round(cagr_b*100,2)}%"

    def cagr_berechnen(self,ticker):
        n = self.portfolio.n_calcForCAGR()
        expo = 1/n #bis hier ok
        twr = self.getBenchTWRValue(ticker) #ab hier
        cagr = ((1+twr)**expo)-1
        return cagr

    def filter_by_performance(self):
        temp_porto = sorted(self.portfolio.getPortfolio(),key = lambda x: x.performance)
        output = "Absolute und Relative Performace der sich im Portfolio befindenden Aktien\n"
        for i in range(len(temp_porto)):
            temp = temp_porto[i]
            if temp.get_anteile()>0:
                output +=(f"Aktie: {temp.get_name()}\n"
                          f"Performance: {temp.get_Performance()}%\n"
                          f"Kursentwicklung: {temp.get_BuyIn()} -> {round(temp.aktuellerKurs(),2)}\n"
                          f"Sie haben Aktien von {temp.get_name()} im Wert von {round(temp.get_anteile() * temp.aktuellerKurs(),2)}\n"
                          f"–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––\n")
        return output
if __name__ == "__main__":
    p1 = Portfolio("erstes Portfolio")
    p1.readingCSV("/Users/dado/Documents/Selbststudium/Python lernen/MoneyTracker/test.csv")
    performi = Performance(p1)
    print(performi.twr_vergleichen())