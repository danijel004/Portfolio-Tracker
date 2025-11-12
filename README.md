# Intro
Mein erstes Projekt "MoneyTracker" (ich weiß der Name könnte besser sein), ist aus dem Wunsch entstanden, dass ich mein
Aktienportfolio gerne mit bestimmten Benchmarks vergleichen wollte. Das liegt daran, dass diese Funktion auf vielen 
Websiten entweder hinter einer "Pay-Wall" versteckt ist oder man nicht die flexibilität hat sein Wunsch-Benchmark 
einzugeben. Zunächst hatte ich vor das Projekt in Java zu schreiben (in Uni gelernt), habe mich jedoch schlussendlich 
dagegen entschieden. Das liegt daran, dass ich in den Semesterferien zum dritten Semester mir Python selber beigebracht 
habe und keine Lust hatte nur Tutorials nachzumachen. Das Programm habe ich immer in der Main getestet (im Nachhinein 
weiß ich nicht was ich mir da gedacht habe ...).

# Funktionsweise
Alle Daten zu den Aktien stammen aus der Bibliothek "yfinance". Die Kurse sind immer die bereinigten Abschlusskurse, 
damit man einen fairen Vergleich hat. Beim Erstellen/Einfügen der Aktien muss darauf geachtet werden, dass der Ticker/
Kürzel richtig ist, da das Program die Daten nur aus der Bibliothek holen kann wenn das Kürzel stimmt 
(Name ist nur für Übersicht da). Daten können  als CSV Datei eingegeben werden oder als Objekt => 
wenn als CSV Datei wird der Verkaufspreis immer vom Programm berechnet => fairness !

# Key - Learnings
- Funktionsweise von yfinance
- Python Syntax (vorallem List Comprehension)
- wie funktioniert cagr und twr

# Was will ich in der Zukunft anderst/besser machen ?
- testen mit unittesting
- besser an SOLID/best practice Prinzipien halten
- Komplexität/Laufzeit optimieren
- nicht einfach drauf los coden, sondern Roadmap erstellen => welche Klassen/Methoden brauche ich und was machen diese
- Code auf Englisch schreiben 

# Autor
Danijel Mutic

# Schluss
Falls sie Fragen oder Verbesserungsvorschläge haben, kontaktieren sie mich gerne :))




