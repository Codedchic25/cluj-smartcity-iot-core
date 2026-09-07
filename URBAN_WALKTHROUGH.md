# 🏙️ Ghid de Parcurgere și Validare Interactivă (Urban Walkthrough)

Acest document însoțește evaluatorul pas cu pas prin toate modulele platformei **Smart City Cluj-Napoca IoT**, demonstrând funcționalitatea end-to-end și deciziile tehnice luate.

---

## 🛠️ Pasul 1: Bootstrapping și Inițializarea Determinista a Datelor

Înainte de a lansa interfața grafică, trebuie să generăm structura relațională locală și să inserăm markerii geospațiali pentru cele 8 stații de monitorizare din Cluj-Napoca (Mărăști, Gheorgheni, Zorilor, Mănăștur, Centru, Parcul Central, Tetarom, Florești).

1. Deschideți un terminal în rădăcina proiectului: `C:\Users\user\Documents\Smart-City-Cluj-IoT`
2. Executați scriptul de seed tranzacțional utilizând managerul rapid `uv`:
   ```bash
   uv run python seed_db.py
   ```
3. Pentru a verifica integritatea structurală a tabelelor SQLite create (`city_stats`, `sensors`, `settings`) și utilizarea corectă a driverului asincron SQLAlchemy 2.0, puteți rula utilitarul de diagnoză local:
   ```bash
   uv run python check_db.py
   ```

---

## 🔒 Pasul 2: Autentificarea Securizată a Operatorului

1. Porniți serverul local Streamlit:
   ```bash
   uv run streamlit run main.py
   ```
2. Accesați adresa indicată în browser (`http://localhost:8501`).
3. Interfața va fi blocată instantaneu de ecranul securizat de login. Introduceți acreditările izolate în fișierul `.env`. Scriptul folosește `st.stop()` pentru a preveni încărcarea memoriei cache sau randarea parțială a datelor înainte de introducerea parolei corecte.

---

## 📡 Pasul 3: Monitorizarea Live și Logica de Alertare (Dashboard)

1. Navigați la pagina **`1_Dashboard.py`**. Veți observa cele 5 coloane simetrice de KPI-uri telemetrice live și harta nativă Mapbox.
2. Schimbați limba platformei din selectorul global. Callback-ul `dashboard_lang_callback` va propaga instantaneu pachetul lingvistic din `translations.py` în toate cele 5 limbi suportate (RO, EN, IT, ES, HU), forțând un `st.rerun()` curat.
3. Pentru a simula o breșă critică de mediu, generatorul asincron din `app/services/producer.py` va împinge o valoare ce depășește pragurile imutabile (ex: Calitatea Aerului PM2.5 > 80.0 sau Temperatură > 32.0°C).
4. **Validarea Scutului Anti-Flood:** În acel moment, o alertă roșie `st.error` va apărea pe ecran. Utilitarul `src/utils/local_alerts.py` va intercepta anomalia și va scrie o singură linie de audit în fișierul fizic `security_alerts.log`. Datorită cooldown-ului de 10 secunde, trimiterile succesive de date identice din aceeași secundă vor fi blocate, eliminând fenomenele de *I/O Lock* pe disc sau consumul inutil de resurse.

---

## 🔬 Pasul 4: Evaluarea Predictivă și Inteligența Artificială (Analytics)

1. Navigați la pagina **`3_Analytics.py`**.
2. **Prognoza Clasic ML:** Selectați un parametru urban. Algoritmul de Regresie Liniară din `scikit-learn` preia istoricul din SQLite, transformă timestamp-urile într-un vector numeric NumPy pur și generează pe graficul Plotly următoarele 3 puncte de tendință. Graficul randează instantaneu fără blocaje de cache vizual, datorită utilizării unei chei dinamice în milisecunde (`dynamic_ms`) și a parametrului stabil `use_container_width=True`.
3. **Operational Reasoning (Qwen Engine):** În subsolul paginii, asistentul AI contextual este pregătit pentru interogare. La trimiterea unei cereri, funcția `get_latest_alerts_context()` citește prin byte-stream ultimele 5 linii din fișierul `security_alerts.log`.
4. Acest context dens este injectat în promptul din `ai_tests/prompts.txt`, iar modelul **Qwen 3.6-27B** generează o recomandare administrativă ultra-personalizată în maximum 3 fraze. Răspunsul este stocat securizat în `st.session_state` pentru a rezista ciclului de auto-refresh de 5 secunde al interfeței.

---

## 🧪 Pasul 5: Validarea DevOps și MLOps (Suita de Teste)

Pentru a demonstra reziliența aplicației în medii de integrare continuă (CI/CD) înainte de deployment-ul final, rulați manual suita de teste unitare și matricea de siguranță semantică:

1. **Testarea Unitara Offline (Pytest):**
   ```bash
   uv run pytest ai_tests/test_alerts_offline.py -v -s
   ```
   Această comandă validează izolarea completă a tranzacțiilor, integritatea matricei de traduceri din `translations.py` și comportamentul inegalităților stricte matematice la valorile limită.
2. **Evaluarea Promptfoo Matrix:**
   ```bash
   uvx promptfoo eval --no-cache
   ```
   Această comandă pornește execuția celor 8 scenarii din Cluj-Napoca utilizând aserțiuni ultra-rapide de tip `substring` direct pe modelul Qwen, certificând un scor impecabil de **100% passed (8/8 cases)** fără interogări ascunse către API-uri cloud terțe.
