# 🛡️ Interview Defense Guide — Smart City Cluj-Napoca

Acest ghid concentrează deciziile de design, compromisurile arhitecturale (trade-offs) și barierele defensive implementate în platformă. Este structurat pentru a răspunde întrebărilor de nivel Senior/Architect în timpul fazelor de evaluare tehnică a portofoliului.

---

## 🗄️ 1. Persistență & Managementul Conexiunilor (De ce SQLite + SQLAlchemy?)

### Întrebare: De ce ai ales SQLite pentru o aplicație de tip Smart City care simulează fluxuri continue de date IoT? SQLite nu are probleme la scrieri concurente?
* **Apărare**: Alegerea a fost dictată de cerințele de determinism, izolare locală și portabilitate ale unui proiect de portofoliu tehnic (zero-config, zero-infrastructure overhead pentru utilizatorul sau recruiterul care clonează codul în GitHub Codespaces).
* **Barieră implementată**: Pentru a combate limitările native SQLite legate de blocarea bazei la scrieri concurente, am implementat trei straturi defensive:
  1. Conexiunile sincrone folosesc un argument explicit de `timeout=15` în momentul deschiderii, prevenind crash-urile instantanee ale tranzacțiilor.
  2. Am configurat un context manager asincron enterprise (`@asynccontextmanager`) în `app/database/database.py` care asigură că fiecare sesiune de interogare rulează un `session.rollback()` în caz de eroare și un `session.close()` garantat la final, eliberând lock-urile de pe disc instantaneu.
  3. Suita de teste din `ai_tests/test_alerts_offline.py` rulează complet izolat, validând logica de business înainte ca datele persistente să fie modificate pe disc.

---

## 🚨 2. Izolarea Serviciilor și Logica Anti-Flood Locală (Scutul Cooldown)

### Întrebare: Ce se întâmplă dacă un senzor rămâne blocat peste pragul critic? Cum ai prevenit blocarea thread-ului principal și flood-ul de loguri?
* **Apărare**: Dependențele cloud externe introduc vulnerabilități de rețea, latențe I/O-bound mari și costuri operaționale imprevizibile. Din acest motiv, am decuplat complet platforma de servicii de mesagerie terțe (fără Twilio API), migrând întregul sistem către o jurnalizare de audit locală rapidă, securizată și izolată în fișierul `security_alerts.log`.
* **Barieră implementată**: Pentru a preveni degradarea spațiului pe disc prin scrieri masive repetitive în cazul în care un senzor defect transmite continuu anomalii, am dezvoltat un registru de cooldown în memorie în utilitarul `src/utils/local_alerts.py`. La detectarea unei abateri, sistemul blochează re-transmiterea aceleiași alerte pentru o barieră temporală strictă de 10 secunde. Orice tentativă în acest interval este respinsă direct în memorie, întorcând `False`, fără a mai accesa discul fizic.
* **Tratare defensivă**: Execuția în fundal din `app/services/producer.py` utilizează un executor asincron: `await loop.run_in_executor(None, lambda: ...)`. Această tehnică deleagă scrierea fizică în log către un thread pool separat. Loop-ul asincron principal IoT se eliberează instantaneu, continuând să genereze și să proceseze datele restului de senzori urbani cu latență zero.

```text
Măsurătoare IoT → Indice peste pragul critic (Caniculă / Poluare)
                                 │
                                 ▼
                     Barieră Temporală Cooldown
                                 │
       ┌─────────────────────────┴─────────────────────────┐
       ▼                                                   ▼
Alertă repetată în sub 10s                             Alerte noi / Interval expirat
       │                                                   │
  Scriere Blocată                                     Aprobată și Jurnalizată
  [Local Cooldown Activ]                              [security_alerts.log Updated]
       │                                                   │
Zero solicitări I/O redundante                       Thread asincron I/O eliberat
```

---

## 🧠 3. Evaluarea Deterministă a AI-ului Generativ Context-Aware

### Întrebare: Output-ul LLM-urilor este nedeterminist. Cum garantezi că recomandările asistentului AI sunt sigure, poliglote și corelate cu istoricul operațional?
* **Apărare**: În această platformă, componenta de AI este tratată ca un software clasic ce trebuie testat continuu prin metrici riguroase, nu ca o cutie neagră probabilistică. Am transformat asistentul într-un analist urban Context-Aware prin injecție dinamică de loguri reale de pe disc.
* **Barieră implementată**:
  1. În `app/ai/ai_interface.py`, am configurat funcția `get_latest_alerts_context()` care extrage prin byte-stream ultimele 5 linii din `security_alerts.log` și le injectează ca vector de context în prompt, oferind modelului memorie operațională recentă.
  2. În `app/ai/groq_provider.py`, am integrat modelul de producție **Qwen 3.6-27B** prin Groq API, configurat cu o temperatură setată strict la `0.2`, forțând răspunsuri deterministe, axate pe acțiune tehnică, în limitele a maximum 3 fraze.
  3. Suita MLOps Promptfoo (`promptfooconfig.yaml`) rulează automat în pipeline-ul CI/CD aserțiuni rapide de tip `substring` pe cele 8 scenarii din Cluj-Napoca, garantând un scor perfect de **100% succes (8/8 cazuri trecute)** fără utilizarea unor interogări ascunse către modele OpenAI.

---

## 🔐 4. Strategia Securității Stratificate (Defense in Depth)

### Întrebare: Cum ai securizat cheile de API și cum ai protejat containerul la runtime împotriva atacurilor cibernetice?
* **Apărare**: Proiectul aplică un model de securitate pe mai multe niveluri (Defense in Depth) pentru a reduce suprafața de atac locală și în cloud:
  1. **Layer-ul 1 (Secret Isolation):** Toate acreditările private (`GROQ_API_KEY`) sunt extrase complet din codul sursă și găzduite în fișierul local `.env`, exclus structural din Git prin reguli stricte în `.gitignore` și `.dockerignore`.
  2. **Layer-ul 2 (Runtime Protection):** Specificațiile din `Dockerfile` blochează utilizarea permisiunilor de tip `root`. Am creat un utilizator izolat cu drepturi minimale (`appuser`) pentru a rula serverul Streamlit, protejând mașina gazdă împotriva atacurilor de tip Container Breakout.
  3. **Layer-ul 3 (Access Control):** Componentele multipage din directorul `pages/` sunt protejate global prin starea de sesiune, utilizând oprirea execuției prin `st.stop()` în cazul în care utilizatorul nu este autentificat.

---

## 🛠️ 5. Modernizarea Ecosistemului (De ce uv și nu requirements.txt?)

### Întrebare: Am observat că ai eliminat complet fișierele tradiționale requirements.txt. Care a fost motivul tehnic?
* **Apărare**: Menținerea fișierelor `requirements.txt` introduse manual introduce un risc major de *Environment Drift* (desincronizarea versiunilor de pachete în echipă sau între mediul local și cel de producție).
* **Barieră implementată**: Sursa unică de adevăr pentru dependințe este definită strict prin standardul modern PEP 621 în `pyproject.toml`, iar rezoluția deterministă a arborelui de pachete este blocată prin `uv.lock`. Utilizarea managerului `uv` aduce build-uri de imagini Docker de până la 10 ori mai rapide datorită mecanismului avansat de caching global al straturilor, garantând instalări identice de fiecare dată prin comanda `uv sync --frozen`.

---

## 📊 6. Performanța și Threading-ul UI (De ce st_autorefresh și nu o buclă infinită?)

### Întrebare: Pentru reîmprospătarea datelor live din dashboard, de ce ai folosit st_autorefresh în loc de o buclă simplă while True în Python?
* **Apărare**: Rularea unei bucle infinite direct în thread-ul principal de UI blochează complet randarea elementelor, face pagina neresponsivă și împiedică utilizatorul să interacționeze cu widget-urile (cum ar fi schimbarea limbilor sau selectarea senzorilor).
* **Barieră implementată**: Componenta `st_autorefresh` deleagă declanșarea reîmprospătării direct către browser (pe partea de client, via JavaScript). UI-ul își încheie execuția curat, randează graficele Plotly și harta geospațială nativă Mapbox, iar la fiecare 5 secunde browserul cere o re-execuție controlată a scriptului. Acest lucru permite citirea ultimelor măsurători din tabela SQLite fără a bloca sau îngheța interfața de control urban.

## 📊 7. Idempotența și Atomicitatea Procesului de Seeding (.VENV Boundary)

### Întrebare: Dacă scriptul `seed_db.py` eșuează la jumătatea execuției în GitHub Codespaces, cum garantezi că baza de date nu rămâne într-o stare coruptă (half-baked state) care să blocheze aplicația Streamlit?
* **Apărare**: Procesul de populare a bazei de date localizate a fost proiectat să fie complet **idempotent** și **tranzacțional**, eliminând riscul de poluare a stării sistemului.
* **Barieră implementată**:
  1. În loc să alterăm direct tabelele existente, scriptul deschide o tranzacție SQL nativă și execută operațiunile sub o barieră de tip `try/except`.
  2. Curățarea datelor se face utilizând instrucțiuni de ștergere totală (`DELETE FROM`) încapsulate într-un singur bloc tranzacțional securizat.
  3. Apelul `connection.commit()` se execută **exclusiv la final**, după ce toate inserările de coordonate și praguri implicite au fost validate cu succes în memorie. Dacă apare o eroare la mijlocul procesului, modificările nu sunt scrise pe disc, garantând că `app.db` rămâne fie în starea anterioară stabilă, fie este reconstruit complet la următoarea inițializare fără a arunca excepții de tip `OperationalError` în thread-ul UI.
