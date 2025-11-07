#!/usr/bin/env python3
"""
Demo: Anti-Redundanz Konsolen-Ausgabe
Zeigt den Unterschied zwischen alter (redundanter) und neuer (optimierter) Ausgabe
"""

import sys
import time

def demo_alte_redundante_ausgabe():
    """Simuliert die alte redundante Ausgabe wie in Ihrem Beispiel"""
    print("=" * 60)
    print("🔴 ALTE REDUNDANTE AUSGABE (wie vorher):")
    print("=" * 60)
    
    text = "The Pythagorean theorem, also known as Pythagoras' theorem, is a fundamental concept in geometry that describes the relationship between the lengths of the sides of a right triangle. The theorem states that for a right triangle with legs of length a and b, and a hypotenuse (the side opposite the right angle) of length c, the following equation holds: a^2 + b^2 = c^2"
    
    words = text.split()
    current_text = ""
    
    for i, word in enumerate(words):
        current_text += word + " "
        
        # Alte Methode: Drucke ALLES neu bei jedem Token
        print(f"[13:36:{48+i//10}] 🤖 llama2:13b:")
        print(current_text.strip())
        print()
        time.sleep(0.1)  # Simulation der Streaming-Verzögerung
        
        if i >= 15:  # Nur ersten Teil für Demo
            break

def demo_neue_anti_redundanz_ausgabe():
    """Simuliert die neue Anti-Redundanz Ausgabe"""
    print("\n" + "=" * 60)
    print("🟢 NEUE ANTI-REDUNDANZ AUSGABE (optimiert):")
    print("=" * 60)
    
    text = "The Pythagorean theorem, also known as Pythagoras' theorem, is a fundamental concept in geometry that describes the relationship between the lengths of the sides of a right triangle. The theorem states that for a right triangle with legs of length a and b, and a hypotenuse (the side opposite the right angle) of length c, the following equation holds: a^2 + b^2 = c^2"
    
    words = text.split()
    current_text = ""
    
    print("🤖 llama2:13b: ", end="", flush=True)
    
    for i, word in enumerate(words):
        current_text += word + " "
        
        # Neue Methode: Überschreibe nur eine Zeile, zeige nur relevanten Teil
        if i % 5 == 0:  # Update nur alle 5 Wörter
            # Zeige nur die letzten 15 Wörter + "..."
            display_words = current_text.split()
            if len(display_words) > 15:
                display = "... " + " ".join(display_words[-15:])
            else:
                display = current_text
            
            # Überschreibe die vorherige Zeile
            sys.stdout.write('\r' + ' ' * 100 + '\r')
            sys.stdout.write(f"🤖 llama2:13b: {display}")
            sys.stdout.flush()
        
        time.sleep(0.1)
        
        if i >= 30:  # Mehr Wörter für bessere Demo
            break
    
    # Finale Ausgabe mit Checkmark
    final_words = current_text.split()
    if len(final_words) > 20:
        final_display = "..." + " ".join(final_words[-20:]) + " ✓"
    else:
        final_display = current_text + " ✓"
    
    sys.stdout.write('\r' + ' ' * 100 + '\r')
    print(f"🤖 llama2:13b: {final_display}")

def main():
    print("🔧 ANTI-REDUNDANZ DEMO")
    print("Zeigt den Unterschied zwischen alter und neuer Konsolen-Ausgabe\n")
    
    # Demo der alten redundanten Methode
    demo_alte_redundante_ausgabe()
    
    # Pause zwischen Demos
    print("\n⏳ Pause zwischen Demos...")
    time.sleep(2)
    
    # Demo der neuen Anti-Redundanz Methode
    demo_neue_anti_redundanz_ausgabe()
    
    print("\n\n" + "=" * 60)
    print("✅ ZUSAMMENFASSUNG:")
    print("=" * 60)
    print("🔴 Alt: Jedes Token → komplette Antwort neu drucken")
    print("   → Führt zu überfüllter, redundanter Konsole")
    print()
    print("🟢 Neu: Nur eine Zeile überschreiben + relevanter Kontext")
    print("   → Saubere, übersichtliche Konsolen-Ausgabe")
    print("   → Zeigt nur die letzten ~15-20 Wörter")
    print("   → Updates nur alle 50 Zeichen für weniger Spam")
    print("   → Finale Bestätigung mit ✓")

if __name__ == "__main__":
    main()