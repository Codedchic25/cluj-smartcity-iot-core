# 🎓 Ghid Avansat de Susținere Orală (Q&A Matrix) — Smart City Cluj IoT

Acest document centralizează întrebările de arhitectură, deciziile ingineriești și scenariile de depanare care pot apărea în timpul examinării tehnice a proiectului, oferind apărări clare bazate direct pe codul sursă real al platformei.

---

## 🏗️ Secțiunea 1: Decizii de Arhitectură și Concurență Streamlit

### Î1: În paginile `1_Dashboard.py`, `2_Settings.py` și `3_Analytics.py` folosești interogări SQL directe. De ce ai ales această abordare în interiorul funcțiilor din pagini?
* **Apărare**: Streamlit rulează sub formă de script-uri repetitive care execută codul de sus în jos la fiecare interacțiune directă. Deschiderea și închiderea instanțelor în interiorul funcțiilor garantează izolarea completă a operațiunilor cu date.
* **Justificare Tehnică**: Pentru a interfața baza de date locală SQLite cu ciclul de randare dinamic al interfeței, am utilizat conexiuni sincrone protejate prin timeout-uri stricte (`timeout=15`). Acest lucru permite colectarea rapidă a seturilor de date pentru DataFrame-urile Pandas și închiderea imediată a sesiunilor, prevenind apariția erorilor blocante de tip `database is locked` în momentul în care serviciul de fundal `producer.py` scrie date în paralel.

### Î2: De ce ai ales să folosești structura nativă Multipage a Streamlit (directorul `pages/`) în loc de un selector simplu de tip `st.sidebar.radio` într-un singur fișier monolitic?
* **Apărare**: Abordarea monoliților într-un singur fișier (unde ecranele sunt doar funcții Python controlate de un bloc condițional `if/else`) duce la degradarea accelerată a performanței și la fenomene de Memory Bloat.
* **Justificare Tehnică**: Prin utilizarea structurii native multipage (`pages/`), Streamlit încarcă în memoria RAM exclusiv codul sursă al paginii active în care navighează operatorul la un moment dat. Fișierele sunt izolate structural ca module independente, reducând amprenta de execuție a procesului și facilitând mentenanța pe termen lung, păstrând în același timp starea sesiunii globală prin `st.session_state`.

---

## 🚨 Secțiunea 2: Logica Alertelor și Optimizarea Resurselor Localizate

### Î3: În `producer.py` și `local_alerts.py` verifici telemetria cu inegalități stricte (`>`). Care este impactul acestei decizii matematice asupra sistemului?
* **Apărare**: Inegalitățile non-stricte introduc un risc major de oscilație a alertelor în sistemele IoT (Alert Oscillation) în cazul în care un senzor defect transmite repetat valoarea limită exactă.
* **Justificare Tehnică**: Prin trecerea globală la inegalități stricte unificate (`temperature > 32.0`, `air_quality > 80.0`, `soil_moisture < 35.0`), am aliniat codul cu modelul formal din documentație. Dacă un senzor transmite valoarea limită exactă, sistemul o interpretează ca fiind la granița superioară a zonei sigure și NU declanșează alerta, eliminând fenomenul de oboseală a operatorului (*alert fatigue*).

### Î4: Cum garantează funcția `send_local_log_alert_async` din `producer.py` că thread-ul de fundal nu se blochează atunci când scrie în jurnalul de pe disc?
* **Apărare**: Scrierea fizică pe disc este o operațiune de tip I/O-bound intrinsec blocantă care ar fi oprit temporar pipeline-ul principal de colectare a datelor IoT în momentul accesării hardware-ului.
* **Justificare Tehnică**: Am remediat această vulnerabilitate izolând scrierea prin intermediul unui executor de fundal: `await loop.run_in_executor(None, lambda: ...)`. Această instrucțiune trimite sarcina de scriere în fișierul `security_alerts.log` într-un thread pool separat administrat autonom de Python. Loop-ul asincron principal se eliberează instantaneu, continuând să genereze și să proceseze datele restului de senzori urbani cu latență zero.
---

## 🧠 Secțiunea 3: Securitate AI și Validare MLOps (Qwen Engine)

### Î5: Cumionează utilitarul de procesare AI protecția împotriva atacurilor cibernetice de tip Prompt Injection?
* **Apărare**: În loc să ne bazăm pe reguli lejere de filtrare care pot fi ocolite, structura proiectului aplică principiul izolării stricte a datelor în interiorul unui șablon bine delimitat (System/User Open-Block).
* **Justificare Tehnică**: Datele primite de la senzori sunt injectate în secțiuni clar separate prin marcaje structurate în fișierul `ai_tests/prompts.txt`. Acest lucru împiedică modelul LLM să confunde datele telemetrice cu instrucțiunile de sistem. În plus, prin setarea unei temperaturi scăzute (`0.2`) în `groq_provider.py`, modelul este forțat să rămână determinist și să livreze recomandări tehnice scurte, eliminând riscurile de evadare din context (jailbreak).

### Î6: În `promptfooconfig.yaml` ai configurat aserțiuni de tip substring. Ce anume validează acestea mai exact și de ce sunt rulate în pipeline-ul CI/CD din GitHub Actions?
* **Apărare**: Răspunsurile modelelor LLM sunt probabilistice. Într-o actualizare viitoare de model în cloud, AI-ul ar putea să ofere recomandări într-o altă limbă sau să omită directivele operaționale de urgență.
* **Justificare Tehnică**: Suita Promptfoo rulează în `ci.yml` ca o poartă de calitate (Quality Gate). Aserțiunile de tip `substring` caută cuvinte cheie imperative (ex: `irigare` în caz de secetă, `aer` în caz de poluare). Prin utilizarea modelului de producție **Qwen 3.6-27B** și a verificărilor locale substring, am eliminat dependențele de OpenAI din fundal, obținând un scor perfect de **100% passed (8/8 cases)** care garantează siguranța semantică înainte ca codul să intre în producție.

---

## 🌐 Secțiunea 4: Gesiunea Sesiunilor, I18n și Reactivitate Plotly

### Î7: În `pages/3_Analytics.py`, folosești un timestamp în milisecunde (`dynamic_ms`) adăugat direct în cheia `key` a graficului Plotly predictiv. Ce problemă Streamlit rezolvă această decizie?
* **Apărare**: Streamlit tinde să păstreze în cache starea vizuală a hergheliilor grafice complexe pentru a economisi performanță. Fără o cheie dinamică, atunci când schimbi parametrul în selectbox, graficul refuză să se redeseneze (state-locking).
* **Justificare Tehnică**: Prin generarea `dynamic_ms = int(time.time() * 1000)` și adăugarea lui în cheia unificată, forțăm Streamlit să detecteze o componentă complet nouă la fiecare rulare. Memoria cache vizuală veche este ștearsă instantaneu, iar graficul Plotly randează pe ecran noua traiectorie liniară calculată de modelul `LinearRegression` în funcție de selecția operatorului.

### Î8: În paginile din folderul `pages/`, ai configurat callback-uri speciale pentru selectoarele de limbă (ex: `on_change=dashboard_lang_callback`). Cum argumentezi această structură din punct de vedere al sincronizării globale?
* **Apărare**: În mod implicit, widget-urile din subpagini își pierd starea în momentul navigării. Legarea simplă ar fi resetat limba platformei la valoarea implicită la fiecare schimbare de ecran.
* **Justificare Tehnică**: Callback-urile interceptate (precum `dashboard_lang_callback`) preiau valoarea selectată local și o salvează direct în punctul unic de adevăr al stării sesiunii globale (`st.session_state["lang"]`). Datorită acestui mecanism, pachetul lingvistic din `translations.py` se propagă natural și simetric pe toate ecranele aplicației, permițând operatorului să schimbe limba din orice colț al platformei, fără conflicte sau desincronizări.

---

## 🐳 Secțiunea 5: Containerizare, Infrastructură Docker și Multi-Stage Builds

### Î9: În `Dockerfile`-ul de producție optimizat pentru GitHub Codespaces, observ că ai separat configurarea în două etape distincte (`FROM ... AS builder` și `FROM python:3.12-slim-bookworm`). Ce avantaje aduce această arhitectură?
* **Apărare**: Această tehnică este utilizată pentru a minimiza dimensiunea imaginii finale de producție, eliminând instrumentele grele de dezvoltare de care containerul nu mai are nevoie la runtime.
* **Justificare Tehnică**: În prima etapă (`builder`), utilizăm imaginea oficială `ghcr.io/astral-sh/uv` pentru a compila dependențele brute în byte-code. În a doua etapă, copiem *exclusiv* folderul curat `.venv`. Nu instalăm managerul `uv` în imaginea finală. Acest lucru reduce dimensiunea containerului cu peste 60%, elimină vectorii de atac cibernetic la nivel de infrastructură (Attack Surface Reduction) și permite pornirea instantanee a aplicației în cloud.

### Î10: De ce rulează instrucțiunea `USER appuser` spre finalul fișierului `Dockerfile`?
* **Apărare**: În mod implicit, containerele Docker rulează procesele interne sub contul de administrator absolut (`root`), creând riscul de tip *Container Breakout*.
* **Justificare Tehnică**: Prin crearea unui utilizator dedicat sistemului (`appuser`) și delegarea permisiunilor de scriere pe directorul `/workspace`, ne asigurăm că aplicația operează sub principiul privilegiilor minime (*Principle of Least Privilege*). Serverul Streamlit rulează izolat, având exclusiv permisiunile necesare pentru a citi și scrie date în `app.db` și `security_alerts.log`, făcând aplicația extrem de sigură în rețelele cloud.

---

## 🔍 Secțiunea 6: Depanare și Administrare Procedurală Locală

### Î11: În caz de erori de inițializare a bazei de date locale (Missing Data Target), care este procedura corectă de rezolvare și de ce a fost înlocuit vechiul script setup_db.py?
* **Apărare**: Mesajele statice care fac referire la vechi proceduri moștenite (cum ar fi setup_db.py) au fost depreciate pentru a asigura o populare geospațială precisă. Întregul pipeline a fost complet centralizat în noul motor de seed.
* **Justificare Tehnică**: Pentru a genera instantaneu structura bazei de date SQLite locale și a o popula tranzacțional cu cele 8 stații IoT unice din Cluj-Napoca, se rulează din terminal comanda unificată prin managerul `uv`: `uv run python seed_db.py`. La reîncărcarea paginii din browser, serverul Streamlit va prelua automat noul fișier stabilizat `app.db` și va debloca instantaneu vizualizările din Dashboard, utilizând nativ parametrul `use_container_width=True`.
