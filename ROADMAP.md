# 🗺️ Plan de Dezvoltare Tehnică (Roadmap): Smart City Cluj IoT

Acest document schițează fazele de evoluție arhitecturală pentru platforma de control urban din Cluj-Napoca, migrând de la un prototip educațional monolitic către un ecosistem microservicii distribuit.

---

## 📅 Faza 1: Decuplare și Servicii API (Q3 2026) — *În Curs*
- **Migrare către FastAPI**: Separarea completă a logicii de business din prezentarea Streamlit prin construirea unui backend asincron în FastAPI cu endpoint-uri REST protejate, utilizând dependințele declarate gestionate prin `uv`.
- **PostgreSQL în Producție**: Înlocuirea bazei de date ușoare SQLite (`app.db`) cu o instanță PostgreSQL clusterizată, optimizată pentru interogări masive concurente și indexare geografică prin extensia `PostGIS`.
- **Gestiune Autentificare (RBAC real)**: Extinderea modulului nativ `streamlit-authenticator` prin integrarea unui sistem de autentificare securizat bazat pe token-uri JWT (`pyjwt`), mapând riguros rolurile operaționale ale dispeceratului urban.

## 📅 Faza 2: Edge Computing și Securitate Avansată (Q4 2026)
- **Integrare Broker MQTT**: Înlocuirea pipeline-ului simulat dintr-un script intern cu un broker real MQTT (ex: Eclipse Mosquitto) capabil să preia fluxuri live de date criptate direct de la senzori fizici de teren.
- **Extindere Firewall Semantic**: Integrarea unei librării specializate sau a unui cadru avansat de siguranță (precum `NeMo Guardrails`) poziționat la nivelul modelului **Qwen 3.6-27B** și al clientului Groq API, pentru a bloca încercările complexe de evadare din context sau manipulare semantică a asistentului urban.

## 📅 Faza 3: Scalabilitate și MLOps Automatizat (Q1 2027)
- **Orchestrare Docker & Kubernetes**: Containerizarea completă a microserviciilor prin optimizarea instrucțiunilor din `Dockerfile` și orchestrarea lor prin Kubernetes pentru a asigura disponibilitate continuă (High Availability) și scalare automatizată în funcție de încărcarea rețelei de senzori.
- **Pipeline de Re-antrenare Predictivă**: Automatizarea pipeline-ului Scikit-Learn pentru a re-antrena modelele de Regresie Liniară (`LinearRegression`) în fiecare noapte cu noile seturi de date colectate din cartierele Clujului, integrând suport pentru modele avansate prin bibliotecile `statsmodels` și `prophet`.
## 📅 Faza 4: Monitorizare Distribuită și Sincronizare Multi-Regiune (Q2 2027)
- **Întrebare de Arhitectură**: Când platforma va migra către PostgreSQL/PostGIS și FastAPI într-o infrastructură multi-regiune, cum va fi gestionat jurnalul de audit local `security_alerts.log` pentru a preveni pierderea consistenței datelor?
- **Apărare și Direcție**: Jurnalizarea simplă pe fișier local va fi înlocuită de un serviciu centralizat de colectare a logurilor (de tip Vector sau FluentBit). Logurile vor fi transmise asincron către un cluster Elasticsearch/Grafana Loki dedicat, păstrând în același timp un fallback local tampon (buffer format din fișiere rotative de 5MB) pe fiecare nod de calcul. Acest lucru va asigura că barierele de securitate și regulile de audit rămân imune la întreruperile temporare ale rețelei de cloud.
