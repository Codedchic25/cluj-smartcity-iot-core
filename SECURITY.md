# 🛡️ Politica de Securitate și Ghidul de Hardening: Smart City Cluj IoT

Acest document detaliază straturile defensive implementate în platformă pentru a proteja integritatea datelor IoT din Cluj-Napoca și a bloca atacurile cibernetice la nivel de API.

---

## 1. Straturi Defensive și Modelul Defense-in-Depth

Platforma aplică o arhitectură de securitate pe mai multe niveluri locale:

```text
  Date Senzori (Brut SQLite)
         │
         ▼
[Izolare prin Interfață Locală] ──► Scriptul Python preia datele securizat și elimină state-locking
         │
         ▼
[Sintaxă de Prompt Structurată] ──► Izolează datele în interiorul tag-urilor de bloc imutabile
         │
         ▼
[Injecție Context-Aware de Audit] ──► Încarcă ultimele 5 linii din security_alerts.log în LLM
         │
         ▼
[Validare Substring (Promptfoo)] ──► Evaluează comportamentul imun al răspunsului Groq API
```

## 2. Managementul Acreditărilor și Secretelor Urbane
- **Izolarea Cheilor Private**: Toate credențialele sensibile (`GROQ_API_KEY`) sunt complet extrase din codul sursă și stocate exclusiv în fișierul securizat local `.env`.
- **Prevenirea Scurgerilor în Producție**: Fișierul `.env` este introdus explicit în `.gitignore` și `.dockerignore`. Nicio cheie de producție sau certificat nu ajunge în sistemul public de control al versiunilor (GitHub).
- **Securitatea Containerului la Runtime**: Conform specificațiilor de producție din `Dockerfile`, aplicația blokează utilizarea permisiunilor de tip `root` în sandbox, delegând execuția serverului Streamlit către utilizatorul izolat `appuser`, eliminând riscurile de tip Container Breakout.

## 3. Raportarea Vulnerabilităților
Dacă identificați o breșă de securitate în logica de evaluare a datelor sau în expunerea porturilor, vă rugăm **să nu deschideți un Issue public**. Trimiteți un raport detaliat echipei de securitate tehnică la adresa de e-mail dedicată portofoliului personal.

## 4. Protecția împotriva Atacurilor de tip Path Traversal pe Fișierul de Loguri
- **Întrebare de Arhitectură**: Deoarece jurnalul de audit `security_alerts.log` este citit dinamic și afișat în timp real pe interfața dashboard-ului, cum este protejat sistemul împotriva unui atac prin care o componentă malițioasă ar încerca să citească alte fișiere de pe server (ex: `/etc/passwd`)?
- **Barieră implementată**: Calea către fișierul de jurnalizare este definită în mod absolut imutabil la nivel de modul prin structura nativă `Path("security_alerts.log").resolve()`. Codul din `main.py` nu acceptă parametri sau argumente din exterior (din query string sau input-uri text ale utilizatorului) pentru a schimba locația descriptorului de fișier. Funcția execută o citire nativă directă pe calea pre-alocată pe disc, blocând la nivel de compilare orice tentativă de injectare a caracterelor de salt directoare (de tip `../`), securizând total afișarea datelor în UI.
