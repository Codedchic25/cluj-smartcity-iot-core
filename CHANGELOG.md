# 📝 Jurnal de Modificări: Smart City Cluj IoT

Toate modificările notabile aduse acestui proiect sunt documentate în acest fișier. Acest depozit respectă standardele de Versiune Semantică (`MAJOR.MINOR.PATCH`).

---

## [v2.3.0] — 2026-08-25

### ✨ Adăugat
- **Asistent AI Context-Aware cu Ingestie de Loguri:** S-a dezvoltat un mecanism avansat de citire automată a jurnalului local `security_alerts.log` (ultimele 5 linii) și injectarea lor în promptul LLM, oferind asistentului memorie temporală recentă.
- **Provider Python Local pentru Promptfoo:** S-a implementat o arhitectură de testare izolată prin script local (`groq_provider.py:call_api`) rulând pe modelul de mare viteză cu identificatorul de sistem `Qwen 3.6-27B`.
- **Sistem Robust de Citire a Secretelor:** S-a dezvoltat un parser de text imun la codificări specifice sistemelor de operare, asigurând încărcarea securizată a variabilelor de mediu din fișierul local `.env`.
- **Automatizare și Formatare cu Ruff & UV:** Întregul proiect a fost aliniat la standardele PEP 8 și regulile moderne de clean code prin utilizarea linterului ultra-rapid `ruff` orchestrat nativ prin managerul de pachete `uv`.

### 🐛 Corectat
- **Eliminarea Completă a Dependențelor Cloud (Twilio):** S-au eliminat toate importurile, funcțiile reziduale și referințele către Twilio SMS, migrând întregul sistem de alertare către jurnalizarea nativă și izolată local pe disc cu o barieră de cooldown de 10 secunde.
- **Aserțiuni Substring în Promptfoo (100% Pass Rate):** S-au optimizat aserțiunile din `promptfooconfig.yaml` utilizând tipul explicit `substring` pentru a elimina dependențele OpenAI, deblocând testele la un scor perfect de **100% succes (8/8 cazuri trecute)**.
- **Aliniere Componente Vizuale Streamlit:** S-a securizat randarea tabelelor de date istorice și a graficelor interactive Plotly prin formatarea lor nativă cu parametrul stabil `use_container_width=True` pe toate paginile active (`Dashboard`, `Settings`, `Analytics`).
- **Formular Administrativ Extins la 5 Praguri:** S-a corectat tab-ul de configurare adăugând slidere interactive pentru toți cei 5 metrici urbani ai platformei, cu salvare automată în tabela SQLite `settings`.

---

## [v2.1.0] — 2026-05-12

### ✨ Adăugat
- **Senzor IoT pentru Umiditate Sol:** Extinderea pipeline-ului IoT prin introducerea telemetriei de sol pentru Parcul Central, facilitând optimizarea ecologică a sistemelor municipale de irigații.
- **Interfață Tematică Navy (UI/UX Rebuild):** Reconfigurarea completă a stilului vizual în Streamlit prin injectare CSS, migrând de la accentele roșii stridente la o temă Navy profesională, optimizată pentru reducerea oboselii operatorilor civici.
