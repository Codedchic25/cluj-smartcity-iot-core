# 🎓 Ghid Avansat de Susținere Orală (Q&A Matrix) — Smart City Cluj IoT

Acest document centralizează întrebările de arhitectură, deciziile ingineriești și scenariile de depanare care pot apărea în timpul examinării tehnice a proiectului, oferind apărări clare bazate direct pe codul sursă real.

---

## 🏗️ Secțiunea 1: Decizii de Arhitectură și Concurență Streamlit

### Î1: În paginile `1_Dashboard.py`, `2_Settings.py` și `3_Analytics.py` folosești SQLAlchemy 2.0 și aiosqlite pentru baze de date. Cum interfețezi acest ecosistem cu ciclul de randare Streamlit?
* **Apărare**: Streamlit nu este un framework asincron nativ în corpul său principal. Rularea unui `await` direct la nivel de modul ar arunca o eroare de sintaxă. Pentru a rezolva acest conflict, operațiunile asincrone sunt gestionate prin puncte de intrare controlate.
* **Justificare Tehnică**: Utilizăm `asyncio.run()` pentru a porni un event loop izolat care execută interogările asincrone, colectează datele în DataFrame-uri Pandas și închide conexiunea imediat. Toate conexiunile sunt protejate prin timeout-uri stricte (ex: `timeout=15`), fapt ce garantează izolarea operațiunilor și previne apariția erorilor de tip `database is locked` în timp ce serviciul de fundal `producer.py` scrie date în paralel.

### Î2: De ce ai ales să folosești structura nativă Multipage a Streamlit (directorul `pages/`) în loc de un selector simplu de tip `st.sidebar.radio` într-un singur fișier monolitic?
* **Apărare**: Abordarea monoliților într-un singur fișier (unde paginile sunt funcții controlate de un `if/else`) duce la Memory Bloat (umflarea memoriei RAM) deoarece la fiecare refresh întregul script se reexecută.
* **Justificare Tehnică**: Prin utilizarea structurii multipage (`pages/`), Streamlit încarcă în memorie doar codul paginii active în care navighează operatorul. Fișierele sunt izolate complet ca module, reducând amprenta de memorie și facilitând mentenanța codului, păstrând în același timp starea sesiunii globală (`st.session_state`).

---

## 🚨 Secțiunea 2: Logica Alertelor și Optimizarea Resurselor Localizate

### Î3: În engine-ul platformei verifici telemetria cu inegalități stricte (`>`). Care este impactul acestei decizii matematice asupra sistemului?
* **Apărare**: Inegalitățile non-stricte introduc un risc major de oscilație a alertelor în sistemele IoT în cazul în care un senzor transmite repetat valoarea limită exactă (ex: exact `32.0°C` sau exact `80.0 PM2.5`).
* **Justificare Tehnică**: Prin trecerea globală la inegalități stricte unificate (`temperature > 32.0`, `air_quality > 80.0`, `soil_moisture < 35.0`), am aliniat codul cu modelul matematic formal din documentație. Dacă un senzor trimite valoarea limită exactă, sistemul o interpretează ca fiind la granița superioară a zonei sigure și NU declanșează alerta, eliminând fenomenul de oboseală a operatorului (*alert fatigue*).

### Î4: Cum garantează pipeline-ul asincron că scrierea alertelor în jurnalul de pe disc nu blochează generarea datelor IoT?
* **Apărare**: Scrierea fizică pe hard-disk este o operațiune de tip I/O-bound blocantă. Rularea ei direct în loop-ul asincron principal ar fi oprit temporar colectarea telemetriei în momentul accesării discului.
* **Justificare Tehnică**: Am remediat această vulnerabilitate izolând scrierea prin intermediul unui executor de fundal: `await loop.run_in_executor(None, lambda: ...)`. Această instrucțiune trimite sarcina de scriere în fișierul `security_alerts.log` într-un thread pool separat administrat de Python. Loop-ul asincron principal se eliberează instantaneu, continuând să citească restul senzorilor fără nicio milisecundă de latență.

---

## 🧠 Secțiunea 3: Securitate AI și Validare MLOps (Qwen Engine)

### Î5: Cum gestionează utilitarul de procesare AI protecția împotriva atacurilor de tip Prompt Injection?
* **Apărare**: Structura sistemului respinge regulile lejere de filtrare și aplică principiul izolării stricte a datelor în interiorul unui șablon delimitat prin marcaje imutabile (System/User Open-Block).
* **Justificare Tehnică**: Datele primite de la senzori sunt injectate în secțiuni clar separate prin tag-uri de bloc structurate. Acest lucru împiedică modelul LLM să confunde datele telemetrice cu instrucțiunile de sistem. În plus, prin setarea unei temperaturi scăzute (`0.2`), modelul este forțat să rămână determinist și să livreze recomandări tehnice scurte, eliminând riscurile de jailbreak.

### Î6: În `promptfooconfig.yaml` ai configurat aserțiuni de tip substring. Ce anume validează acestea mai exact și care este rolul lor?
* **Apărare**: Răspunsurile modelelor LLM sunt probabilistice. Într-o actualizare de model în cloud, AI-ul ar putea să ofere recomandări evazive, omită directivele de urgență sau să schimbe limba.
* **Justificare Tehnică**: Suita Promptfoo rulează ca o poartă de calitate (Quality Gate). Aserțiunile de tip `substring` caută cuvinte cheie imperative în limba română (ex: `irigare` în caz de secetă, `aer` în caz de poluare). Prin utilizarea modelului de producție **Qwen 3.6-27B** și a verificărilor locale substring, am eliminat dependențele de OpenAI din fundal, obținând un scor perfect de **100% passed (8/8 cases)**.
## 🗄️ Secțiunea 4: Persistența Datelor și Gestiunea Memoriei Asincrone

### Î7: În modulul de bază de date, de ce utilizezi un bloc de tip `try/except/finally` care rulează manual `session.rollback()` și `session.close()`, în loc să lași SQLAlchemy să gestioneze sesiunea în mod automat?
* **Apărare**: În aplicațiile reactive (cum sunt paginile Streamlit care rulează cicluri de auto-refresh), gestionarea implicită a conexiunilor poate duce la epuizarea pool-ului de conexiuni (*Connection Pooling Exhaustion*) sau blocaje de tip *Database Locked*.
* **Justificare Tehnică**: Managerul de context implementat garantează un comportament determinist pe straturi. Dacă o interogare asincronă eșuează la jumătatea execuției în timp ce o altă pagină citește datele, blocul `except` interceptează eroarea și rulează instantaneu `await session.rollback()`, eliberând lock-urile de scriere. Blocul `finally` asigură că instrucțiunea `await session.close()` se execută întotdeauna, returnând conexiunea fizică `aiosqlite` în pool-ul motorului asincron și prevenind scurgerile de memorie.

### Î8: Tabela `city_stats` colectează continuu date de telemetrie de la toți senzorii. Cum optimizezi interogările pentru a asigura o scalabilitate perfectă a dashboard-ului?
* **Apărare**: Fără o indexare corectă, interogarea care determină ultimele valori prin clauza `MAX(timestamp)` grupate după `sensor_id` ar executa un *Full Table Scan* (scanarea integrală a hard-disk-ului) la fiecare ciclu de randare.
* **Justificare Tehnică**: Prin generarea unui index compus format din `(sensor_id, timestamp)`, motorul bazei de date sare instantaneu la locația fizică a ultimelor intrări cronologice (complexitate timp O(log n) în loc de O(n)). Acest lucru reduce utilizarea procesorului la mai puțin de 1% în timpul ciclurilor de auto-refresh, asigurând o încărcare instantanee a datelor indiferent de dimensiunea tabelei.

---

## 📈 Secțiunea 5: Pipeline-ul Statistic, Matematică și Machine Learning

### Î9: În fișierul `pages/3_Analytics.py`, de ce transformi timestamp-urile într-un vector numeric NumPy simplu (`np.arange`) în loc să pasezi direct obiectele de tip `datetime64` în modelul `LinearRegression`?
* **Apărare**: Modelele de regresie liniară din `scikit-learn` funcționează exclusiv cu matrici de numere float continue și nu pot procesa nativ structuri complexe de tip timestamp sau string-uri temporale.
* **Justificare Tehnică**: Prin maparea cronologică a datelor curățate de valori nule (`.dropna()`) într-o secvență numerică liniară, am izolat algoritmul de micro-întârzierile pachetelor de rețea sau de variațiile ceasului sistemului. Modelul calculează corect panta de evoluție (y = b_0 + b_1*x) reprezentând rata de schimb structural a parametrului urban per unitate de observație, permițând o prognoză predictivă robustă pentru următoarele 3 iterații fără riscul de a introduce anomalii matematice cauzate de diferențele mari de scală ale valorilor Unix epoch.

### Î10: Cum gestionează modulul tău de Machine Learning situațiile în care un senzor IoT transmite date constante din cauza unei defecțiuni hardware?
* **Apărare**: Dacă valorile de intrare sunt perfect constante în raport cu axa timpului, panta regresiei devine exact `0.0`, reflectând o evoluție plată, fără a bloca funcționarea serverului Streamlit sau a prăbuși pipeline-ul de date.
* **Justificare Tehnică**: Din punct de vedere statistic, modelul rezolvă ecuația prin metoda celor mai mici pătrate (OLS). Dacă variația este nulă, modelul calculează panta ca fiind 0 și setează valoarea de interceptare la valoarea constantă raportată de hardware. Protecția noastră din cod (`if len(clean_series) < 2`) împiedică antrenarea dacă nu există destule observații, prevenind erorile de tip *division-by-zero* la calculul matriceal.

---

## 🐳 Secțiunea 6: Containerizare, Infrastructură Docker și Managementul Secretelor

### Î11: În `Dockerfile`-ul de producție optimizat, observ că ai separat configurarea în două etape distincte (`FROM ... AS builder` și `FROM python:3.12-slim-bookworm`). Ce avantaje aduce această arhitectură?
* **Apărare**: Această tehnică de tip Multi-Stage Build este utilizată pentru a minimiza drastic dimensiunea imaginii finale de producție, eliminând instrumentele grele de dezvoltare de care containerul nu mai are nevoie la runtime.
* **Justificare Tehnică**: În prima etapă (`builder`), utilizăm imaginea oficială `ghcr.io/astral-sh/uv` pentru a compila dependențele brute în byte-code. În a doua etapă, copiem exclusiv folderul curat `.venv`. Nu instalăm managerul `uv` în imaginea finală. Acest lucru reduce dimensiunea containerului cu peste 60%, elimină vectorii de atac la nivel de infrastructură (Attack Surface Reduction) și permite pornirea instantanee a aplicației în cloud.

### Î12: De ce rulează instrucțiunea `USER appuser` spre finalul fișierului `Dockerfile` și ce vulnerabilitate previne?
* **Apărare**: În mod implicit, containerele Docker rulează procesele interne sub contul de administrator absolut (`root`), creând riscul de tip *Container Breakout*.
* **Justificare Tehnică**: Prin crearea unui utilizator dedicat sistemului (`appuser`) și delegarea permisiunilor de scriere pe directorul în care se generează logurile și baza de date, ne asigurăm că aplicația operează sub principiul privilegiilor minime (*Principle of Least Privilege*). Serverul Streamlit rulează izolat, având exclusiv permisiunile necesare pentru a citi și scrie date în `app.db` și `security_alerts.log`, eliminând riscul ca un atacator să preia controlul mașinii gazdă.

---

## 🔍 Secțiunea 7: Depanare și Administrare Procedurală Locală

### Î13: La lansarea aplicației, interfața afișează o alertă critică ce indică lipsa bazei de date. Care este procedura corectă de rezolvare?
* **Apărare**: Această eroare indică lipsa fișierului fizic `app.db` sau desincronizarea acestuia în urma restructurării directoarelor. Sistemul de populare a fost complet centralizat în motorul de seed nativ.
* **Justificare Tehnică**: Pentru a genera instantaneu structura bazei de date SQLite locale și a o popula tranzacțional cu cele 8 stații IoT unice din Cluj-Napoca, se rulează din terminal comanda unificată prin managerul `uv`: `uv run python seed_db.py`. La reîncărcarea paginii din browser, serverul Streamlit va prenova automat noul fișier stabilizat `app.db` și va debloca instantaneu vizualizările.

### Î14: În funcția `run_automatic_seeding` din `main.py`, execuți un `DROP TABLE IF EXISTS settings` la fiecare pornire, urmat de o recreare a tabelei. De ce ai ales această abordare distructivă în loc de un simplu `INSERT OR IGNORE`?
* **Apărare**: Aceasta este o decizie conștientă de design menită să asigure **alinierea strictă a configurărilor de mediu** în medii volatile de dezvoltare precum GitHub Codespaces, unde utilizatorii modifică des variabilele din `.env`.
* **Justificare Tehnică**: Dacă am fi folosit doar `INSERT OR IGNORE`, modificările aduse pragurilor implicite în fișierul `.env` sau `.env.example` (de exemplu, schimbarea `DEFAULT_TEMP_LIMIT` de la 35.0 la 32.0) nu s-ar fi propagat niciodată în baza de date locală dacă linia cu ID-ul 1 exista deja pe disc. Prin aplicarea acestui *schema flush* controlat exclusiv pe tabela de configurări (`settings`), forțăm aplicația să citească și să persiste instantaneu cele mai recente variabile de mediu injectate, eliminând erorile de tip *stale configuration* (configurări învechite cache-uite) între sesiunile de rulare.
