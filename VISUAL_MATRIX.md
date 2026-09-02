# 📊 Matricea de Validare Vizuală a Interfeței: Smart City Cluj IoT

Acest document cataloghează capturile de ecran oficiale din cadrul portofoliului personal, demonstrând conformitatea stilistică Navy și integrarea grafică fluidă a datelor IoT din Cluj-Napoca.

---

## 1. Galeria Ecranelor Core (Interfața de Producție)

### 🖥️ 01 — Dashboard-ul Central Urban (`pages/1_Dashboard.py`)
- **Descriere**: Ecranul principal de monitorizare live. Afișează grila colorată de senzori (Temperatură, Aer, Trafic, Zgomot, Sol) din cartierele selectate, integrată cu harta geospațială nativă Mapbox pentru localizarea exactă a senzorilor din Cluj-Napoca.
- **Element Cheie**: Banner-ul dinamic roșu de tip `st.error` pentru alerte critice imediate (Caniculă sau Poluare severă), corelat instantaneu cu logul local de pe disc.

### 📈 02 — Panoul de Analiză și Modele Predictive AI (`pages/3_Analytics.py`)
- **Descriere**: Afișează graficele liniare de tendințe extrase direct din tabela SQLite. Include secțiunea Machine Learning (Scikit-Learn) unde operatorii simulează comportamentul indicilor pe pași de timp viitori, corelând traficul auto cu degradarea calității aerului urban.
- **Element Cheie**: Tabelul de date istorice și graficele interactive Plotly formate complet cu parametrul nativ stabil `use_container_width=True`.

---

## 2. Matricea de Validare a Securității (Cybersecurity Validation)

### 🛡️ 03 — Auditul Securizat și Jurnalizarea Live
- **Descriere**: Captură de ecran din pagina principală care demonstrează randarea în timp real a blocului de cod pentru `security_alerts.log`. Jurnalul de audit urban local rulează asincron și captează breșele de mediu sub scutul anti-duplicat de tip cooldown de 10 secunde.

---

## 3. Matricea de Validare MLOps (Promptfoo Suite)

### 🟢 04 — Ecranul de Succes Promptfoo (`promptfoo view`)
- **Descriere**: Interfața grafică locală deschisă în browser care afișează tabelul curat de evaluări. Confirmă rularea cu succes a celor 8 scenarii de test extinse din Cluj-Napoca (Mărăști, Gheorgheni, Zorilor, Mănăștur, Centru, Parcul Central, Tetarom, Florești), raportând un scor impecabil de **100% passed (8/8 cases)** utilizând modelul stabil de mare viteză Qwen 3.6-27B apelat prin workflow-ul unificat `uvx`.
