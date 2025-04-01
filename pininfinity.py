import decimal
import time
import threading
import sys
import os
from datetime import datetime

# Dezimalpräzision für Start (wird kontinuierlich erhöht)
BASE_PRECISION = 1000

def chudnovsky_algorithm(precision, update_callback, stop_event):
    """
    Berechnet Pi mit der Chudnovsky-Methode.
    Diese Methode konvergiert sehr schnell und ist für hohe Genauigkeiten gut geeignet.
    Berechnet kontinuierlich, bis sie durch das stop_event unterbrochen wird.
    """
    # Initialisierung der Variablen für den Chudnovsky-Algorithmus
    decimal.getcontext().prec = precision
    C = 426880 * decimal.Decimal(10005).sqrt()
    M = decimal.Decimal(1)
    L = decimal.Decimal(13591409)
    X = decimal.Decimal(1)
    K = decimal.Decimal(6)
    S = L
    
    pi = C / S  # Erste grobe Annäherung
    current_iteration = 0
    
    # Kontinuierliche Berechnung, bis das Stoppsignal gegeben wird
    while not stop_event.is_set():
        current_iteration += 1
        
        # Algorithmusschritte
        M = M * (K**3 - 16 * K) // (current_iteration**3)
        L = L + 545140134
        X = X * -262537412640768000
        S = S + (M * L) / X
        K = K + 12
        
        # Pi berechnen
        pi = C / S
        
        # Alle 10 Iterationen Präzision erhöhen (langsam ansteigend)
        if current_iteration % 10 == 0:
            new_precision = precision + 100
            decimal.getcontext().prec = new_precision
            precision = new_precision
            
            # Callback aufrufen, um aktuellen Wert zu melden
            update_callback(pi, current_iteration, precision)
    
    return pi, precision, current_iteration

def save_to_file(pi_value, precision, iterations, elapsed_time):
    """Speichert den berechneten Pi-Wert in einer Textdatei."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pi_berechnung_{timestamp}.txt"
    
    with open(filename, "w") as file:
        file.write(f"Pi-Berechnung\n")
        file.write(f"Erreichte Präzision: ~{precision} Stellen\n")
        file.write(f"Durchgeführte Iterationen: {iterations}\n")
        file.write(f"Berechnungszeit: {elapsed_time:.2f} Sekunden\n\n")
        file.write(str(pi_value))
    
    return filename

def display_pi(pi_value, max_display=1000):
    """Zeigt Pi auf dem Bildschirm an (mit Begrenzung für sehr große Werte)."""
    pi_str = str(pi_value)
    
    # Bildschirm leeren und neue Ausgabe starten
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Aktuelle Pi-Berechnung:")
    print("-" * 60)
    
    print("Pi =", pi_str[:2], end="")  # Zeigt "3."
    
    # Zeigt die Nachkommastellen in Blöcken von 10 für bessere Lesbarkeit
    display_length = min(max_display + 2, len(pi_str))
    
    for i in range(2, display_length):
        if (i - 2) % 10 == 0:
            print(" ", end="")
        if (i - 2) % 50 == 0 and i > 2:
            print("\n    ", end="")
        print(pi_str[i], end="")
    
    # Bei sehr großen Zahlen anzeigen, dass die Ausgabe gekürzt wurde
    if len(pi_str) > display_length:
        print(f"\n... (weitere {len(pi_str) - display_length} Stellen werden berechnet)")
    
    print("\n" + "-" * 60)

def calculate_pi(time_limit=None):
    """Hauptfunktion zur kontinuierlichen Berechnung von Pi mit optionalem Zeitlimit."""
    print("Starte kontinuierliche Pi-Berechnung" + 
          (f" (Zeitlimit: {time_limit} Sekunden)" if time_limit else ""))
    print("Die Genauigkeit erhöht sich mit der Laufzeit.")
    print("Drücken Sie Strg+C, um die Berechnung jederzeit zu beenden.")
    
    # Event zum Stoppen der Berechnung
    stop_event = threading.Event()
    
    # Aktuelle Berechnungsergebnisse
    current_results = {
        "pi": None,
        "precision": BASE_PRECISION,
        "iterations": 0,
        "last_update": time.time()
    }
    
    # Callback-Funktion für Updates aus dem Berechnungsthread
    def update_results(pi, iterations, precision):
        current_results["pi"] = pi
        current_results["iterations"] = iterations
        current_results["precision"] = precision
        
        # Nur alle 2 Sekunden den Bildschirm aktualisieren (reduziert Flackern)
        current_time = time.time()
        if current_time - current_results["last_update"] > 2:
            display_pi(pi)
            elapsed = current_time - start_time
            print(f"Laufzeit: {elapsed:.2f} Sekunden | Iterationen: {iterations} | Präzision: ~{precision} Stellen")
            current_results["last_update"] = current_time
    
    # Funktion für den Berechnungsthread
    def calculation_thread():
        try:
            pi, final_precision, iterations = chudnovsky_algorithm(
                BASE_PRECISION, 
                update_results,
                stop_event
            )
            current_results["pi"] = pi
            current_results["precision"] = final_precision
            current_results["iterations"] = iterations
        except Exception as e:
            print(f"\nFehler während der Berechnung: {e}")
    
    # Timer-Funktion für Zeitlimit
    def timeout_thread():
        time.sleep(time_limit)
        print("\nZeitlimit erreicht, Berechnung wird beendet...")
        stop_event.set()
    
    # Startzeit erfassen
    start_time = time.time()
    
    # Thread für die Berechnung starten
    thread = threading.Thread(target=calculation_thread)
    thread.daemon = True
    thread.start()
    
    # Wenn ein Zeitlimit gesetzt ist, Timer starten
    if time_limit:
        timer = threading.Thread(target=timeout_thread)
        timer.daemon = True
        timer.start()
    
    # Auf Abschluss der Berechnung warten oder manuelle Unterbrechung
    try:
        while thread.is_alive():
            thread.join(0.1)  # Kurzes Warten, um Tastatureingaben zu ermöglichen
    except KeyboardInterrupt:
        print("\nBerechnung manuell abgebrochen...")
    finally:
        # Berechnung stoppen
        stop_event.set()
        # Kurz warten, um dem Thread Zeit zum Beenden zu geben
        time.sleep(0.5)
    
    # Endzeit erfassen
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Abschließende Anzeige
    if current_results["pi"]:
        pi_value = current_results["pi"]
        precision = current_results["precision"]
        iterations = current_results["iterations"]
        
        display_pi(pi_value)
        
        print(f"\nBerechnung abgeschlossen nach {elapsed_time:.2f} Sekunden")
        print(f"Durchgeführte Iterationen: {iterations}")
        print(f"Erreichte Präzision: ~{precision} Stellen")
        
        filename = save_to_file(pi_value, precision, iterations, elapsed_time)
        print(f"Ergebnis wurde in {filename} gespeichert")
        
        return pi_value, precision
    else:
        print("Keine Ergebnisse (Berechnung wurde zu früh abgebrochen)")
        return None, 0

def main():
    """Hauptprogramm mit Benutzeroberfläche."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("Kontinuierliche Pi-Berechnung".center(60))
    print("=" * 60)
    print("Dieses Programm berechnet Pi kontinuierlich mit steigender Genauigkeit,")
    print("bis die festgelegte Zeit abgelaufen ist oder Sie die Berechnung abbrechen.")
    print("=" * 60)
    
    try:
        use_time_limit = input("Zeitlimit festlegen? (j/n): ").lower() == 'j'
        time_limit = None
        
        if use_time_limit:
            time_limit = float(input("Zeitlimit in Sekunden: "))
        
        print("\nBerechnung startet...")
        print("Drücken Sie Strg+C, um die Berechnung jederzeit abzubrechen.")
        time.sleep(2)  # Kurze Pause, damit der Benutzer die Meldung lesen kann
        
        calculate_pi(time_limit)
        
    except ValueError:
        print("Fehler: Bitte geben Sie eine gültige Zahl ein.")
    except KeyboardInterrupt:
        print("\nProgramm wurde vom Benutzer beendet.")
    
    print("\nDanke für die Verwendung dieses Programms!")

if __name__ == "__main__":
    main()