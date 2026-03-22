# Pokemon Tournament — Manuale Completo del Codice

> Guida dettagliata per comprendere ogni componente del gioco.
> **Linguaggio:** Python 3.12+ | **Framework grafico:** Pygame 2.5 | **Pokemon disponibili:** 809

---

## Indice

1. [Panoramica del Gioco](#1-panoramica-del-gioco)
2. [Struttura dei File](#2-struttura-dei-file)
3. [Costanti e Configurazione](#3-costanti-e-configurazione)
4. [Sistema di Comunicazione tra Thread](#4-sistema-di-comunicazione-tra-thread)
5. [main.py — Punto d'ingresso](#5-mainpy--punto-dingresso)
6. [dati.py — Caricamento Dati](#6-datipy--caricamento-dati)
7. [pokemon.py — Stato di Battaglia](#7-pokemonpy--stato-di-battaglia)
8. [danno.py — Calcolo Danni e Cura](#8-dannopy--calcolo-danni-e-cura)
9. [ai.py — Intelligenza Artificiale](#9-aipy--intelligenza-artificiale)
10. [torneo.py — Gestione del Torneo](#10-torneopy--gestione-del-torneo)
11. [battaglia.py — Motore di Battaglia](#11-battagliapy--motore-di-battaglia)
12. [finestra_tk.py — Grafica Pygame](#12-finestra_tkpy--grafica-pygame)
13. [Sistema Temi Giorno/Notte](#13-sistema-temi-giornonotte)
14. [Sistema di Animazioni](#14-sistema-di-animazioni)
15. [Schermate del Gioco](#15-schermate-del-gioco)
16. [Aggiungere Contenuti](#16-aggiungere-contenuti)
17. [Appendice — Riferimento Rapido](#17-appendice--riferimento-rapido)

---

## 1. Panoramica del Gioco

Pokemon Tournament è un gioco a turni per un giocatore contro la CPU. Il giocatore sceglie un Pokemon e partecipa a un torneo a eliminazione diretta con altri 15 Pokemon (selezionati in base alla difficoltà). Ogni scontro è un combattimento 1vs1 con mosse simultanee.

### Flusso di gioco

| Fase | Descrizione |
|------|-------------|
| Avvio | `main.py` lancia due thread: logica (`battaglia.py`/`torneo.py`) e grafica (`finestra_tk.py` via Pygame) |
| Difficoltà | Il giocatore sceglie Facile / Media / Difficile — determina il pool di avversari |
| Selezione | Sceglie il proprio Pokemon da una griglia di 809 disponibili |
| Tabellone | Il torneo viene generato con 16 Pokemon (il giocatore + 15 CPU), bracket casuale |
| Battaglia | Ad ogni round il giocatore sceglie una mossa; la CPU sceglie in base alla difficoltà |
| Round | Le mosse vengono eseguite simultaneamente; chi arriva a 0 HP perde |
| Avanzamento | Dopo ogni battaglia compare il tabellone aggiornato, poi si passa al round successivo |
| Campione | Se il giocatore vince tutti e 4 i round (ottavi, quarti, semifinale, finale) vince il torneo |

### Mosse disponibili in battaglia

| Mossa | Effetto |
|-------|---------|
| Attacco | Usa la statistica ATK del Pokemon. Danno fisico diretto. |
| Attacco Speciale | Usa la statistica SpA. Può avere moltiplicatore di tipo (×0, ×0.5, ×1, ×2). |
| Pozione Normale | Ripristina il 100% degli HP. L'eccesso va in DEF/SpD. Limitata per round. |
| Pozione Speciale | Come la pozione normale ma conta separatamente. Limitata per round. |

> **Nota:** Le mosse sono **SIMULTANEE**: entrambi i combattenti scelgono nello stesso turno. Se uno attacca e l'altro si cura, la cura avviene prima. In caso di doppio KO, perde il Pokemon più lento.

---

## 2. Struttura dei File

| File / Cartella | Ruolo |
|-----------------|-------|
| `main.py` | Punto d'ingresso. Crea i thread logica e grafica, li collega tramite due Queue. |
| `finestra_tk.py` | Tutta la grafica (Pygame). Gestisce eventi mouse, disegno, animazioni, temi. ~1350 righe. |
| `battaglia.py` | Motore di combattimento. Gestisce turni, mosse simultanee, pozioni, KO. |
| `torneo.py` | Genera e gestisce il bracket a eliminazione. Avanza round, determina il campione. |
| `ai.py` | Logica decisionale della CPU in base alla difficoltà (facile/media/difficile). |
| `danno.py` | Calcola i danni fisici e speciali, cura, moltiplicatori di tipo. |
| `pokemon.py` | Classe che rappresenta lo stato di un Pokemon durante la battaglia (HP, difesa attuale...). |
| `dati.py` | Carica `pokedex.json` e `types.json`. Fornisce la lista di tutti i Pokemon. |
| `PokemonGame/pokedex.json` | Database con statistiche e tipi di 809 Pokemon. |
| `PokemonGame/types.json` | Matrice di efficacia dei tipi (es. Fuoco vs Acqua = 0.5×). |
| `PokemonGame/pokemon_images/` | Immagini PNG dei Pokemon (`nome.png` o `nome-forma.png`). |
| `PokemonGame/style/` | Immagini di stile: pannelli, sole, luna, nuvole, font TTF. |
| `PokemonGame/wallpaper_dark/` | Sfondi per la battaglia in modalità notte. |
| `PokemonGame/wallpaper_light/` | Sfondi per la battaglia in modalità giorno. |

---

## 3. Costanti e Configurazione

Tutte le costanti di layout sono definite all'inizio di `finestra_tk.py` come variabili modulo. Cambiarle qui modifica l'intero gioco.

### Finestra e timing

| Costante | Valore | Significato |
|----------|--------|-------------|
| `W, H` | `1280, 760` | Dimensioni della finestra in pixel |
| `BAR` | `44` | Altezza della barra superiore in pixel |
| `TICK` | `50` | Target FPS — `1000 // TICK = 20` frame al secondo |

### Sprite e posizioni di battaglia

| Costante | Valore | Significato |
|----------|--------|-------------|
| `SPR_SEL` | `36` | Raggio del cerchio sprite nella griglia di selezione |
| `SPR_PAN` | `72` | Raggio del cerchio sprite nel pannello statistiche |
| `SPR_B` | `320` | Dimensione sprite in battaglia (320×320 px) |
| `SPR_OFF` | `0.05` | Offset verticale dello sprite rispetto al centro |
| `SPR_CER_OFF` | `0.25` | Offset verticale dello sprite dentro il cerchio |
| `GX` | `50` | X del giocatore in battaglia |
| `GY` | `80` | Y del giocatore in battaglia |
| `AX` | `W - 370` | X dell'avversario in battaglia |
| `AY` | `140` | Y dell'avversario in battaglia |

### Griglia di selezione Pokemon

| Costante | Valore | Significato |
|----------|--------|-------------|
| `GRIGLIA_CELLA_W` | `200` | Larghezza di ogni cella nella griglia |
| `GRIGLIA_CELLA_H` | `96` | Altezza di ogni cella nella griglia |
| `GRIGLIA_GAP` | `6` | Spazio tra celle (orizzontale e verticale) |
| `GRIGLIA_ORIG_X` | `238` | X dell'angolo in alto a sinistra della griglia |
| `GRIGLIA_ORIG_Y` | `54` | Y dell'angolo in alto a sinistra della griglia (`BAR + 10`) |
| `GRIGLIA_COLONNE` | `5` | Numero di colonne nella griglia |
| `PANNELLO_L_W` | `230` | Larghezza del pannello statistiche a sinistra |

### Log e zona bassa

| Costante | Valore | Significato |
|----------|--------|-------------|
| `LOW` | `282` | Altezza della zona inferiore (log + pulsanti mossa) in pixel |
| `LOG_N` | `14` | Numero di righe di log visibili simultaneamente |

### Tabellone torneo

| Costante | Valore | Significato |
|----------|--------|-------------|
| `BRACKET_TOP` | `BAR + 35` | Y di inizio del tabellone |
| `BRACKET_H` | `H - BAR - 65` | Altezza totale del tabellone |
| `BRACKET_BOX_W` | `155` | Larghezza di ogni box match |
| `BRACKET_BOX_H` | `56` | Altezza di ogni box match |
| `BRACKET_GAP` | `18` | Spazio tra le colonne del bracket |

> Le coordinate X di ogni colonna (`R16_L_X1`, `QF_L_X1`, `SF_L_X1`, `FINAL_X1` e i loro simmetrici a destra) vengono calcolate automaticamente a partire dal centro dello schermo e dal `BRACKET_GAP`, garantendo sempre un layout bilanciato.

---

## 4. Sistema di Comunicazione tra Thread

Il gioco usa due thread separati: uno per la **logica** (battaglia, AI, torneo) e uno per la **grafica** (Pygame). Comunicano tramite due oggetti `queue.Queue` thread-safe.

### Le due code

| Coda | Direzione | Uso |
|------|-----------|-----|
| `coda_comandi` | Logica → Grafica | La logica invia messaggi alla GUI (es: disegna la battaglia, mostra animazione) |
| `coda_risposte` | Grafica → Logica | La GUI invia input dell'utente (es: ha cliccato Attacco, ha scelto Pikachu) |

### Messaggi dalla logica alla grafica (`coda_comandi`)

| Tipo | Descrizione |
|------|-------------|
| `difficolta` | Mostra schermata scelta difficoltà. Passa il pool di Pokemon decorativi. |
| `selezione` | Mostra griglia selezione. Passa pool Pokemon disponibili e difficoltà. |
| `tabellone` | Mostra bracket torneo. Passa i dati del bracket e messaggio eventuale. |
| `battaglia_inizia` | Avvia una battaglia. Passa i dati di giocatore e avversario. |
| `aggiorna` | Aggiorna HP/pozioni visualizzati durante la battaglia. |
| `log` | Aggiunge una riga al log di battaglia con testo e colore. |
| `chiedi_mossa` | Attiva i pulsanti mossa (è il turno del giocatore). |
| `anim_attacco` | Lancia animazione di attacco fisico (scatto, onde, particelle). |
| `anim_attacco_doppio` | Attacco simultaneo di entrambi. |
| `anim_speciale` | Lancia animazione attacco speciale (scia colorata). Passa moltiplicatore. |
| `anim_cura` | Lancia animazione pozione (bolle colorate). Passa tipo pozione. |
| `anim_ko` | Lancia animazione KO (dissolvenza progressiva). |
| `risultato` | Fine battaglia: mostra messaggio e pulsante Continua. |
| `campione` | Fine torneo: mostra schermata campione. |

### Messaggi dalla grafica alla logica (`coda_risposte`)

| Tipo | Descrizione |
|------|-------------|
| `difficolta` | L'utente ha scelto la difficoltà. Valore: `'facile'` / `'media'` / `'difficile'`. |
| `pokemon` | L'utente ha scelto il suo Pokemon. Valore: dizionario con dati Pokemon. |
| `mossa` | L'utente ha scelto una mossa. Valore: `'attacco'` / `'attacco_speciale'` / `'pozione_normale'` / `'pozione_speciale'`. |
| `continua` | L'utente ha cliccato Continua (dopo risultato o tabellone). |
| `indietro` | L'utente ha cliccato Indietro nella selezione Pokemon. |
| `esci` | L'utente ha chiuso la finestra. |

---

## 5. main.py — Punto d'ingresso

`main.py` è il file da eseguire per avviare il gioco. Ha il solo compito di creare i due oggetti principali, collegarli tramite le code e avviare i thread.

```python
dati_gioco = DatiGioco('PokemonGame/pokedex.json', 'PokemonGame/types.json')
# Carica tutti i 809 Pokemon e la matrice dei tipi dal disco

finestra = Finestra('PokemonGame/pokemon_images', 'PokemonGame')
# Crea l'oggetto grafico Pygame con percorsi alle immagini

logica = LogicaGioco(dati_gioco, finestra.coda_comandi, finestra.coda_risposte)
# Crea la logica collegandola alle due code della finestra

thread_logica = threading.Thread(target=logica.avvia, daemon=True)
# Il thread logica è daemon: si ferma quando si chiude la finestra

finestra.avvia(thread_logica)
# Avvia il loop Pygame nel thread principale (richiesto da macOS/Windows)
```

> **Perché due thread?** Pygame richiede di girare nel thread principale. La logica di gioco (AI, calcoli, attese) deve girare in un thread separato per non bloccare il rendering. Le Queue garantiscono che i due thread comunichino in modo sicuro senza race condition.

---

## 6. dati.py — Caricamento Dati

`dati.py` carica al momento dell'avvio il database dei Pokemon e la tabella dei tipi da file JSON.

### Struttura di `pokedex.json`

Ogni Pokemon è un dizionario con questi campi:

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `nome` | `string` | Nome del Pokemon (es: `'Pikachu'`). Usato anche come nome file immagine. |
| `tipi` | `list` | Lista di 1 o 2 tipi (es: `['Electric']` o `['Water', 'Flying']`). |
| `stats` | `dict` | Dizionario con: `hp`, `attack`, `defense`, `sp_attack`, `sp_defense`, `speed`. |

### Struttura di `types.json`

Matrice NxN (18 tipi × 18 tipi) che contiene il moltiplicatore di danno quando un attacco di tipo X colpisce un Pokemon di tipo Y.

Valori possibili: `0` (immune), `0.5` (non molto efficace), `1` (normale), `2` (super efficace).

> **Esempio:** `types['Fire']['Grass'] = 2.0` → il fuoco fa il doppio dei danni all'Erba. Il calcolo finale per un Pokemon dual-type moltiplica entrambi i valori (es: Volante+Ghiaccio vs Fuoco: `1.0 × 0.5 = 0.5×`).

---

## 7. pokemon.py — Stato di Battaglia

La classe `PokemonBattaglia` rappresenta un Pokemon durante uno scontro. Mantiene i valori attuali (HP, difesa) che cambiano nel corso della battaglia, separati dalle statistiche base del Pokedex.

### Attributi principali

| Attributo | Descrizione |
|-----------|-------------|
| `nome` | Nome del Pokemon |
| `tipi` | Lista dei tipi (copiata dal Pokedex) |
| `stats` | Dizionario statistiche base (invariato durante la battaglia) |
| `hp_attuale` | HP correnti. Inizia uguale a `stats['hp']`. Scende quando si riceve danno. |
| `difesa_attuale` | Difesa corrente. Può aumentare con la pozione (eccesso HP → DEF). |
| `sp_difesa_attuale` | Difesa speciale corrente. Funziona come `difesa_attuale`. |
| `pozioni_normali` | Numero di pozioni normali rimaste per questo round. |
| `pozioni_speciali` | Numero di pozioni speciali rimaste per questo round. |

> **Perché separare `hp_attuale` da `stats['hp']`?** `stats['hp']` è il valore massimo base, mai modificato. `hp_attuale` è il valore attuale che scende in battaglia. Questo permette di calcolare percentuali per le barre HP e di sapere quando un Pokemon è KO (`hp_attuale <= 0`).

---

## 8. danno.py — Calcolo Danni e Cura

`danno.py` contiene le formule per calcolare quanti HP vengono tolti o ripristinati in ogni azione.

### Attacco fisico

```python
danno = max(1, attaccante.stats['attack'] - difensore.difesa_attuale)
# Il danno minimo è sempre 1 (non può essere 0 o negativo)
# difesa_attuale può crescere con le pozioni
```

### Attacco speciale

```python
moltiplicatore = calcola_tipo(tipo_attaccante, tipi_difensore, types_data)
# Calcola ×0, ×0.5, ×1 o ×2 in base alla tabella dei tipi

danno = max(0, int(attaccante.stats['sp_attack'] * moltiplicatore
               - difensore.sp_difesa_attuale))
# Se il moltiplicatore è 0 (immune), il danno è esattamente 0
```

### Pozione

```python
cura = difensore.stats['hp']  # Ripristina il 100% degli HP base

hp_prima = difensore.hp_attuale
difensore.hp_attuale = difensore.stats['hp']
eccesso = cura - (difensore.stats['hp'] - hp_prima)

if eccesso > 0:
    # L'HP era già alto: l'eccesso potenzia la difesa
    difensore.difesa_attuale    += eccesso // 2
    difensore.sp_difesa_attuale += eccesso // 2
```

> **Meccanismo dell'eccesso:** Curarsi quando si è quasi integri aumenta DEF e SpD, creando una scelta strategica (curare subito o aspettare di perdere HP?).

---

## 9. ai.py — Intelligenza Artificiale

La CPU sceglie la mossa in base alla difficoltà selezionata dal giocatore.

### Livelli di difficoltà

| Difficoltà | Comportamento CPU |
|------------|-------------------|
| **Facile** | Sceglie una mossa a caso tra quelle disponibili. Pool: i 15 Pokemon con punteggio totale più basso. |
| **Media** | Preferisce l'attacco speciale se il moltiplicatore è favorevole; usa la pozione se gli HP sono sotto il 40%. Pool: 15 Pokemon casuali. |
| **Difficile** | Simula entrambe le mosse possibili e sceglie quella con il miglior risultato atteso. Tiene conto di danni, HP rimanenti e pozioni. Pool: i 15 Pokemon più forti. |

### Selezione del pool avversari

```python
# Calcola un punteggio per ogni Pokemon
punteggio = stats['hp'] + stats['attack'] + stats['sp_attack'] + stats['speed']

# Facile: prende i 15 con punteggio più basso
pool_facile = sorted(tutti, key=punteggio)[:15]

# Media: 15 Pokemon casuali dall'intero Pokedex
pool_media = random.sample(tutti, 15)

# Difficile: prende i 15 con punteggio più alto
pool_difficile = sorted(tutti, key=punteggio, reverse=True)[:15]
```

---

## 10. torneo.py — Gestione del Torneo

`torneo.py` gestisce il bracket a eliminazione diretta con 16 Pokemon.

### Struttura del bracket

| Round | Match | Risultato |
|-------|-------|-----------|
| Ottavi (Round of 16) | 8 match | 16 Pokemon → 8 vincitori |
| Quarti di finale | 4 match | 8 Pokemon → 4 vincitori |
| Semifinali | 2 match | 4 Pokemon → 2 vincitori |
| Finale | 1 match | 2 Pokemon → 1 campione |

### Formato dei dati bracket

`bracket_dati` è una lista di 4 liste (una per round). Ogni match è un dizionario:

```python
match = {
    'a': 'Pikachu',     # Nome del primo combattente
    'b': 'Charizard',   # Nome del secondo combattente
    'vincitore': None   # None = non ancora disputato, altrimenti nome vincitore
}
```

Nel tabellone grafico:
- Il nome del giocatore appare sempre in **viola**
- Il vincitore ha una freccia `▶` davanti al nome
- Il bordo del box è viola se contiene il giocatore, verde se ha un vincitore

---

## 11. battaglia.py — Motore di Battaglia

`battaglia.py` coordina le mosse simultanee e gestisce la progressione del torneo.

### Flusso di un turno di battaglia

| Step | Azione |
|------|--------|
| 1 | La logica invia `'chiedi_mossa'` alla GUI → si attivano i pulsanti |
| 2 | Il giocatore clicca una mossa → la GUI invia `'mossa'` alla logica |
| 3 | La logica chiede alla CPU di scegliere la sua mossa (`ai.py`) |
| 4 | Le due mosse vengono risolte: se uno si cura e l'altro attacca, prima la cura |
| 5 | Si invia `'anim_attacco'` o `'anim_cura'` per le animazioni |
| 6 | Si aggiornano gli HP e si invia `'aggiorna'` alla GUI |
| 7 | Si aggiunge una riga al log con `'log'` |
| 8 | Se un Pokemon ha HP ≤ 0, si invia `'anim_ko'` e si determina il vincitore |
| 9 | La battaglia finisce: si invia `'risultato'` e si aspetta `'continua'` |

### Regola delle mosse simultanee

```python
# Ordine di risoluzione (priorità):
# 1. Le cure avvengono PRIMA degli attacchi
# 2. Gli attacchi avvengono in ordine di velocità (il più veloce prima)
# 3. In caso di doppio KO: perde il Pokemon più lento

if mossa_gio in ('pozione_normale', 'pozione_speciale'):
    applica_cura(giocatore)       # Prima la cura del giocatore

if mossa_avv in ('pozione_normale', 'pozione_speciale'):
    applica_cura(avversario)      # Poi la cura dell'avversario

# Poi gli attacchi in ordine di velocità
if giocatore.stats['speed'] >= avversario.stats['speed']:
    attacca(giocatore, avversario)
    attacca(avversario, giocatore)
else:
    attacca(avversario, giocatore)
    attacca(giocatore, avversario)
```

---

## 12. finestra_tk.py — Grafica Pygame

Il file più grande (~1350 righe). Gestisce tutto ciò che è visibile: rendering, input, animazioni, temi.

### Loop principale (`avvia`)

```python
while self.in_esecuzione:
    # 1. Gestione eventi Pygame (click, scroll, tastiera)
    for evento in pygame.event.get(): ...

    # 2. Legge messaggi dalla logica e aggiorna lo stato
    self._leggi_messaggi()

    # 3. Aggiorna posizioni animazioni (scatto, particelle, shake...)
    self._aggiorna_animazioni()

    # 4. Disegna tutto sul buffer
    self._disegna_frame()

    # 5. Mostra il buffer a schermo
    pygame.display.flip()

    # 6. Aspetta per mantenere ~20 FPS
    orologio.tick(1000 // TICK)
```

### Metodi di disegno principali

| Metodo | Funzione |
|--------|----------|
| `_txt(x, y, testo, font, col, ancora)` | Disegna testo con ancoraggio (`'nw'`, `'center'`, `'e'`, `'n'`...). Restituisce `(w, h)`. |
| `_rett(x1, y1, x2, y2, ...)` | Rettangolo semplice con sfondo e/o bordo. |
| `_rett_r(x1, y1, x2, y2, raggio, ...)` | Rettangolo con angoli arrotondati. |
| `_px(x1, y1, x2, y2, sfondo)` | Rettangolo con ombra nera offset +3px e angoli arrotondati (pixel-art). |
| `_linea(x1, y1, x2, y2, colore, sp)` | Linea retta. `sp` = spessore. |
| `_cerchio(cx, cy, r, sfondo, bordo)` | Cerchio con sfondo e/o bordo. |
| `_barra(x, y, lw, lh, val, max, col)` | Barra percentuale colorata (HP, ATK, ecc.). |
| `_overlay()` | Sovrappone un rettangolo nero semitrasparente (usato per il risultato). |
| `_btn_continua(label)` | Disegna il pulsante Continua/Gioca Ancora centrato in basso. |

### Gestione delle immagini

Tutte le immagini vengono caricate una sola volta e salvate in cache per non rileggere il disco ad ogni frame.

```python
# Cache principale per sprite Pokemon
self.cache_immagini = {}  # chiave: (nome, dim, specchiata)

# Cache per immagini di stile (pannelli, sole, luna, nuvole)
self.cache_stile = {}  # chiave: (nome_file, larghezza, altezza)
# Nota: cache_stile viene svuotata al cambio tema

# Il nome del file viene derivato dal nome del Pokemon:
# 'Pikachu'  → pikachu.png
# 'Mr. Mime' → mr.-mime.png  (spazi → trattini)
```

### Ancoraggi del testo (`_txt`)

| Ancora | Significato |
|--------|-------------|
| `'nw'` | In alto a sinistra (default) |
| `'n'` | Centrato in alto |
| `'ne'` | In alto a destra |
| `'w'` | Centrato a sinistra |
| `'center'` | Centrato sia orizz. che vert. |
| `'e'` | Centrato a destra |
| `'s'` | Centrato in basso |
| `'se'` | In basso a destra |

---

## 13. Sistema Temi Giorno/Notte

Il gioco ha due temi selezionabili nella schermata difficoltà tramite il toggle in basso al centro. Il cambio tema aggiorna istantaneamente tutti i colori e ricarica le immagini dei pannelli.

### Colori dei temi

| Variabile | Uso | Tema Scuro | Tema Chiaro |
|-----------|-----|-----------|-------------|
| `BG` | Sfondo principale | `#000000` nero | `#ffffff` bianco |
| `BG2` | Sfondo secondario | `#000000` | `#ffffff` |
| `BG3` | Sfondo terziario (barre, celle) | `#1E1E1E` grigio scuro | `#c8eafc` azzurro chiaro |
| `ACCENT` | Colore primario UI | `(255,255,255)` bianco | `#3D3D3D` grigio |
| `TXT` | Testo principale | `#ffffff` | `#0c1a2e` blu scuro |
| `TXT2` | Testo secondario | `#a78bba` viola chiaro | `#1a4a7a` blu medio |
| `BORDER` | Bordi | `#A3A3A300` trasparente! | `#000000` nero |
| `GOLD` | Oro per la finale | `#ffd700` | `#f57f17` |
| `COL_HP` | Colore barra HP | `#39ff14` verde neon | `#2e7d32` verde |
| `BARRA_BG` | Sfondo barre HP in battaglia | `#000000` | `#ffffff` |
| `BAR_BG` | Sfondo barra superiore | `#000000` | `(183,204,209)` azzurro |

> **Attenzione:** Il `BORDER` in tema scuro ha alpha = 0 (completamente trasparente). Questo significa che le linee del bracket e i bordi delle barre HP non sono visibili, dando un aspetto più minimale. In tema chiaro il bordo è nero solido.

### Colori fissi (identici in entrambi i temi)

| Costante | Valore | Uso |
|----------|--------|-----|
| `VIOLA_PLAYER` | `(168, 85, 247)` | Viola per evidenziare il giocatore nel tabellone |
| `COL_DEF` | `#1565c0` | Colore barra difesa |
| `COL_SPD` | `#a855f7` | Colore barra difesa speciale |
| `COL_ATK` | `#ff3535` | Colore barra attacco |
| `COL_SPA` | `#ff9f43` | Colore barra attacco speciale |
| `COL_VEL` | `#e879f9` | Colore barra velocità |

### Aspetto visivo per tema

**Tema Scuro — Schermata difficoltà:**
- Sfondo nero
- 80 stelle animate con scintillio sinusoidale (`sin(fase)`)
- Luna (`moon.png`, 110×110px) in alto a destra
- Toggle con stelline e pallino grigio a destra

**Tema Chiaro — Schermata difficoltà:**
- Gradiente cielo azzurro (righe orizzontali da `(100,185,255)` in alto a `(160,220,255)` in basso)
- 11 nuvole animate (`cloud1.png`...`cloud11.png`) scalate 1.2×, si spostano verso destra
- Sole (`sun.png`, 130×130px) in alto a destra
- Toggle con nuvolette e pallino dorato con raggi a sinistra

---

## 14. Sistema di Animazioni

Tutte le animazioni sono gestite da `_aggiorna_animazioni()` chiamata ogni frame. Ogni animazione è un dizionario con `frame`/`eta` (età) e `durata`.

### Elenco animazioni

| Animazione | Descrizione | Durata |
|-----------|-------------|--------|
| `animazione_scatto` | Il Pokemon si lancia verso l'avversario e torna indietro | 10 frame |
| `animazione_scatto_avv` | Come sopra ma per l'avversario (attacco doppio) | 10 frame |
| `animazione_ko` | Il Pokemon perde opacità gradualmente fino a 0 (dissolvenza) | 14 frame |
| `shake_schermo` | L'intera scena trema con offset X/Y casuali decrescenti | 8–10 frame |
| `scia_attiva` | Particelle colorate attorno all'attaccante (attacco speciale) | 18 frame |
| `onde_impatto` | 3 cerchi concentrici che si espandono al punto di impatto | 12–14 frame |
| `particelle_impatto` | 20 scintille che partono dall'impatto con gravità | 10–18 frame |
| `speed_lines` | Linee orizzontali di velocità | 8–9 frame |
| `bolle_cura` | 18 bolle verdi (normale) o viola (speciale) che salgono | 20–35 frame |
| `numeri_fluttuanti` | Numeri di danno/cura che salgono e spariscono | 70–100 frame |
| `nuvole_anim` | 11 nuvole che si spostano lentamente verso destra | continuo |
| `stelle_anim` | 80 stelle con drift lento e scintillio sinusoidale | continuo |

### Come funziona un'animazione — esempio: scatto

```python
# In _leggi_messaggi, quando arriva 'anim_attacco':
self.animazione_scatto = {'chi': 'giocatore', 'frame': 0, 'durata': 10}

# In _aggiorna_animazioni, ogni frame:
if self.animazione_scatto is not None:
    f = self.animazione_scatto['frame']
    d = self.animazione_scatto['durata']
    p = f / d  # progresso da 0.0 a 1.0

    # Prima metà (p < 0.5): avanza verso l'avversario
    # Seconda metà (p >= 0.5): torna indietro
    if p < 0.5:
        offset = int(distanza * (p / 0.5))
    else:
        offset = int(distanza * ((1 - p) / 0.5))

    self.offset_x_giocatore = offset
    self.animazione_scatto['frame'] += 1

    if f >= d:
        self.animazione_scatto = None  # Animazione terminata
```

### Colori della scia attacco speciale

| Moltiplicatore | Colore scia | Significato |
|----------------|-------------|-------------|
| `> 1` | `(255, 215, 0)` oro | Super efficace |
| `== 1` | `(180, 106, 255)` viola | Normale |
| `< 1` | `(116, 185, 255)` azzurro | Non molto efficace |
| `== 0` | `(99, 110, 114)` grigio | Immune |

---

## 15. Schermate del Gioco

### Schermata Difficoltà

Prima schermata del gioco. Sullo sfondo compaiono sprite decorativi di 10 Pokemon ai lati (5 a sinistra, 5 a destra).

| Elemento | Dettagli |
|----------|----------|
| Pulsanti | Centrati verticalmente, 420×76px ciascuno, gap 18px tra loro |
| Hover | Il pulsante si riempie col colore del bordo al passaggio del mouse |
| Toggle | 160×60px, centrato in basso a `y = H - 110`. Click cambia tema e ricarica pannelli |
| Stelle | 80 stelle, posizione casuale (seed=42), drift ±0.15px/frame, scintillio con `sin(fase)` |
| Nuvole | 11 nuvole `cloud1.png`...`cloud11.png`, scalate 1.2×, velocità 0.3–0.9 px/frame |

### Schermata Selezione Pokemon

| Elemento | Dettagli |
|----------|----------|
| Pannello sinistro | 230×716px. Mostra statistiche del Pokemon selezionato. Sfondo: `panel_*.png` |
| Bigpanel | 1050×716px. Sfondo della griglia. Immagine: `bigpanel_*.png` |
| Griglia | 5 colonne × 7 righe visibili. Cella 200×96px, gap 6px. Origine: `x=238, y=54` |
| Scrollbar | Verticale, 10px larghezza, `x = W - 16`. Thumb trascinabile col mouse |
| Pulsante INDIETRO | Top bar, posizione `x: W-230 → W-120`. Torna alla scelta difficoltà |
| Pulsante INIZIA | Top bar all'estrema destra `x: W-115 → W-10`. Attivo solo se Pokemon selezionato |
| Difficoltà | Il nome appare centrato nella top bar con colore verde/arancio/rosso |

### Schermata Tabellone

| Elemento | Dettagli |
|----------|----------|
| Box match | 155×56px. Ombra nera +3px. Bordo viola se contiene il giocatore, verde se ha vincitore |
| Linee connessione | Collegano i box tra i round. Colore `BORDER` (trasparente in tema scuro) |
| Freccia `▶` | Appare davanti al nome del vincitore in ogni box |
| Messaggio | Esito dell'ultima battaglia sopra il pulsante Continua |

### Schermata Battaglia

| Elemento | Dettagli |
|----------|----------|
| Wallpaper | Casuale dalla cartella `wallpaper_*/`. Non si ripete due volte di fila |
| Sprite giocatore | 320×320px, posizione `GX=50, GY=80`, specchiato orizzontalmente |
| Sprite avversario | 320×320px, posizione `AX=W-370, AY=140`, non specchiato |
| Barre HP/DEF/SpD | In alto, larghezza 300px. Mostra `valore/massimo` a destra |
| Log | Zona bassa sinistra (72% larghezza). Ultime 14 righe, ognuna con colore proprio |
| Pulsanti mossa | Zona bassa destra. 4 pulsanti verticali. Grigi e disabilitati durante il turno CPU |
| Overlay risultato | Rettangolo nero semitrasparente + messaggio bianco + pulsante Continua |

### Schermata Campione

- 12 raggi dorati emanano dal centro
- Testo "CAMPIONE DEL TORNEO" in oro (`GOLD`)
- Nome del Pokemon vincitore centrato
- Pulsante "GIOCA ANCORA" (riavvia dall'inizio)

---

## 16. Aggiungere Contenuti

### Nuovo Pokemon

```python
# 1. Aggiungi al file PokemonGame/pokedex.json:
{
    "nome": "NomePokemon",
    "tipi": ["Tipo1"],          # oppure ["Tipo1", "Tipo2"]
    "stats": {
        "hp": 100,
        "attack": 80,
        "defense": 70,
        "sp_attack": 90,
        "sp_defense": 75,
        "speed": 85
    }
}

# 2. Aggiungi l'immagine:
# File: PokemonGame/pokemon_images/nomepokemon.png
# Il nome deve essere in minuscolo.
# Se il nome ha spazi, usa il trattino:
# 'Mr. Mime' → mr.-mime.png
```

### Nuovi Wallpaper

Copia file `PNG`/`JPG`/`WEBP` nelle cartelle:
- `PokemonGame/wallpaper_dark/` per tema notte
- `PokemonGame/wallpaper_light/` per tema giorno

Il gioco li seleziona casualmente ad ogni battaglia e non ripete lo stesso due volte di fila (se ci sono almeno 2 file).

### Font personalizzato

```
PokemonGame/style/
├── PixelifySans-Regular.ttf   # testi normali
└── PixelifySans-Bold.ttf      # titoli e grassetti
```

Se i file non esistono, il gioco usa il font bitmap built-in di Pygame come fallback automatico (nessun errore).

### Immagini pannello

| File | Dimensione | Uso |
|------|-----------|-----|
| `panel_scuro.png` | 230 × 716 px | Pannello statistiche, tema notte |
| `panel_chiaro.png` | 230 × 716 px | Pannello statistiche, tema giorno |
| `bigpanel_scuro.png` | 1050 × 716 px | Sfondo griglia Pokemon, tema notte |
| `bigpanel_chiaro.png` | 1050 × 716 px | Sfondo griglia Pokemon, tema giorno |
| `sun.png` | 130 × 130 px | Sole nella schermata difficoltà (giorno) |
| `moon.png` | 110 × 110 px | Luna nella schermata difficoltà (notte) |
| `cloud1.png`...`cloud11.png` | qualsiasi | Nuvole animate (scalate 1.2× automaticamente) |

### Modificare le difficoltà

```python
# In ai.py, la funzione che calcola il pool:
def pool_avversari(tutti_pokemon, difficolta):
    punteggio = lambda p: sum(p['stats'].values())

    if difficolta == 'facile':
        return sorted(tutti_pokemon, key=punteggio)[:15]           # 15 più deboli

    elif difficolta == 'media':
        return random.sample(tutti_pokemon, 15)                     # 15 casuali

    else:  # difficile
        return sorted(tutti_pokemon, key=punteggio, reverse=True)[:15]  # 15 più forti

# Per rendere la modalità facile ancora più semplice,
# abbassa il numero 15 o cambia la formula del punteggio.
```

---

## 17. Appendice — Riferimento Rapido

### Shortcut da tastiera

| Tasto | Azione |
|-------|--------|
| `ESC` | Alterna tra schermo intero e finestra |
| `Alt + F4` | Chiude il gioco (da sistema operativo) |

### Tutte le variabili globali di colore

Queste variabili sono globali in `finestra_tk.py` e vengono aggiornate da `_applica_tema()`:

| Variabile | Aggiornata dal tema | Note |
|-----------|---------------------|------|
| `BG` | ✅ | Sfondo principale |
| `BG2` | ✅ | Sfondo secondario |
| `BG3` | ✅ | Sfondo terziario |
| `ACCENT` | ✅ | Colore primario UI |
| `ACCENT2` | ✅ | Alias di `ACCENT` |
| `OK` | ✅ | Verde |
| `WARN` | ✅ | Arancio |
| `ERR` | ✅ | Rosso |
| `TXT` | ✅ | Testo principale |
| `TXT2` | ✅ | Testo secondario |
| `BORDER` | ✅ | Bordi |
| `GOLD` | ✅ | Oro |
| `COL_HP` | ✅ | Barra HP |
| `COL_DEF` | ❌ fisso | `#1565c0` blu |
| `COL_SPD` | ❌ fisso | `#a855f7` viola |
| `COL_ATK` | ❌ fisso | `#ff3535` rosso |
| `COL_SPA` | ❌ fisso | `#ff9f43` arancio |
| `COL_VEL` | ❌ fisso | `#e879f9` rosa |
| `VIOLA_PLAYER` | ❌ fisso | `(168,85,247)` viola giocatore |

### Colori dei tipi Pokemon (`TIPO_COL`)

| Tipo | Colore |
|------|--------|
| Normal | `#9e9e9e` grigio |
| Fire | `#ff6b35` arancio |
| Water | `#0099ff` blu |
| Grass | `#39ff14` verde neon |
| Electric | `#ffd700` oro |
| Ice | `#48dbfb` azzurro |
| Fighting | `#ff2d55` rosso |
| Poison | `#b06aff` viola |
| Ground | `#c8a06e` marrone |
| Flying | `#74b9ff` azzurro chiaro |
| Psychic | `#fd79a8` rosa |
| Bug | `#a3cb38` verde oliva |
| Rock | `#b8b000` giallo scuro |
| Ghost | `#6c5ce7` indaco |
| Dragon | `#5352ed` blu/viola |
| Dark | `#636e72` grigio scuro |
| Steel | `#74b9ff` azzurro chiaro |
| Fairy | `#fd79a8` rosa |

---

> **Suggerimento di studio:** Apri `finestra_tk.py` e segui il flusso dalla funzione `avvia()` verso il basso. Ogni schermata ha il suo metodo `_disegna_*()` e ogni animazione viene aggiornata in `_aggiorna_animazioni()`. Le code sono il confine netto tra logica e grafica: tutto ciò che le attraversa è un messaggio dizionario.
