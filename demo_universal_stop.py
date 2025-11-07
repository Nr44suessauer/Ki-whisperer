#!/usr/bin/env python3
"""
Demo: Stop-Button für Downloads und Chat-Generation
Zeigt die erweiterte Stop-Funktionalität für beide Szenarien
"""

import time
import threading

class UniversalStopDemo:
    """Demo der universellen Stop-Funktionalität"""
    
    def __init__(self):
        self.generation_stopped = False
        self.download_stopped = False
    
    def demonstrate_all_stop_scenarios(self):
        """Zeigt alle Stop-Szenarien"""
        print("🛑 UNIVERSAL STOP-BUTTON DEMO")
        print("=" * 60)
        print("Der Stop-Button kann jetzt sowohl Generation als auch Downloads stoppen!")
        
        print("\n1️⃣ SZENARIO: Chat-Generation stoppen")
        self.demo_chat_stop()
        
        print("\n\n2️⃣ SZENARIO: Model-Download stoppen")
        self.demo_download_stop()
        
        print("\n\n3️⃣ SZENARIO: UI-Zustandsänderungen")
        self.demo_ui_states()
        
        self.print_summary()
    
    def demo_chat_stop(self):
        """Simuliert Chat-Generation mit Stop"""
        print("=" * 40)
        print("🤖 CHAT-GENERATION")
        print("Stop-Button: 🔴 AKTIV - Text: 'Stop'")
        
        self.generation_stopped = False
        
        def stop_after_delay():
            time.sleep(2.5)
            self.generation_stopped = True
            print("\n  🛑 STOP GEDRÜCKT!")
        
        stop_thread = threading.Thread(target=stop_after_delay, daemon=True)
        stop_thread.start()
        
        print("\n🤖 Modell generiert: ", end="", flush=True)
        
        words = ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
        for i, word in enumerate(words):
            if self.generation_stopped:
                print("\n❌ Generation abgebrochen")
                print("🔄 UI: Stop deaktiviert, Send aktiviert")
                print("💾 Unvollständige Antwort NICHT gespeichert")
                break
            
            print(f"{word} ", end="", flush=True)
            time.sleep(0.4)
        
        if not self.generation_stopped:
            print("✓ Vollständig generiert")
    
    def demo_download_stop(self):
        """Simuliert Model-Download mit Stop"""
        print("=" * 40)
        print("📥 MODEL-DOWNLOAD")
        print("Stop-Button: 🔴 AKTIV - Text: 'Stop Download'")
        
        self.download_stopped = False
        
        def stop_after_delay():
            time.sleep(3)
            self.download_stopped = True
            print("\n  🛑 STOP GEDRÜCKT!")
        
        stop_thread = threading.Thread(target=stop_after_delay, daemon=True)
        stop_thread.start()
        
        print("\n📡 Download llama2:7b:")
        
        # Simuliere Download-Progress
        for progress in range(0, 100, 15):
            if self.download_stopped:
                print(f"\n🛑 DOWNLOAD STOPPED at {progress}%")
                print("🔄 UI: Progress ausgeblendet, Stop deaktiviert")
                print("🗑️  Unvollständige Download-Daten verworfen")
                break
            
            print(f"📊 {progress}% (downloading layers...)")
            time.sleep(0.6)
        
        if not self.download_stopped:
            print("✅ Download komplett")
    
    def demo_ui_states(self):
        """Zeigt UI-Zustandsübergänge"""
        print("=" * 40)
        print("🖱️  UI-ZUSTANDSMASCHINE")
        
        states = [
            ("🟢 Idle", "Send: ✅", "Stop: ❌", "Text: 'Stop'"),
            ("🔄 Chat Generation", "Send: ❌", "Stop: ✅", "Text: 'Stop'"),
            ("📥 Model Download", "Send: ❌", "Stop: ✅", "Text: 'Stop Download'"),
            ("🛑 Stopped (Any)", "Send: ✅", "Stop: ❌", "Text: 'Stop'"),
            ("🟢 Back to Idle", "Send: ✅", "Stop: ❌", "Text: 'Stop'")
        ]
        
        for state, send, stop, text in states:
            print(f"\n{state}:")
            print(f"  • {send}")
            print(f"  • {stop}")
            print(f"  • {text}")
            time.sleep(0.8)
    
    def print_summary(self):
        """Druckt Zusammenfassung"""
        print("\n" + "=" * 60)
        print("✅ IMPLEMENTIERTE FEATURES")
        print("=" * 60)
        
        features = [
            "🔴 Universeller roter Stop-Button",
            "🤖 Stoppt Chat-Generation sofort",
            "📥 Stoppt Model-Downloads sofort", 
            "🔄 Intelligente UI-Zustandsverwaltung",
            "📝 Kontextuelle Button-Labels ('Stop' / 'Stop Download')",
            "🛡️  Thread-sichere Implementierung",
            "💾 Verhindert Speicherung unvollständiger Daten",
            "🖥️  Konsolen-Feedback bei Stop-Aktionen",
            "⚡ Sofortige Reaktion ohne Verzögerung"
        ]
        
        for feature in features:
            print(f"✅ {feature}")
            time.sleep(0.3)
        
        print("\n" + "=" * 60)
        print("🎯 VERWENDUNG")
        print("=" * 60)
        print("📤 Chat senden → Stop-Button wird aktiv (rot)")
        print("📥 Download starten → Stop-Button wird aktiv mit 'Stop Download'")
        print("🛑 Stop klicken → Sofortiger Abbruch + UI-Reset")
        print("🔄 Bereit für neue Aktion")
        
        print("\n💡 TECHNISCHE DETAILS:")
        print("• generation_stopped + download_stopped Flags")
        print("• Thread-Referenzen für saubere Verwaltung")
        print("• Stop-Checks in Stream-Loops")
        print("• Automatisches UI-Reset nach Stop")

def main():
    """Hauptdemo"""
    demo = UniversalStopDemo()
    demo.demonstrate_all_stop_scenarios()

if __name__ == "__main__":
    main()