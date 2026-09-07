# ❓ Întrebări Frecvente Tehnice și Operaționale: Smart City Cluj IoT

Acest document răspunde la cele mai frecvente întrebări de arhitectură, securitate și management al datelor din cadrul platformei de control urban.

---

### Î1: De ce continuă graficele din panoul Streamlit să se updateze fluid, iar terminalul a scăpat de avertismentele legate de layout?
* **Răspuns**: În versiunile anterioare de Streamlit, anumite proprietăți de layout puteau genera avertismente de depreciere. Am înlocuit global acele sintaxe cu parametrul modern, nativ și stabil `use_container_width=True` în toate paginile active (`Dashboard`, `Settings`, `Analytics`), asigurând o scalare perfectă a tabelelor și a graficelor interactive Plotly indiferent de rezoluția ecranului.

### Î2: Cum asigură simulatorul izolarea datelor și rularea 100% offline în medii containerizate precum GitHub Codespaces?
* **Răspuns**: Platforma implementează o inițializare defensivă a stării globale, eliminând complet dependențele de rețea sau API-uri cloud externe pentru partea de stocare și alertare. Sistemul interoghează sincron baza de date centrală `app.db` locală, ocolind blocajele de rețea. Toate erorile de tip `KeyError` la navigarea inter-pagini sunt neutralizate, asigurând o încărcare fluidă a contextului pe orice sistem de operare.

### Î3: Ce se întâmplă cu monitorizarea orașului dacă conexiunea externă către cloud-ul LLM (Groq) suferă o întrerupere sau o eroare de rețea?
* **Răspuns**: Sistemul implementează un framework de **Determinism Local și Fail-Safe**. Toate apelurile API către modelele de analiză sunt încapsulate în blocuri robuste de tip `try/except` în interiorul codului de infrastructură AI. Dacă rețeaua pică, sistemul interceptează eroarea, o loghează în siguranță în consolă și servește un mesaj informativ controlat în interfață, fără a bloca rularea restului platformei. Scrierea datelor de la senzorii IoT în SQLite, generarea graficelor live Plotly, actualizarea bazei de date și scrierea alertelor în `security_alerts.log` continuă să funcționeze 100% neîntrerupt.

### Î4: Cum asigură sistemul context-aware o recomandare AI superioară fără a supraîncărca fereastra de context a modelului?
* **Răspuns**: În loc să trimitem asistentului tot istoricul masiv de date, funcția dedicată de colectare a contextului execută o citire securizată la nivel de byte-stream și extrage strict ultimele 5 linii din fișierul fizic `security_alerts.log`. Acest extras compact este injectat dinamic în promptul central. Modelul de producție **Qwen 3.6-27B** primește astfel un istoric temporal recent și dens, generând decizii de triaj de mare finețe în maximum 3 fraze, optimizând costurile de API și respectând limitele de token-uri.

### Î5: Cum protejează aplicația datele de sesiune ale operatorului (`st.session_state`) împotriva atacurilor de tip Session Cross-Talk într-un mediu cloud multi-utilizator?
* **Răspuns**: Framework-ul Streamlit rulează o instanță complet izolată a contextului de execuție pentru fiecare tab de browser deschis de un utilizator nou. Toate variabilele salvate în `st.session_state` (cum ar fi flag-ul `authenticated`, selecția de limbă din `main_lang_widget` sau istoricul de răspunsuri generate de modelul **Qwen 3.6-27B**) sunt stocate într-un container de memorie dedicat exclusiv acelui fir de execuție (thread-isolated memory). Nu există absolut niciun risc ca un operator conectat în cloud să poată vizualiza alertele sau starea de autentificare a unui alt operator, garantând confidențialitatea și securitatea datele la nivel de sesiune individuală.
