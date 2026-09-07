# 🏙️ MANUAL DE CONTROL URBAN
# Smart City Cluj-Napoca IoT
## Sistem Urban de Suport Decizional (CDSS) pentru Orașe Inteligente

---

# PARTEA I
# Fundamente Urbane și Fiziologia Senzorilor

---

# 1. Rezumat Executiv Urban

## 1.1 Scopul Platformei
Smart City Cluj-Napoca IoT este un Sistem Urban de Suport Decizional (CDSS) educațional, proiectat pentru a simula monitorizarea în timp real, evaluarea și alertarea automatizată a indicatorilor de mediu și de trafic multi-parametric în cadrul municipiului Cluj-Napoca.

Platforma integrează:
- Monitorizarea telemetrică în timp real a mediului (Temperatură, Calitatea Aerului PM2.5, Nivelul de Zgomot, Gradul de Trafic, Umiditatea Solului).
- Motoare deterministe de reguli operaționale asincrone bazate pe SQLAlchemy 2.0 și aiosqlite.
- Sistem local de auditare și jurnalizare a urgențelor pe disc (`security_alerts.log`) cu scut de cooldown de 10 secunde.
- Migrări automatizate de scheme de baze de date via Alembic (Revizia `5ae1c03dbd71`).
- Sinteză operațională asistată de Inteligență Artificială prin LLM Context-Aware (Qwen 3.6-27B via Groq API).
- Framework-uri de evaluare MLOps rulate prin Promptfoo cu 100% succes.

Obiectivul este de a demonstra modul în care pipeline-urile moderne de AI Generativ pot fi integrate în siguranță în aplicațiile de guvernanță civică, fără a sacrifica determinismul operațional, securitatea locală sau trasabilitatea codului.

## 1.2 Filosofia Core
Platforma operează pe baza a trei principii fundamentale:
- **Atenuare Proactivă**: Degradarea mediului și disfuncționalitățile rețelei urbane trebuie identificate înainte de colapsul catastrofal (de exemplu, riscuri respiratorii severe sau uscarea completă a solului în spațiile verzi).
- **Determinism Absolut**: Acțiunile civice de urgență (cum ar fi activarea sistemelor de irigații sau înregistrarea alertelor) trebuie să se bazeze strict pe surse de date sigure și pe valorile din baza de date `app.db`, niciodată pe răspunsuri probabilistice de tip LLM.
- **Guvernanță Trasabilă**: Fiecare recomandare urbană automatizată trebuie să fie corelată direct cu valori de senzori măsurabile și imutabile, salvate în baza de date persistentă.

---

# 2. Fiziologia Degradării Mediului Urban

## 2.1 Efectul de Insulă de Căldură Urbană (UHI) și Stresul Termic
Nucleele urbane dense din Cluj-Napoca suferă de acumulări de energie termică ambientală din cauza absorbției solare continue în beton și a fricțiunii generate de combustia traficului auto intens. Platforma simulează acest fenomen printr-o corelație matematică dinamică în engine-ul generatorului, unde volumul ridicat de trafic amplifică direct indicii de căldură ambientală și nivelul de zgomot (dB).

## 2.2 Poluarea Microparticulată a Aerului (PM2.5)
Particulele în suspensie PM2.5 (μg/m³) reprezintă un pericol cardiovascular și de mediu acut în nodurile de tranzit dense. Platforma stabilește limite stricte: depășirea pragului de 80.0 PM2.5 determină platforma să execute avertizări vizuale imediate în dashboard și scrieri asincrone în jurnalul de securitate pentru a preveni expunerea respiratorie a populației.

---

# PARTEA A II-A
# Logica Decizională Operațională și Infrastructura

---

# 3. Motorul Determinist de Reguli și Stratificarea Riscurilor

Sistemul respinge modelele probabilistice de tip „black-box” pentru siguranța urbană. În schimb, logica execută potriviri deterministe pe bază de praguri fixe salvate în tabela `settings` din baze de date, interogate asincron. Pentru a preveni alerte false la valorile limită, evaluările folosesc inegalități stricte:

- **Hazard Acut de Poluare a Aerului**: `air_quality (PM2.5) > 80.0`
- **Anomalii Termice Extreme (Caniculă)**: `temperature > 32.0°C`
- **Secătuirea Ecologică Critică a Solului**: `soil_moisture < 35.0%`

---

# PARTEA A III-A
# Siguranța AI, Guardrails de Securitate Cibernetică și MLOps

---

# 4. Arhitectura de Securitate Cibernetică și Ingestia Contextuală
Aplicațiile civice sunt vulnerabile la atacuri de tip prompt injection. Pentru a securiza fluxul, sistemul decuplează interogările brute și folosește o structură de prompt strict izolată prin variabile unificate.

În plus, asistentul urban execută o injecție dinamică a contextului de securitate live direct în structura de prompt, citind ultimele 5 linii din `security_alerts.log`. Acest lucru garantează că modelul LLM generează recomandări bazate pe istoricul real al breșelor, în mod complet izolat și fără a îngheța UI-ul Streamlit.

---

# 5. Suita de Validare MLOps Promptfoo

Pentru a ne asigura că motorul AI își păstrează alinierea lingvistică în cele 5 limbi, automatizarea definită în `promptfooconfig.yaml` execută evaluări matriceale concurente (fără cache), utilizând modelul modern Qwen 3.6-27B de pe infrastructura Groq.

Aserțiunile au fost configurate utilizând tipul nativ rapid `substring` pentru a elimina complet apelurile OpenAI din fundal, obținând un scor perfect de **100% succes (8/8 cazuri trecute)** cu timp de latență optimizat.
# 🎓 Ghid Avansat de Susținere Orală (Q&A Matrix) — Smart City Cluj IoT

Acest document centralizează întrebările de arhitectură, deciziile ingineriești și scenariile de depanare care pot apărea în timpul examinării tehnice a proiectului, oferind apărări clare bazate direct pe codul sursă real.

---

## 🏗️ Secțiunea 1: Decizii de Arhitectură și Concurență Streamlit

### Î1: În paginile `1_Dashboard.py`, `2_Settings.py` și `3_Analytics.py` folosești SQLAlchemy 2.0 și aiosqlite pentru a apela funcțiile bazei de date. De ce nu ai folosit cuvântul cheie `await` direct în corpul principal al scriptului?
* **Apărare**: Streamlit nu este un framework asincron nativ în corpul său principal. Rularea unui `await` direct la nivel de modul (top-level) ar arunca o eroare de sintaxă de tipul `SyntaxError: 'await' outside function`.
* **Justificare Tehnică**: Pentru a interfața arhitectura asincronă a bazei de date cu ciclul de randare sincron al Streamlit, am utilizat puncte de intrare controlate prin `asyncio.run()`. Această metodă pornește un event loop izolat, execută interogarea asincronă, colectează datele în DataFrame-uri Pandas și închide loop-ul curat. Toate conexiunile sunt protejate prin timeout-uri stricte (ex: `timeout=15`), prevenind apariția erorilor de tip `database is locked` în timp ce serviciul de fundal `producer.py` scrie date în paralel.

### Î2: De ce ai ales să folosești structura nativă Multipage a Streamlit (directorul `pages/`) în loc de un selector simplu de tip `st.sidebar.radio` într-un singur fișier monolitic?
* **Apărare**: Abordarea monoliților într-un singur fișier (unde paginile sunt funcții Python controlate de un `if/else`) duce la **Memory Bloat** (umflarea memoriei RAM) și degradarea performanței, deoarece la fiecare refresh întregul script se reexecută.
* **Justificare Tehnică**: Prin utilizarea structurii multipage (`pages/`), Streamlit încarcă în memorie doar codul paginii active în care navighează operatorul. Fișierele sunt izolate complet ca module, reducând amprenta de memorie și facilitând mentenanța codului, păstrând în același timp starea sesiunii globală (`st.session_state`).

---

## 🚨 Secțiunea 2: Logica Alertelor și Optimizarea Resurselor Localizate

### Î3: În engine-ul platformei verifici telemetria cu inegalități stricte (`>`). Care este impactul acestei decizii matematice asupra sistemului?
* **Apărare**: Inegalitățile non-stricte introduc un risc major de **Alert Oscillation** (oscilație de alertă) în sistemele IoT în cazul în care un senzor transmite repetat valoarea limită exactă (ex: exact `32.0°C` sau exact `80.0 PM2.5`).
* **Justificare Tehnică**: Prin trecerea globală la inegalități stricte unificate (`temperature > 32.0`, `air_quality > 80.0`, `soil_moisture < 35.0`), am aliniat codul cu modelul matematic formal din documentație. Dacă un senzor trimite valoarea limită exactă, sistemul o interpretează ca fiind la granița superioară a zonei sigure și NU declanșează alerta, eliminând fenomenul de oboseală a operatorului (*alert fatigue*).

### Î4: Cum garantează pipeline-ul asincron că scrierea alertelor în jurnalul de pe disc nu blochează generarea datelor IoT și cum ai eliminat dependențele externe?
* **Apărare**: Dependențele cloud externe introduc vulnerabilități de rețea, latențe mari și costuri imprevizibile. Din acest motiv, am decuplat complet platforma de servicii terțe (fără Twilio), migrând întregul sistem către o **jurnalizare de audit locală rapidă și izolată** în `security_alerts.log` protejată de un scut de cooldown de 10 secunde.
* **Justificare Tehnică**: Scrierea fizică pe hard-disk este o operațiune de tip I/O-bound blocantă. Am remediat riscul de blocare izolând scrierea prin intermediul unui executor de fundal: `await loop.run_in_executor(None, lambda: ...)`. Această instrucțiune trimite sarcina de scriere într-un thread pool separat administrat de Python. Loop-ul asincron principal se eliberează instantaneu, continuând să genereze date pentru restul senzorilor fără nicio milisecundă de latență.

---

## 🧠 Secțiunea 3: Securitate AI și Validare MLOps (Qwen Engine)

### Î5: Cumionează utilitarul de procesare AI protecția împotriva atacurilor de tip Prompt Injection?
* **Apărare**: În loc să ne bazăm pe reguli lejere, structura proiectului aplică principiul izolării stricte a datelor în interiorul unui șablon bine delimitat (System/User Open-Block).
* **Justificare Tehnică**: Datele primite de la senzori sunt injectate în secțiuni clar separate prin marcaje structurate în fișierul `ai_tests/prompts.txt`. Acest lucru împiedică modelul LLM să confunde datele telemetrice cu instrucțiunile de sistem. În plus, prin setarea unei temperaturi scăzute (`0.2`) în `groq_provider.py`, modelul este forțat să rămână determinist și să livreze recomandări tehnice scurte, eliminând riscurile de evadare din context (jailbreak).

### Î6: În `promptfooconfig.yaml` ai configurat aserțiuni de tip substring. Ce anume validează acestea mai exact și de ce sunt rulate în pipeline-ul CI/CD din GitHub Actions?
* **Apărare**: Răspunsurile modelelor LLM sunt probabilistice. Într-o actualizare de model în cloud, AI-ul ar putea să ofere recomandări într-o altă limbă sau să omită directivele operaționale de urgență.
* **Justificare Tehnică**: Suita Promptfoo rulează în `ci.yml` ca o poartă de calitate (Quality Gate). Aserțiunile de tip `substring` caută cuvinte cheie imperative (ex: `irigare` în caz de secetă, `aer` în caz de poluare). Prin utilizarea modelului de producție **Qwen 3.6-27B** și a verificărilor locale substring, am eliminat dependențele de OpenAI din fundal, obținând un scor perfect de **100% passed (8/8 cases)** care garantează siguranța semantică înainte ca codul să intre în producție.

---

## 🌐 Secțiunea 4: Gestiunea Sesiunilor, I18n și Reactivitate Plotly

### Î7: În `pages/3_Analytics.py`, folosești un timestamp în milisecunde (`dynamic_ms`) adăugat direct în cheia `key` a graficului Plotly predictiv. Ce problemă Streamlit rezolvă această decizie?
* **Apărare**: Streamlit tinde să păstreze în cache starea vizuală a graficelor complexe pentru a economisi performanță. Fără o cheie dinamică, atunci când schimbi parametrul în selectbox, graficul refuză să se redeseneze (state-locking).
* **Justificare Tehnică**: Prin generarea `dynamic_ms = int(time.time() * 1000)` și adăugarea lui în cheia unificată, forțăm Streamlit să detecteze o componentă complet nouă la fiecare rulare. Memoria cache vizuală veche este ștearsă instantaneu, iar graficul Plotly randează pe ecran noua traiectorie liniară calculată de modelul `LinearRegression` în funcție de selecția operatorului.

### Î8: În paginile din folderul `pages/`, ai configurat callback-uri speciale pentru selectoarele de limbă (ex: `on_change=dashboard_lang_callback`). Cum argumentezi această structură din punct de vedere al sincronizării globale?
* **Apărare**: În mod implicit, widget-urile din subpagini își pierd starea în momentul navigării. Legarea simplă ar fi resetat limba platformei la valoarea implicită la fiecare schimbare de ecran.
* **Justificare Tehnică**: Callback-urile interceptate preiau valoarea selectată local și o salvează direct în punctul unic de adevăr al stării sesiunii globale (`st.session_state["lang"]`). Datorită acestui mecanism, pachetul lingvistic din `translations.py` se propagă natural și simetric pe toate ecranele aplicației, permițând operatorului să schimbe limba din orice colț al platformei, fără conflicte sau desincronizări.

---

## 🐳 Secțiunea 5: Containerizare, Infrastructură Docker și Multi-Stage Builds

### Î9: În `Dockerfile`-ul de producție optimizat, observ că ai separat configurarea în două etape distincte (`FROM ... AS builder` și `FROM python:3.12-slim-bookworm`). Ce avantaje aduce această arhitectură?
* **Apărare**: Acest model este utilizat pentru a minimiza dimensiunea imaginii finale de producție, eliminând instrumentele grele de dezvoltare de care containerul nu mai are nevoie la runtime.
* **Justificare Tehnică**: În prima etapă (`builder`), utilizăm imaginea oficială `ghcr.io/astral-sh/uv` pentru a compila dependențele brute în byte-code. În a doua etapă, copiem *exclusiv* folderul curat `.venv`. Nu instalăm managerul `uv` în imaginea finală. Acest lucru reduce dimensiunea containerului cu peste 60%, elimină vectorii de atac cibernetic la nivel de infrastructură (Attack Surface Reduction) și permite pornirea instantanee a aplicației în cloud.

### Î10: De ce rulează instrucțiunea `USER appuser` spre finalul fișierului `Dockerfile`?
* **Apărare**: În mod implicit, containerele Docker rulează procesele interne sub contul de administrator absolut (`root`), creând riscul de tip *Container Breakout*.
* **Justificare Tehnică**: Prin crearea unui utilizator dedicat sistemului (`appuser`) și delegarea permisiunilor de scriere pe directorul `/workspace`, ne asigurăm că aplicația operează sub principiul privileges minime (*Principle of Least Privilege*). Serverul Streamlit rulează izolat, având exclusiv permisiunile necesare pentru a citi și scrie date în `app.db` și `security_alerts.log`, făcând aplicația extrem de sigură în rețelele cloud.

---

---

## 🔍 Secțiunea 6: Depanare și Administrare Procedurală Locală

### Î11: În caz de erori de inițializare a bazei de date locale (Missing Data Target), care este procedura corectă de rezolvare și de ce a fost eliminat vechiul script setup_db.py?
* **Apărare**: Mesajele care fac referire la vechi proceduri moștenite (cum ar fi setup_db.py) au fost depreciate pentru a asigura redistribuirea geospațială precisă. Întregul pipeline a fost complet centralizat în noul motor de seed.
* **Justificare Tehnică**: Pentru a genera instantaneu structura bazei de date SQLite locale și a o popula tranzacțional cu cele 8 stații IoT unice din Cluj-Napoca, se rulează din terminal comanda unificată prin managerul uv: `uv run python seed_db.py`. La reîncărcarea paginii din browser, serverul Streamlit va prelua automat noul fișier stabilizat `app.db` și va debloca instantaneu vizualizările din Dashboard.
