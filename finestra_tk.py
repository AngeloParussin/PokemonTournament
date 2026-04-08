# -*- coding: utf-8 -*-
# finestra_tk.py — grafica del Pokemon Tournament con Pygame

import pygame
import queue
import math
import os
import random

# ---------------------------------------------------------------
# TEMI
# ---------------------------------------------------------------

# Colori statistiche — identici in entrambi i temi
COL_DEF = "#1565c0"
COL_SPD = "#a855f7"
COL_ATK = "#ff3535"
COL_SPA = "#ff9f43"
COL_VEL = "#e879f9"

BG=BG2=BG3=ACCENT=ACCENT2=OK=WARN=ERR=TXT=TXT2=BORDER=GOLD = "#000000"
COL_HP = "#000000"

TEMA_SCURO = {
    "BG":"#000000","BG2":"#000000","BG3":"#1E1E1E",
    "ACCENT":(255,255,255),
    "OK":"#39ff14","WARN":"#ff6b35","ERR":"#ff2d55",
    "TXT":"#ffffff","TXT2":"#a78bba","BORDER":"#A3A3A300","GOLD":"#ffd700",
    "COL_HP":"#39ff14",
    "BARRA_BG":"#000000","BAR_BG":"#000000",
}
TEMA_CHIARO = {
    "BG":"#ffffff","BG2":"#ffffff","BG3":"#c8eafc",
    "ACCENT":"#3D3D3D",
    "OK":"#2e7d32","WARN":"#e65100","ERR":"#c62828",
    "TXT":"#0c1a2e","TXT2":"#1a4a7a","BORDER":"#000000","GOLD":"#f57f17",
    "COL_HP":"#2e7d32",
    "BARRA_BG":"#ffffff","BAR_BG":(183,204,209),
}

TIPO_COL = {
    "Normal":"#9e9e9e","Fire":"#ff6b35","Water":"#0099ff","Grass":"#39ff14",
    "Electric":"#ffd700","Ice":"#48dbfb","Fighting":"#ff2d55","Poison":"#b06aff",
    "Ground":"#c8a06e","Flying":"#74b9ff","Psychic":"#fd79a8","Bug":"#a3cb38",
    "Rock":"#b8b000","Ghost":"#6c5ce7","Dragon":"#5352ed","Dark":"#636e72",
    "Steel":"#74b9ff","Fairy":"#fd79a8",
}

VIOLA_PLAYER = (168, 85, 247)

# ---------------------------------------------------------------
# DIMENSIONI
# ---------------------------------------------------------------

W, H = 1280, 760
BAR  = 44
TICK = 50

SPR_SEL     = 36
SPR_PAN     = 72
SPR_B       = 320
SPR_OFF     = 0.05
SPR_CER_OFF = 0.25   # identico per selezione e pannello

GX = 50
GY = 80
AX = W - SPR_B - 50
AY = 140

LOW   = 282
LOG_N = 14

GRIGLIA_CELLA_W = 200
GRIGLIA_CELLA_H = 96
GRIGLIA_GAP     = 6
GRIGLIA_ORIG_X  = 238
GRIGLIA_ORIG_Y  = BAR + 10
GRIGLIA_COLONNE = 5
PANNELLO_L_W    = 230

BRACKET_TOP   = BAR + 35
BRACKET_H     = H - BAR - 65
BRACKET_BOX_W = 155
BRACKET_BOX_H = 56
BRACKET_GAP   = 18

FINAL_X1 = W // 2 - BRACKET_BOX_W // 2
FINAL_X2 = W // 2 + BRACKET_BOX_W // 2
SF_L_X2  = FINAL_X1 - BRACKET_GAP;  SF_L_X1 = SF_L_X2 - BRACKET_BOX_W
SF_R_X1  = FINAL_X2 + BRACKET_GAP;  SF_R_X2 = SF_R_X1 + BRACKET_BOX_W
QF_L_X2  = SF_L_X1 - BRACKET_GAP;  QF_L_X1 = QF_L_X2 - BRACKET_BOX_W
QF_R_X1  = SF_R_X2 + BRACKET_GAP;  QF_R_X2 = QF_R_X1 + BRACKET_BOX_W
R16_L_X2 = QF_L_X1 - BRACKET_GAP;  R16_L_X1 = R16_L_X2 - BRACKET_BOX_W
R16_R_X1 = QF_R_X2 + BRACKET_GAP;  R16_R_X2 = R16_R_X1 + BRACKET_BOX_W

R16_SLOT = BRACKET_H // 4
QF_SLOT  = BRACKET_H // 2
SF_Y     = BRACKET_TOP + BRACKET_H // 2 - BRACKET_BOX_H // 2

# ---------------------------------------------------------------
# UTILITA' COLORE
# ---------------------------------------------------------------

def col(c):
    if isinstance(c, (tuple, list)):
        return (c[0], c[1], c[2])
    return (int(c[1:3],16), int(c[3:5],16), int(c[5:7],16))

def ctk(c):
    if isinstance(c, tuple):
        return "#{:02x}{:02x}{:02x}".format(c[0],c[1],c[2])
    return c

# ---------------------------------------------------------------
# CLASSE FINESTRA
# ---------------------------------------------------------------

class Finestra:

    def __init__(self, cart="PokemonGame/pokemon_images", cartella_dati="PokemonGame"):
        self.cartella_immagini  = cart
        self.cartella_dati      = cartella_dati
        self.cartella_wallpaper = ""
        self.wallpaper_corrente = None
        self.ultimo_wallpaper   = None
        self.tema               = None
        self.barra_bg_colore    = "#000000"
        self.bar_top_colore     = "#000000"
        self.immagine_pannello  = None
        self.immagine_bigpanel  = None
        self.cache_stile        = {}
        self.hover_difficolta   = -1

        self.coda_comandi       = queue.Queue()
        self.coda_risposte      = queue.Queue()
        self.schermata_corrente = "attesa"

        # Selezione
        self.lista_pokemon          = []
        self.hover_indice           = -1
        self.selezionato_indice     = -1
        self.scroll_righe           = 0
        self.sb_dragging            = False
        self.difficolta_corrente    = ""
        self.nome_pokemon_giocatore = ""

        # Tabellone
        self.bracket_dati   = []
        self.nome_round_att = ""

        # Battaglia
        self.pokemon_giocatore   = None
        self.pokemon_avversario  = None
        self.nome_round_batt     = ""
        self.e_turno_mio         = False
        self.pozioni_norm        = 1
        self.pozioni_spec        = 1
        self.messaggio_risultato = ""
        self.mostra_continua     = False
        self.log_battaglia       = []
        self.pokemon_campione    = None

        # Animazioni battaglia
        self.offset_x_giocatore    = 0
        self.offset_x_avversario   = 0
        self.animazione_scatto     = None
        self.animazione_scatto_avv = None
        self.animazione_ko         = None
        self.opacita_giocatore     = 255
        self.opacita_avversario    = 255
        self.numeri_fluttuanti     = []
        self.particelle_speciali   = []
        self.scia_attiva           = None
        self.onde_impatto          = []
        self.particelle_impatto    = []
        self.speed_lines           = []
        self.bolle_cura            = []
        self.shake_schermo         = None
        self.offset_shake_x        = 0
        self.offset_shake_y        = 0

        # Animazioni sfondo
        self.nuvole_anim = []
        self.stelle_anim = []

        self.cache_immagini = {}
        self.hover_mossa    = -1
        self.schermo        = None
        self.in_esecuzione  = True
        self.is_fullscreen  = True

    # -----------------------------------------------------------
    # AVVIO
    # -----------------------------------------------------------

    def avvia(self, thread_logica):
        pygame.init()
        pygame.display.set_caption("Pokemon Tournament")
        self.schermo = pygame.display.set_mode((W, H), pygame.SRCALPHA | pygame.FULLSCREEN)
        self._crea_font()
        self._applica_tema("scuro")
        thread_logica.start()
        orologio = pygame.time.Clock()

        while self.in_esecuzione:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.coda_risposte.put({"tipo": "esci"})
                    self.in_esecuzione = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self._toggle_fullscreen()
                elif evento.type == pygame.MOUSEMOTION:
                    self._mouse_muove(evento.pos[0], evento.pos[1])
                    if self.sb_dragging:
                        self._scrollbar_drag(evento.pos[1])
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if not self._scrollbar_inizia_drag(evento.pos[0], evento.pos[1]):
                        self._mouse_click(evento.pos[0], evento.pos[1])
                elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                    self.sb_dragging = False
                elif evento.type == pygame.MOUSEWHEEL:
                    self._mouse_scroll(evento.y)

            self._leggi_messaggi()
            self._aggiorna_animazioni()
            self._disegna_frame()
            pygame.display.flip()
            orologio.tick(1000 // TICK)

        pygame.quit()

    def _crea_font(self):
        r = os.path.join(self.cartella_dati, "style", "PixelifySans-Regular.ttf")
        b = os.path.join(self.cartella_dati, "style", "PixelifySans-Bold.ttf")
        if not os.path.isfile(b): b = r
        def pf(percorso, size):
            if os.path.isfile(percorso):
                try: return pygame.font.Font(percorso, size)
                except: pass
            return pygame.font.Font(None, size)
        self.font_piccolo    = pf(r, 16)
        self.font_normale    = pf(r, 19)
        self.font_log        = pf(r, 18)
        self.font_grassetto  = pf(b, 21)
        self.font_titolo     = pf(b, 28)
        self.font_grande     = pf(b, 38)
        self.font_simboli_s  = pf(r, 16)
        self.font_simboli_b  = pf(b, 28)
        self.font_simboli_xl = pf(b, 38)

    def _applica_tema(self, nome_tema):
        global BG,BG2,BG3,ACCENT,ACCENT2,OK,WARN,ERR,TXT,TXT2,BORDER,GOLD,COL_HP
        self.tema = nome_tema
        t = TEMA_SCURO if nome_tema == "scuro" else TEMA_CHIARO
        BG=t["BG"]; BG2=t["BG2"]; BG3=t["BG3"]
        ACCENT=t["ACCENT"]; ACCENT2=t["ACCENT"]   # ACCENT2 identico ad ACCENT
        OK=t["OK"]; WARN=t["WARN"]; ERR=t["ERR"]
        TXT=t["TXT"]; TXT2=t["TXT2"]; BORDER=t["BORDER"]; GOLD=t["GOLD"]
        COL_HP=t["COL_HP"]
        self.barra_bg_colore    = t["BARRA_BG"]
        self.bar_top_colore     = t["BAR_BG"]
        self.cartella_wallpaper = os.path.join(self.cartella_dati,
            "wallpaper_dark" if nome_tema=="scuro" else "wallpaper_light")
        self.immagine_pannello  = self._carica_immagine_stile(f"panel_{nome_tema}.png",   PANNELLO_L_W,    H - BAR)
        self.immagine_bigpanel  = self._carica_immagine_stile(f"bigpanel_{nome_tema}.png", W - PANNELLO_L_W, H - BAR)
        self.cache_stile = {}
        self._init_nuvole()
        self._init_stelle()

    def _init_nuvole(self):
        rng = random.Random(99)
        ys = [BAR+30,BAR+55,BAR+20,BAR+65,BAR+35,BAR+180,BAR+300,BAR+400,BAR+250,BAR+160,BAR+350]
        self.nuvole_anim = [
            {"k":k+1,"x":float(rng.randint(-200,W+100)),"y":float(ys[k]),"vx":rng.uniform(0.3,0.9)}
            for k in range(11)
        ]

    def _init_stelle(self):
        rng = random.Random(42)
        self.stelle_anim = [
            {"x":float(rng.randint(0,W)),"y":float(rng.randint(BAR+4,H-10)),
             "vx":rng.uniform(-0.15,0.15),"vy":rng.uniform(-0.08,0.08),
             "r":rng.randint(1,3),"bright":rng.randint(150,255),"fase":rng.uniform(0,math.pi*2)}
            for _ in range(80)
        ]

    def _toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        flags = pygame.FULLSCREEN | pygame.SRCALPHA if self.is_fullscreen else pygame.SRCALPHA
        self.schermo = pygame.display.set_mode((W, H), flags)

    # -----------------------------------------------------------
    # DISEGNO PRINCIPALE
    # -----------------------------------------------------------

    def _disegna_frame(self):
        self._sfondo()
        self._barra_top()
        s = self.schermata_corrente
        if   s == "difficolta": self._disegna_difficolta()
        elif s == "selezione":  self._disegna_selezione()
        elif s == "tabellone":  self._disegna_tabellone()
        elif s == "battaglia":  self._disegna_battaglia()
        elif s == "campione":   self._disegna_campione()
        else:
            self._txt(W//2, H//2, "CARICAMENTO...", self.font_grande, col(ACCENT), "center")

        if self.is_fullscreen:
            sw, sh = self.schermo.get_size()
            if sh > H: pygame.draw.rect(self.schermo, (0,0,0), pygame.Rect(0, H, sw, sh-H))
            if sw > W: pygame.draw.rect(self.schermo, (0,0,0), pygame.Rect(W, 0, sw-W, sh))

    # -----------------------------------------------------------
    # PRIMITIVE
    # -----------------------------------------------------------

    def _txt(self, x, y, testo, font, colore, ancora="nw"):
        img = font.render(str(testo), True, colore)
        w, h = img.get_width(), img.get_height()
        if   ancora=="nw":     px,py = x,      y
        elif ancora=="w":      px,py = x,      y-h//2
        elif ancora=="e":      px,py = x-w,    y-h//2
        elif ancora=="ne":     px,py = x-w,    y
        elif ancora=="center": px,py = x-w//2, y-h//2
        elif ancora=="n":      px,py = x-w//2, y
        elif ancora=="s":      px,py = x-w//2, y-h
        elif ancora=="se":     px,py = x-w,    y-h
        else:                  px,py = x,      y
        self.schermo.blit(img, (px, py))
        return w, h

    def _rett(self, x1, y1, x2, y2, sfondo=None, bordo=None, sp=1):
        r = pygame.Rect(x1, y1, x2-x1, y2-y1)
        if sfondo: pygame.draw.rect(self.schermo, col(sfondo), r)
        if bordo:  pygame.draw.rect(self.schermo, col(bordo), r, sp)

    def _rett_r(self, x1, y1, x2, y2, raggio=12, sfondo=None, bordo=None, sp=1):
        raggio = min(raggio, (x2-x1)//2, (y2-y1)//2)
        r = pygame.Rect(x1, y1, x2-x1, y2-y1)
        if sfondo: pygame.draw.rect(self.schermo, col(sfondo), r, 0, border_radius=raggio)
        if bordo:  pygame.draw.rect(self.schermo, col(bordo),  r, sp, border_radius=raggio)

    def _px(self, x1, y1, x2, y2, sfondo, ombra=True):
        lw, lh = x2-x1, y2-y1
        if ombra:
            pygame.draw.rect(self.schermo, (0,0,0), pygame.Rect(x1+3,y1+3,lw,lh), 0, 10)
        pygame.draw.rect(self.schermo, col(sfondo), pygame.Rect(x1,y1,lw,lh), 0, 10)

    def _linea(self, x1, y1, x2, y2, colore, sp=1):
        pygame.draw.line(self.schermo, col(colore), (x1,y1), (x2,y2), sp)

    def _cerchio(self, cx, cy, raggio, sfondo=None, bordo=None, sp=2):
        if sfondo: pygame.draw.circle(self.schermo, col(sfondo), (cx,cy), raggio)
        if bordo:  pygame.draw.circle(self.schermo, col(bordo),  (cx,cy), raggio, sp)

    def _barra(self, x, y, lw, lh, valore, massimo, c_fill):
        raggio = max(2, lh//2)
        r = pygame.Rect(x, y, lw, lh)
        pygame.draw.rect(self.schermo, col(BG3),   r, 0, border_radius=raggio)
        pygame.draw.rect(self.schermo, col(BORDER), r, 1, border_radius=raggio)
        if massimo > 0 and valore > 0:
            pieni = max(0, int(lw * min(valore,massimo)/massimo))
            if pieni > 0:
                pygame.draw.rect(self.schermo, col(c_fill), pygame.Rect(x,y,pieni,lh), 0, border_radius=raggio)

    def _overlay(self):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0,0,0,160))
        self.schermo.blit(s, (0,0))

    def _btn_continua(self, label="[ CONTINUA ]"):
        x1,y1,x2,y2 = self._rett_cont()
        self._px(x1,y1,x2,y2,ACCENT)
        self._txt((x1+x2)//2,(y1+y2)//2, label, self.font_grassetto, col(BG), "center")

    # -----------------------------------------------------------
    # IMMAGINI
    # -----------------------------------------------------------

    def _carica_immagine_stile(self, nome_file, lw, lh):
        percorso = os.path.join(self.cartella_dati, "style", nome_file)
        if not os.path.isfile(percorso): return None
        try:
            from PIL import Image
            img = Image.open(percorso).convert("RGBA").resize((lw,lh), Image.LANCZOS)
            return pygame.image.fromstring(img.tobytes(), (lw,lh), "RGBA")
        except: pass
        try:
            sup = pygame.image.load(percorso).convert_alpha()
            return pygame.transform.scale(sup, (lw,lh))
        except: return None

    def _carica_stile_cached(self, nome_file, lw, lh):
        k = (nome_file, lw, lh)
        if k not in self.cache_stile:
            self.cache_stile[k] = self._carica_immagine_stile(nome_file, lw, lh)
        return self.cache_stile[k]

    def _carica_wallpaper(self):
        area = (W, H-LOW-BAR)
        if not os.path.isdir(self.cartella_wallpaper): return None
        ext = (".png",".jpg",".jpeg",".bmp",".webp")
        files = [f for f in os.listdir(self.cartella_wallpaper) if f.lower().endswith(ext)]
        if not files: return None
        if len(files) > 1 and self.ultimo_wallpaper in files:
            files = [f for f in files if f != self.ultimo_wallpaper]
        scelta = random.choice(files)
        self.ultimo_wallpaper = scelta
        percorso = os.path.join(self.cartella_wallpaper, scelta)
        try:
            from PIL import Image
            img = Image.open(percorso).convert("RGBA").resize(area, Image.LANCZOS)
            return pygame.image.fromstring(img.tobytes(), area, "RGBA")
        except: pass
        try:
            sup = pygame.image.load(percorso).convert_alpha()
            return pygame.transform.scale(sup, area)
        except: return None

    def _carica_immagine(self, nome, dim, specchiata=False):
        chiave = (nome, dim, specchiata)
        if chiave in self.cache_immagini: return self.cache_immagini[chiave]
        n = nome.lower()
        for nf in [n+".png", n.replace(" ","-")+".png"]:
            percorso = os.path.join(self.cartella_immagini, nf)
            if not os.path.isfile(percorso): continue
            try:
                from PIL import Image
                img = Image.open(percorso).convert("RGBA").resize((dim,dim), Image.NEAREST)
                if specchiata: img = img.transpose(Image.FLIP_LEFT_RIGHT)
                sup = pygame.image.fromstring(img.tobytes(), (dim,dim), "RGBA")
                self.cache_immagini[chiave] = sup
                return sup
            except: pass
            try:
                sup = pygame.image.load(percorso).convert_alpha()
                sup = pygame.transform.scale(sup, (dim,dim))
                if specchiata: sup = pygame.transform.flip(sup, True, False)
                self.cache_immagini[chiave] = sup
                return sup
            except: pass
        self.cache_immagini[chiave] = None
        return None

    def _sprite_libero(self, pokemon, cx, cy, dim):
        img = self._carica_immagine(pokemon["nome"], dim)
        if img:
            self.schermo.blit(img, (cx-dim//2, cy-dim//2-int(dim*0.20)))
        else:
            tipo = pokemon["tipi"][0] if pokemon["tipi"] else "Normal"
            self._txt(cx,cy,pokemon["nome"][0].upper(),self.font_titolo,col(TIPO_COL.get(tipo,TXT2)),"center")

    def _sprite_cerchio(self, pokemon, cx, cy, raggio):
        tipo = pokemon["tipi"][0] if pokemon["tipi"] else "Normal"
        ct   = TIPO_COL.get(tipo, TXT2)
        self._cerchio(cx,cy,raggio,sfondo=BG3,bordo=ct,sp=2)
        dim = int(raggio*3)
        img = self._carica_immagine(pokemon["nome"], dim)
        if img:
            self.schermo.blit(img, (cx-dim//2, cy-dim//2-int(dim*SPR_CER_OFF)))
        else:
            self._txt(cx,cy,pokemon["nome"][0].upper(),self.font_grassetto,col(ct),"center")
        self._cerchio(cx,cy,raggio+1,bordo=ct,sp=1)

    def _sprite_battaglia(self, pokemon, cx, cy, opacita, specchiato=False):
        img = self._carica_immagine(pokemon["nome"], SPR_B, specchiata=specchiato)
        if img:
            if opacita < 255:
                s = img.copy(); s.set_alpha(opacita)
                self.schermo.blit(s, (cx-SPR_B//2, cy-SPR_B//2))
            else:
                self.schermo.blit(img, (cx-SPR_B//2, cy-SPR_B//2))
        else:
            tipo = pokemon["tipi"][0] if pokemon["tipi"] else "Normal"
            self._txt(cx,cy,pokemon["nome"][0].upper(),self.font_grande,col(TIPO_COL.get(tipo,TXT2)),"center")

    # -----------------------------------------------------------
    # MESSAGGI DALLA LOGICA
    # -----------------------------------------------------------

    def _leggi_messaggi(self):
        while True:
            try: m = self.coda_comandi.get_nowait()
            except: break
            tipo = m["tipo"]

            if tipo == "difficolta":
                self.schermata_corrente = "difficolta"
                self.lista_pokemon      = m.get("pool", [])
                self.log_battaglia      = []

            elif tipo == "selezione":
                self.lista_pokemon       = m["pool"]
                self.difficolta_corrente = m.get("difficolta","")
                self.schermata_corrente  = "selezione"
                self.hover_indice        = -1
                self.selezionato_indice  = -1
                self.scroll_righe        = 0

            elif tipo == "tabellone":
                self.bracket_dati        = m["bracket"]
                self.nome_round_att      = m.get("round_attuale","")
                self.messaggio_risultato = m.get("messaggio","")
                self.mostra_continua     = True
                self.schermata_corrente  = "tabellone"

            elif tipo == "battaglia_inizia":
                g = m["giocatore"]; a = m["avversario"]
                self.pokemon_giocatore      = g
                self.pokemon_avversario     = a
                self.nome_round_batt        = m.get("round","")
                self.nome_pokemon_giocatore = g.get("nome","")
                self.log_battaglia          = []
                self.e_turno_mio            = False
                self.mostra_continua        = False
                self.messaggio_risultato    = ""
                self.pozioni_norm           = g["pozioni_normali"]
                self.pozioni_spec           = g["pozioni_speciali"]
                self.offset_x_giocatore = self.offset_x_avversario = 0
                self.animazione_scatto = self.animazione_scatto_avv = self.animazione_ko = None
                self.opacita_giocatore = self.opacita_avversario = 255
                self.numeri_fluttuanti = []; self.particelle_speciali = []
                self.onde_impatto      = []; self.particelle_impatto  = []
                self.speed_lines       = []; self.bolle_cura          = []
                self.scia_attiva       = None
                self.shake_schermo     = None
                self.offset_shake_x    = self.offset_shake_y = 0
                self._carica_immagine(g["nome"], SPR_B)
                self._carica_immagine(a["nome"], SPR_B)
                if self.wallpaper_corrente is None:
                    self.wallpaper_corrente = self._carica_wallpaper()
                self.schermata_corrente = "battaglia"

            elif tipo == "aggiorna":
                self.pokemon_giocatore  = m["giocatore"]
                self.pokemon_avversario = m["avversario"]
                self.pozioni_norm = self.pokemon_giocatore["pozioni_normali"]
                self.pozioni_spec = self.pokemon_giocatore["pozioni_speciali"]

            elif tipo == "log":
                self.log_battaglia.append((m["testo"], ctk(m["colore"])))
                if len(self.log_battaglia) > 100:
                    self.log_battaglia = self.log_battaglia[-100:]

            elif tipo == "anim_attacco":
                chi    = m["chi"]
                valori = [(v[0],ctk(v[1])) for v in m["valori"]]
                self.animazione_scatto = {"chi":chi,"frame":0,"durata":10}
                self.shake_schermo     = {"frame":0,"durata":8,"intensita":5}
                e_gio = chi=="giocatore"
                ix = (AX if e_gio else GX)+SPR_B//2
                iy = (AY if e_gio else GY)+int(SPR_B*0.55)
                ox = (GX if e_gio else AX)+SPR_B//2
                oy = (GY if e_gio else AY)+int(SPR_B*0.55)
                dir_x = 1.0 if e_gio else -1.0
                bersaglio = "avversario" if e_gio else "giocatore"
                for k in range(3):
                    self.onde_impatto.append({
                        "chi_bersaglio":bersaglio,"raggio":0,"raggio_max":80+k*40,
                        "colore":(255,220,80),"alpha":220-k*50,"eta":k*3,"durata":14})
                for _ in range(20):
                    ang = math.radians(random.uniform(-60,60))+(math.pi if dir_x>0 else 0)
                    vel = random.uniform(5,14)
                    self.particelle_impatto.append({
                        "chi_bersaglio":bersaglio,"x":float(ix),"y":float(iy),
                        "vx":math.cos(ang)*vel,"vy":math.sin(ang)*vel-random.uniform(1,4),
                        "eta":0,"durata":random.randint(10,18),"raggio":random.randint(2,6),
                        "colore":random.choice([(255,200,50),(255,140,20),(255,255,150),(255,100,30)])})
                for _ in range(8):
                    self.speed_lines.append({
                        "x1":float(ox),"y1":float(oy+random.uniform(-SPR_B*0.2,SPR_B*0.2)),
                        "dir_x":dir_x,"lunghezza":random.randint(60,140),"eta":0,"durata":8})
                for i,(t,c) in enumerate(valori):
                    self.numeri_fluttuanti.append({
                        "testo":t,"colore":c,"x":float(ix),"y":float(iy-i*26),"eta":0,"durata":70})

            elif tipo == "anim_attacco_doppio":
                vg = [(v[0],ctk(v[1])) for v in m["valori_gio"]]
                va = [(v[0],ctk(v[1])) for v in m["valori_avv"]]
                self.animazione_scatto     = {"chi":"giocatore","frame":0,"durata":10}
                self.animazione_scatto_avv = {"chi":"avversario","frame":0,"durata":10}
                self.shake_schermo         = {"frame":0,"durata":10,"intensita":7}
                for chi_b,dir_x in [("avversario",1.0),("giocatore",-1.0)]:
                    for k in range(2):
                        self.onde_impatto.append({
                            "chi_bersaglio":chi_b,"raggio":0,"raggio_max":70+k*35,
                            "colore":(255,220,80),"alpha":200-k*60,"eta":k*3,"durata":12})
                    for _ in range(12):
                        ang = math.radians(random.uniform(-60,60))+(math.pi if dir_x>0 else 0)
                        vel = random.uniform(4,11)
                        self.particelle_impatto.append({
                            "chi_bersaglio":chi_b,"x":0.0,"y":0.0,
                            "vx":math.cos(ang)*vel,"vy":math.sin(ang)*vel-random.uniform(1,3),
                            "eta":0,"durata":random.randint(8,14),"raggio":random.randint(2,5),
                            "colore":random.choice([(255,200,50),(255,140,20),(255,255,150)])})
                for i,(t,c) in enumerate(vg):
                    self.numeri_fluttuanti.append({
                        "testo":t,"colore":c,"x":float(AX+SPR_B//2),
                        "y":float(AY+int(SPR_B*0.18)-i*26),"eta":0,"durata":70})
                for i,(t,c) in enumerate(va):
                    self.numeri_fluttuanti.append({
                        "testo":t,"colore":c,"x":float(GX+SPR_B//2),
                        "y":float(GY+int(SPR_B*0.18)-i*26),"eta":0,"durata":70})

            elif tipo == "anim_ko":
                self.animazione_ko         = {"chi":m["chi"],"frame":0,"durata":14}
                self.animazione_scatto     = self.animazione_scatto_avv = None
                self.offset_x_giocatore    = self.offset_x_avversario  = 0

            elif tipo == "anim_speciale":
                chi  = m["chi"]
                mult = m["moltiplicatore"]
                cscia = (255,215,0) if mult>1 else ((99,110,114) if mult==0 else ((116,185,255) if mult<1 else (180,106,255)))
                self.scia_attiva = {"chi":chi,"colore":cscia,"frame_rimasti":18}
                e_gio = chi=="giocatore"
                ox = (GX if e_gio else AX)+SPR_B//2
                oy = (GY if e_gio else AY)+int(SPR_B*0.55)
                dir_x = 1.0 if e_gio else -1.0
                for _ in range(10):
                    self.speed_lines.append({
                        "x1":float(ox),"y1":float(oy+random.uniform(-SPR_B*0.35,SPR_B*0.35)),
                        "dir_x":dir_x,"lunghezza":random.randint(70,160),"eta":0,"durata":9})

            elif tipo == "anim_cura":
                chi    = m["chi"]
                valori = [(v[0],ctk(v[1])) for v in m["valori"]]
                e_gio  = chi=="giocatore"
                px = (GX if e_gio else AX)+SPR_B//2
                py = (GY if e_gio else AY)+int(SPR_B*0.18)
                for i,(t,c) in enumerate(valori):
                    self.numeri_fluttuanti.append({
                        "testo":t,"colore":c,"x":float(px),"y":float(py-i*30),"eta":0,"durata":100})
                c_bolla = (160,80,255) if m.get("tipo_pozione")=="speciale" else (60,220,100)
                by_off  = (GY if e_gio else AY)+SPR_B-20
                for _ in range(18):
                    self.bolle_cura.append({
                        "x":float(px+random.uniform(-SPR_B*0.28,SPR_B*0.28)),
                        "y":float(by_off+random.uniform(-20,20)),
                        "vy":random.uniform(-3.5,-1.8),"vx":random.uniform(-0.8,0.8),
                        "raggio":random.randint(4,11),"eta":random.randint(0,8),
                        "durata":random.randint(20,35),"colore":c_bolla})

            elif tipo == "chiedi_mossa":
                self.pokemon_giocatore = m["giocatore"]
                self.pozioni_norm      = self.pokemon_giocatore["pozioni_normali"]
                self.pozioni_spec      = self.pokemon_giocatore["pozioni_speciali"]
                self.e_turno_mio       = True

            elif tipo == "risultato":
                self.e_turno_mio         = False
                self.messaggio_risultato = m["messaggio"]
                self.mostra_continua     = True

            elif tipo == "campione":
                self.messaggio_risultato = m["messaggio"]
                self.pokemon_campione    = m.get("pokemon", None)
                self.schermata_corrente  = "campione"
                self.mostra_continua     = True
                self.wallpaper_corrente  = None

    # -----------------------------------------------------------
    # ANIMAZIONI
    # -----------------------------------------------------------

    def _aggiorna_animazioni(self):
        distanza = AX - GX - SPR_B//2

        def sp(frame, durata):
            if frame >= durata: return 0
            p = frame/durata
            return int(distanza*(p/0.5)) if p<0.5 else int(distanza*((1-p)/0.5))

        if self.animazione_scatto is not None:
            f=self.animazione_scatto["frame"]; d=self.animazione_scatto["durata"]
            chi=self.animazione_scatto["chi"]
            if f < d:
                s=sp(f,d)
                if chi=="giocatore":
                    self.offset_x_giocatore=s
                    if self.animazione_scatto_avv is None: self.offset_x_avversario=0
                else:
                    self.offset_x_avversario=-s
                    if self.animazione_scatto_avv is None: self.offset_x_giocatore=0
                self.animazione_scatto["frame"]+=1
            else:
                if chi=="giocatore": self.offset_x_giocatore=0
                else:                self.offset_x_avversario=0
                self.animazione_scatto=None

        if self.animazione_scatto_avv is not None:
            f=self.animazione_scatto_avv["frame"]; d=self.animazione_scatto_avv["durata"]
            if f < d:
                self.offset_x_avversario=-sp(f,d)
                self.animazione_scatto_avv["frame"]+=1
            else:
                self.offset_x_avversario=0; self.animazione_scatto_avv=None

        if self.animazione_ko is not None:
            f=self.animazione_ko["frame"]; d=self.animazione_ko["durata"]
            chi=self.animazione_ko["chi"]
            if f < d:
                o=int(255*(1-f/d))
                if chi=="giocatore": self.opacita_giocatore=o
                else:                self.opacita_avversario=o
                self.animazione_ko["frame"]+=1
            else:
                if chi=="giocatore": self.opacita_giocatore=0
                else:                self.opacita_avversario=0
                self.animazione_ko=None

        self.numeri_fluttuanti = [
            {**n,"y":n["y"]-1.2,"eta":n["eta"]+1}
            for n in self.numeri_fluttuanti if n["eta"]+1<n["durata"]
        ]

        onde_vive=[]
        for o in self.onde_impatto:
            o["eta"]+=1
            if o["eta"]<o["durata"]:
                o["raggio"]=int(o["raggio_max"]*o["eta"]/o["durata"])
                onde_vive.append(o)
        self.onde_impatto=onde_vive

        pi_vive=[]
        for p in self.particelle_impatto:
            if p["eta"]==0:
                if p["chi_bersaglio"]=="giocatore":
                    p["x"]=float(GX+self.offset_x_giocatore+SPR_B//2)
                    p["y"]=float(GY+int(SPR_B*0.55))
                else:
                    p["x"]=float(AX+self.offset_x_avversario+SPR_B//2)
                    p["y"]=float(AY+int(SPR_B*0.55))
            p["x"]+=p["vx"]; p["y"]+=p["vy"]
            p["vy"]+=0.5; p["vx"]*=0.92; p["eta"]+=1
            if p["eta"]<p["durata"]: pi_vive.append(p)
        self.particelle_impatto=pi_vive

        bolle_vive=[]
        for b in self.bolle_cura:
            b["eta"]+=1
            if b["eta"]>0:
                b["x"]+=b["vx"]+math.sin(b["eta"]*0.4)*0.6
                b["y"]+=b["vy"]
            if b["eta"]<b["durata"]: bolle_vive.append(b)
        self.bolle_cura=bolle_vive

        self.speed_lines=[{**sl,"eta":sl["eta"]+1} for sl in self.speed_lines if sl["eta"]+1<sl["durata"]]

        if self.shake_schermo is not None:
            f=self.shake_schermo["frame"]; d=self.shake_schermo["durata"]
            intens=self.shake_schermo["intensita"]
            if f < d:
                scala=1-f/d
                self.offset_shake_x=int(random.uniform(-intens,intens)*scala)
                self.offset_shake_y=int(random.uniform(-intens,intens)*scala)
                self.shake_schermo["frame"]+=1
            else:
                self.offset_shake_x=self.offset_shake_y=0
                self.shake_schermo=None

        if self.scia_attiva is not None:
            chi_s=self.scia_attiva["chi"]; cscia=self.scia_attiva["colore"]
            e_gio=chi_s=="giocatore"
            sx=(GX+self.offset_x_giocatore if e_gio else AX+self.offset_x_avversario)+SPR_B//2
            sy=(GY if e_gio else AY)+SPR_B//2-int(SPR_B*SPR_OFF)
            for _ in range(4):
                ang=math.radians(random.uniform(0,360)); dist=random.uniform(SPR_B*0.1,SPR_B*0.3)
                self.particelle_speciali.append({
                    "x":float(sx+math.cos(ang)*dist),"y":float(sy+math.sin(ang)*dist*0.6),
                    "vx":random.uniform(-1.5,1.5),"vy":random.uniform(-2.5,-0.5),
                    "eta":0,"durata":random.randint(8,16),"raggio":random.randint(3,7),"colore":cscia})
            self.scia_attiva["frame_rimasti"]-=1
            if self.scia_attiva["frame_rimasti"]<=0: self.scia_attiva=None

        vive=[]
        for p in self.particelle_speciali:
            p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["vy"]+=0.3; p["eta"]+=1
            if p["eta"]<p["durata"]: vive.append(p)
        self.particelle_speciali=vive

        if self.schermata_corrente=="difficolta":
            if self.tema=="chiaro":
                for n in self.nuvole_anim:
                    n["x"]+=n["vx"]
                    if n["x"]>W+300: n["x"]=-300.0
            else:
                for s in self.stelle_anim:
                    s["x"]+=s["vx"]; s["y"]+=s["vy"]; s["fase"]+=0.04
                    if s["x"]<0:   s["x"]=float(W)
                    if s["x"]>W:   s["x"]=0.0
                    if s["y"]<BAR: s["y"]=float(H-10)
                    if s["y"]>H:   s["y"]=float(BAR+4)

    # -----------------------------------------------------------
    # EVENTI MOUSE
    # -----------------------------------------------------------

    def _mouse_muove(self, x, y):
        if self.schermata_corrente=="selezione":
            self.hover_indice=self._cella(x,y)
        elif self.schermata_corrente=="difficolta":
            self.hover_difficolta=-1
            for i,r in enumerate(self._rett_diff()):
                if self._in(x,y,r): self.hover_difficolta=i; break
        elif self.schermata_corrente=="battaglia":
            self.hover_mossa=-1
            for i,r in enumerate(self._rett_mosse()):
                if self._in(x,y,r): self.hover_mossa=i; break

    def _mouse_click(self, x, y):
        s=self.schermata_corrente
        if s=="difficolta":
            if self._in(x,y,self._rett_toggle()):
                self._applica_tema("chiaro" if self.tema=="scuro" else "scuro")
                self.wallpaper_corrente=None; return
            for i,r in enumerate(self._rett_diff()):
                if self._in(x,y,r):
                    self.coda_risposte.put({"tipo":"difficolta","valore":["facile","media","difficile"][i]}); return
        elif s=="selezione":
            if self._in(x,y,self._rett_indietro()):
                self.coda_risposte.put({"tipo":"indietro"}); return
            if self.selezionato_indice>=0 and self._in(x,y,self._rett_inizia()):
                pk=self.lista_pokemon[self.selezionato_indice]
                self.nome_pokemon_giocatore=pk.get("nome","")
                self.coda_risposte.put({"tipo":"pokemon","valore":pk}); return
            idx=self._cella(x,y)
            if idx>=0: self.selezionato_indice=self.hover_indice=idx
        elif s=="battaglia":
            if self.e_turno_mio:
                nomi=["attacco","attacco_speciale","pozione_normale","pozione_speciale"]
                dis=[False,False,self.pozioni_norm<=0,self.pozioni_spec<=0]
                for i,r in enumerate(self._rett_mosse()):
                    if not dis[i] and self._in(x,y,r):
                        self.e_turno_mio=False
                        self.coda_risposte.put({"tipo":"mossa","valore":nomi[i]}); return
            if self.mostra_continua and self._in(x,y,self._rett_cont()):
                self.mostra_continua=False; self.coda_risposte.put({"tipo":"continua"})
        elif s in ("tabellone","campione"):
            if self.mostra_continua and self._in(x,y,self._rett_cont()):
                self.mostra_continua=False; self.coda_risposte.put({"tipo":"continua"})

    def _mouse_scroll(self, dy):
        if self.schermata_corrente!="selezione": return
        dir_=-1 if dy>0 else 1
        max_=max(0,math.ceil(len(self.lista_pokemon)/GRIGLIA_COLONNE)-7)
        self.scroll_righe=max(0,min(max_,self.scroll_righe+dir_))

    # -----------------------------------------------------------
    # HIT TEST E RETTANGOLI
    # -----------------------------------------------------------

    def _in(self, px, py, r): return r[0]<=px<=r[2] and r[1]<=py<=r[3]

    def _rett_sb(self):      return (W-16, GRIGLIA_ORIG_Y, 10, H-GRIGLIA_ORIG_Y-8)
    def _rett_inizia(self):  return (W-115, 4, W-10,  BAR-4)
    def _rett_indietro(self):return (W-230, 4, W-120, BAR-4)
    def _rett_cont(self):
        lw,lh=260,48; x1=W//2-lw//2; return (x1,H-76,x1+lw,H-76+lh)
    def _rett_toggle(self):
        tw,th=160,60; return (W//2-tw//2,H-110,W//2+tw//2,H-110+th)
    def _rett_diff(self):
        lw,lh,gap=420,76,18
        y0=BAR+(H-BAR-lh*3-gap*2)//2; cx=W//2
        return [(cx-lw//2,y0+i*(lh+gap),cx+lw//2,y0+i*(lh+gap)+lh) for i in range(3)]
    def _rett_mosse(self):
        lw_log=int(W*0.72); xi=lw_log+6; lw=W-xi-8; lh=(LOW-16)//4-6
        return [(xi,H-LOW+8+i*(lh+6),xi+lw,H-LOW+8+i*(lh+6)+lh) for i in range(4)]

    def _scrollbar_inizia_drag(self, x, y):
        if self.schermata_corrente!="selezione": return False
        sb_x,sb_y,sb_w,sb_h=self._rett_sb()
        if not (sb_x<=x<=sb_x+sb_w and sb_y<=y<=sb_y+sb_h): return False
        self.sb_dragging=True; return True

    def _scrollbar_drag(self, y):
        if not self.sb_dragging: return
        _,sb_y,_,sb_h=self._rett_sb()
        numero_righe=math.ceil(len(self.lista_pokemon)/GRIGLIA_COLONNE)
        self.scroll_righe=max(0,min(max(1,numero_righe-7),int((y-sb_y)/sb_h*numero_righe)))

    def _cella(self, mx, my):
        if mx<GRIGLIA_ORIG_X or my<GRIGLIA_ORIG_Y: return -1
        c=(mx-GRIGLIA_ORIG_X)//(GRIGLIA_CELLA_W+GRIGLIA_GAP)
        r=(my-GRIGLIA_ORIG_Y)//(GRIGLIA_CELLA_H+GRIGLIA_GAP)
        if not (0<=c<GRIGLIA_COLONNE): return -1
        if mx>GRIGLIA_ORIG_X+c*(GRIGLIA_CELLA_W+GRIGLIA_GAP)+GRIGLIA_CELLA_W: return -1
        if my>GRIGLIA_ORIG_Y+r*(GRIGLIA_CELLA_H+GRIGLIA_GAP)+GRIGLIA_CELLA_H: return -1
        idx=(self.scroll_righe+r)*GRIGLIA_COLONNE+c
        return idx if 0<=idx<len(self.lista_pokemon) else -1

    # -----------------------------------------------------------
    # ELEMENTI COMUNI
    # -----------------------------------------------------------

    def _sfondo(self):
        self.schermo.fill(col(BG))
        if self.schermata_corrente not in ("battaglia","tabellone","campione") and self.tema!="scuro":
            c_g=(180,210,235)
            for x in range(0,W,80): self._linea(x,0,x,H,c_g)
            for y in range(0,H,80): self._linea(0,y,W,y,c_g)

    def _barra_top(self):
        if self.schermata_corrente=="difficolta" and self.tema=="chiaro":
            sfondo_barra = (100,185,255)
        else:
            sfondo_barra = self.bar_top_colore
        self._rett(0,0,W,BAR,sfondo=sfondo_barra)
        self._txt(18,BAR//2,"POKEMON TOURNAMENT",self.font_grassetto,col(ACCENT),"w")

        if self.schermata_corrente=="selezione" and self.difficolta_corrente:
            c_diff={"facile":OK,"media":WARN,"difficile":ERR}.get(self.difficolta_corrente,TXT2)
            self._txt(W//2,BAR//2,self.difficolta_corrente.upper(),self.font_titolo,col(c_diff),"center")

        sub={"tabellone":self.nome_round_att.upper(),
             "battaglia":self.nome_round_batt.upper(),
             "campione":"CAMPIONE!"}.get(self.schermata_corrente,"")
        if sub: self._txt(W-16,BAR//2,sub,self.font_grassetto,col(TXT2),"e")

    # -----------------------------------------------------------
    # SCHERMATA: DIFFICOLTA'
    # -----------------------------------------------------------

    def _disegna_toggle(self):
        x1,y1,x2,y2=self._rett_toggle()
        lw=x2-x1; lh=y2-y1; raggio=lh//2
        e_scuro=(self.tema=="scuro")
        pygame.draw.rect(self.schermo,(15,20,45) if e_scuro else (100,180,240),
                         pygame.Rect(x1,y1,lw,lh),0,border_radius=raggio)
        if e_scuro:
            for sx_,sy_ in [(x1+18,y1+12),(x1+40,y1+30),(x1+28,y1+42),(x1+55,y1+18),(x1+70,y1+38)]:
                pygame.draw.circle(self.schermo,(255,255,255),(sx_,sy_),2)
        else:
            for cx_,cy_,cr in [(x2-65,y1+30,10),(x2-50,y1+24,13),(x2-35,y1+28,10)]:
                pygame.draw.circle(self.schermo,(255,255,255),(cx_,cy_),cr)
        thumb_r=raggio-5
        if e_scuro:
            tx=x2-raggio
            pygame.draw.circle(self.schermo,(210,210,210),(tx,y1+lh//2),thumb_r)
            pygame.draw.circle(self.schermo,(170,170,170),(tx+6,y1+lh//2-6),5)
            pygame.draw.circle(self.schermo,(170,170,170),(tx-4,y1+lh//2+5),3)
        else:
            tx=x1+raggio
            pygame.draw.circle(self.schermo,(255,210,50),(tx,y1+lh//2),thumb_r)
            for ang in range(0,360,45):
                rad=math.radians(ang)
                pygame.draw.line(self.schermo,(255,190,20),
                    (tx+int(math.cos(rad)*(thumb_r+3)),y1+lh//2+int(math.sin(rad)*(thumb_r+3))),
                    (tx+int(math.cos(rad)*(thumb_r+8)),y1+lh//2+int(math.sin(rad)*(thumb_r+8))),2)
        pygame.draw.rect(self.schermo,(50,70,120) if e_scuro else (50,130,190),
                         pygame.Rect(x1,y1,lw,lh),2,border_radius=raggio)
        self._txt(W//2,y2+8,"NOTTE" if e_scuro else "GIORNO",self.font_piccolo,col(TXT2),"n")

    def _disegna_difficolta(self):
        if self.tema=="chiaro":
            for iy in range(BAR,H):
                p=(iy-BAR)/(H-BAR)
                pygame.draw.line(self.schermo,
                    (int(100+(160-100)*p),int(185+(220-185)*p),255),(0,iy),(W,iy))

        if self.tema=="scuro":
            for s in self.stelle_anim:
                lum=int(s["bright"]*(0.6+0.4*math.sin(s["fase"])))
                pygame.draw.circle(self.schermo,(lum,lum,lum),(int(s["x"]),int(s["y"])),s["r"])
            moon=self._carica_stile_cached("moon.png",110,110)
            if moon: self.schermo.blit(moon,(W-270,BAR+20))
            else:
                pygame.draw.circle(self.schermo,(220,220,180),(W-215,BAR+75),55)
                pygame.draw.circle(self.schermo,col(BG),(W-195,BAR+60),42)
        else:
            sun=self._carica_stile_cached("sun.png",130,130)
            if sun: self.schermo.blit(sun,(W-270,BAR+20))
            else:   pygame.draw.circle(self.schermo,(255,220,50),(W-215,BAR+75),52)
            cartella_stile=os.path.join(self.cartella_dati,"style")
            for n in self.nuvole_anim:
                k=n["k"]; nome_cloud=f"cloud{k}.png"
                percorso_cloud=os.path.join(cartella_stile,nome_cloud)
                if not os.path.isfile(percorso_cloud): continue
                chiave_nat=(nome_cloud,"natural")
                if chiave_nat not in self.cache_stile:
                    try:
                        from PIL import Image
                        img_nat=Image.open(percorso_cloud)
                        self.cache_stile[chiave_nat]=(img_nat.width,img_nat.height)
                    except:
                        try:
                            tmp=pygame.image.load(percorso_cloud)
                            self.cache_stile[chiave_nat]=(tmp.get_width(),tmp.get_height())
                        except: self.cache_stile[chiave_nat]=None
                nat=self.cache_stile.get(chiave_nat)
                if nat is None: continue
                cloud=self._carica_stile_cached(nome_cloud,int(nat[0]*1.2),int(nat[1]*1.2))
                if cloud: self.schermo.blit(cloud,(int(n["x"]),int(n["y"])))

        self._txt(W//2,BAR+38,"SCEGLI LA DIFFICOLTA'",self.font_titolo,col(ACCENT),"n")
        ty=BAR+38+self.font_titolo.get_height()+4
        pygame.draw.rect(self.schermo,col(ACCENT),pygame.Rect(W//2-180,ty,360,3))

        nomi=["FACILE","MEDIA","DIFFICILE"]; clist=[OK,WARN,ERR]
        for i,(x1,y1,x2,y2) in enumerate(self._rett_diff()):
            c=clist[i]; cy=(y1+y2)//2; hover=(i==self.hover_difficolta)
            pygame.draw.rect(self.schermo,(0,0,0),pygame.Rect(x1+4,y1+4,x2-x1,y2-y1),0,10)
            pygame.draw.rect(self.schermo,col(c if hover else BG3),pygame.Rect(x1,y1,x2-x1,y2-y1),0,10)
            pygame.draw.rect(self.schermo,col(c),pygame.Rect(x1,y1,x2-x1,y2-y1),3,10)
            nc=BG if hover else c
            self._txt(x1+30,cy,nomi[i],self.font_grande,col(nc),"w")
            self._txt(x2-18,cy,">",self.font_simboli_b,col(nc),"e")

        self._disegna_toggle()

    # -----------------------------------------------------------
    # SCHERMATA: SELEZIONE
    # -----------------------------------------------------------

    def _disegna_selezione(self):
        self._rett(0,BAR,PANNELLO_L_W,H,sfondo=BG2)
        if self.immagine_pannello is not None:
            self.schermo.blit(self.immagine_pannello,(0,BAR))

        if 0<=self.selezionato_indice<len(self.lista_pokemon):
            self._pannello_stats(self.lista_pokemon[self.selezionato_indice])
        else:
            self._txt(PANNELLO_L_W//2,H//2-17,"CLICCA UN",self.font_grassetto,col(TXT2),"center")
            self._txt(PANNELLO_L_W//2,H//2+10,"POKEMON",  self.font_grassetto,col(TXT2),"center")

        # Pulsante INDIETRO
        xb1,yb1,xb2,yb2=self._rett_indietro()
        pygame.draw.rect(self.schermo,(0,0,0),pygame.Rect(xb1+3,yb1+3,xb2-xb1,yb2-yb1),0,4)
        pygame.draw.rect(self.schermo,col(ACCENT),pygame.Rect(xb1,yb1,xb2-xb1,yb2-yb1),0,4)
        self._txt((xb1+xb2)//2,(yb1+yb2)//2,"INDIETRO",self.font_simboli_s,col(BG),"center")

        # Pulsante INIZIA / SCEGLI
        x1,y1,x2,y2=self._rett_inizia()
        if self.selezionato_indice>=0:
            pygame.draw.rect(self.schermo,(0,0,0),pygame.Rect(x1+3,y1+3,x2-x1,y2-y1),0,4)
            pygame.draw.rect(self.schermo,col(ACCENT),pygame.Rect(x1,y1,x2-x1,y2-y1),0,4)
            self._txt((x1+x2)//2,(y1+y2)//2,"INIZIA",self.font_simboli_s,col(BG),"center")
        else:
            pygame.draw.rect(self.schermo,col(BG3),pygame.Rect(x1,y1,x2-x1,y2-y1),0,4)
            self._txt((x1+x2)//2,(y1+y2)//2,"SCEGLI",self.font_simboli_s,col(TXT2),"center")

        if self.immagine_bigpanel is not None:
            self.schermo.blit(self.immagine_bigpanel,(PANNELLO_L_W,BAR))
        self._griglia()
        self._scrollbar()

    def _scrollbar(self):
        numero_righe=math.ceil(len(self.lista_pokemon)/GRIGLIA_COLONNE)
        righe_visibili=7
        if numero_righe<=righe_visibili: return
        sb_x,sb_y,sb_w,sb_h=self._rett_sb()
        pygame.draw.rect(self.schermo,col(BG3),pygame.Rect(sb_x,sb_y,sb_w,sb_h))
        proporzione=righe_visibili/numero_righe
        thumb_h=max(20,int(sb_h*proporzione))
        thumb_y=sb_y+int((sb_h-thumb_h)*(self.scroll_righe/max(1,numero_righe-righe_visibili)))
        pygame.draw.rect(self.schermo,col(ACCENT),pygame.Rect(sb_x,thumb_y,sb_w,thumb_h))

    def _griglia(self):
        for riga in range(8):
            for col_ in range(GRIGLIA_COLONNE):
                idx=(self.scroll_righe+riga)*GRIGLIA_COLONNE+col_
                if idx>=len(self.lista_pokemon): break
                px=GRIGLIA_ORIG_X+col_*(GRIGLIA_CELLA_W+GRIGLIA_GAP)
                py=GRIGLIA_ORIG_Y+riga*(GRIGLIA_CELLA_H+GRIGLIA_GAP)
                if py+GRIGLIA_CELLA_H>H: break
                self._cella_pokemon(self.lista_pokemon[idx],px,py,
                                    idx==self.hover_indice,idx==self.selezionato_indice)

    def _cella_pokemon(self, pokemon, x, y, hover, selezionato):
        tipo=pokemon["tipi"][0] if pokemon["tipi"] else "Normal"
        # hover e selezionato hanno lo stesso stile visivo
        if hover or selezionato:
            if self.tema=="scuro":
                pygame.draw.rect(self.schermo,(0,0,0),  pygame.Rect(x+3,y+3,GRIGLIA_CELLA_W,GRIGLIA_CELLA_H),2)
                pygame.draw.rect(self.schermo,(18,29,47),pygame.Rect(x,y,GRIGLIA_CELLA_W,GRIGLIA_CELLA_H))
                pygame.draw.rect(self.schermo,(255,255,255),pygame.Rect(x,y,GRIGLIA_CELLA_W,GRIGLIA_CELLA_H),2)
            else:
                pygame.draw.rect(self.schermo,(0,0,0),    pygame.Rect(x+3,y+3,GRIGLIA_CELLA_W,GRIGLIA_CELLA_H))
                pygame.draw.rect(self.schermo,(255,255,255),pygame.Rect(x,y,GRIGLIA_CELLA_W,GRIGLIA_CELLA_H))
                pygame.draw.rect(self.schermo,(255,255,255),pygame.Rect(x,y,GRIGLIA_CELLA_W,GRIGLIA_CELLA_H),2)
        elif self.tema=="scuro":
            pygame.draw.rect(self.schermo,(37,61,74),pygame.Rect(x,y,GRIGLIA_CELLA_W,GRIGLIA_CELLA_H))
        else:
            pygame.draw.rect(self.schermo,(192,211,215),pygame.Rect(x,y,GRIGLIA_CELLA_W,GRIGLIA_CELLA_H))

        self._rett(x+2,y+8,x+5,y+GRIGLIA_CELLA_H-8,sfondo=TIPO_COL.get(tipo,TXT2))
        cxs=x+10+SPR_SEL; cys=y+GRIGLIA_CELLA_H//2
        self._sprite_cerchio(pokemon,cxs,cys,SPR_SEL)
        tx=cxs+SPR_SEL+8; ty=y+6
        self._txt(tx,ty,pokemon["nome"][:14],self.font_normale,col(TXT))
        xt=tx; yt=ty+21; xm=x+GRIGLIA_CELLA_W-6
        for t in pokemon["tipi"]:
            tw,th=self.font_piccolo.size(t); lbw=tw+8; lbh=th+4
            if xt+lbw>xm: break
            self._rett_r(xt,yt,xt+lbw,yt+lbh,raggio=4,sfondo=TIPO_COL.get(t,TXT2))
            self._txt(xt+lbw//2,yt+lbh//2,t,self.font_piccolo,col(TXT),"center")
            xt+=lbw+3
        lb=GRIGLIA_CELLA_W-(tx-x)-8; yb=ty+46
        self._barra(tx,yb,lb,5,pokemon["stats"]["hp"],    250,COL_HP);  yb+=8
        self._barra(tx,yb,lb,5,pokemon["stats"]["attack"],200,COL_ATK); yb+=8
        self._barra(tx,yb,lb,5,pokemon["stats"]["speed"], 200,COL_VEL)

    def _pannello_stats(self, pokemon):
        cx=PANNELLO_L_W//2; cy=BAR+20+SPR_PAN
        self._sprite_cerchio(pokemon,cx,cy,SPR_PAN)
        y=cy+SPR_PAN+12
        self._txt(cx,y,pokemon["nome"],self.font_grassetto,col(TXT),"center")
        y+=22; xb=10
        for tipo in pokemon["tipi"]:
            lbw=len(tipo)*7+14
            self._rett_r(xb,y,xb+lbw,y+17,raggio=6,sfondo=TIPO_COL.get(tipo,TXT2))
            self._txt(xb+lbw//2,y+8,tipo,self.font_piccolo,col(TXT),"center")
            xb+=lbw+5
        y+=36; lb=PANNELLO_L_W-24
        for nome,valore,massimo,cb in [
            ("HP", pokemon["stats"]["hp"],         250,COL_HP),
            ("ATK",pokemon["stats"]["attack"],      200,COL_ATK),
            ("DEF",pokemon["stats"]["defense"],     250,COL_DEF),
            ("SpA",pokemon["stats"]["sp_attack"],   194,COL_SPA),
            ("SpD",pokemon["stats"]["sp_defense"],  250,COL_SPD),
            ("VEL",pokemon["stats"]["speed"],       200,COL_VEL),
        ]:
            self._txt(12,y+3,nome,self.font_piccolo,col(TXT2),"w")
            self._txt(PANNELLO_L_W-12,y+3,str(valore),self.font_piccolo,col(TXT),"e")
            y+=15; self._barra(12,y,lb,8,valore,massimo,cb); y+=12

    # -----------------------------------------------------------
    # SCHERMATA: TABELLONE
    # -----------------------------------------------------------

    def _disegna_tabellone(self):
        vuoto = {"a":"","b":"","vincitore":None}
        def round_(n, size):
            r = list(self.bracket_dati[n]) if len(self.bracket_dati) > n else []
            r += [dict(vuoto)] * max(0, size - len(r))
            return r
        r16 = round_(0, 8)
        rqf = round_(1, 4)
        rsf = round_(2, 2)
        rf  = round_(3, 1)

        yi=BRACKET_TOP-22
        for testo,xc,c in [
            ("OTTAVI",(R16_L_X1+R16_L_X2)//2,ACCENT),("QUARTI",(QF_L_X1+QF_L_X2)//2,ACCENT),
            ("SEMIFINALI",(SF_L_X1+SF_L_X2)//2,ACCENT),("FINALE",W//2,GOLD),
            ("SEMIFINALI",(SF_R_X1+SF_R_X2)//2,ACCENT),("QUARTI",(QF_R_X1+QF_R_X2)//2,ACCENT),
            ("OTTAVI",(R16_R_X1+R16_R_X2)//2,ACCENT),
        ]: self._txt(xc,yi,testo,self.font_piccolo,col(c),"n")

        for i in range(4):
            ym=BRACKET_TOP+i*R16_SLOT+(R16_SLOT-BRACKET_BOX_H)//2
            self._box_match(r16[i],  R16_L_X1,ym)
            self._linea(R16_L_X2,ym+BRACKET_BOX_H//2,(R16_L_X2+QF_L_X1)//2,ym+BRACKET_BOX_H//2,BORDER)
            self._box_match(r16[i+4],R16_R_X1,ym)
            self._linea(R16_R_X1,ym+BRACKET_BOX_H//2,(R16_R_X1+QF_R_X2)//2,ym+BRACKET_BOX_H//2,BORDER)

        for i in range(2):
            ym=BRACKET_TOP+i*QF_SLOT+(QF_SLOT-BRACKET_BOX_H)//2
            cy=ym+BRACKET_BOX_H//2
            ya=BRACKET_TOP+(i*2)*R16_SLOT+R16_SLOT//2
            yb_=BRACKET_TOP+(i*2+1)*R16_SLOT+R16_SLOT//2
            xrl=(R16_L_X2+QF_L_X1)//2; xrr=(R16_R_X1+QF_R_X2)//2
            self._box_match(rqf[i],  QF_L_X1,ym)
            self._linea(QF_L_X2,cy,(QF_L_X2+SF_L_X1)//2,cy,BORDER)
            self._linea(xrl,ya,xrl,yb_,BORDER); self._linea(xrl,cy,QF_L_X1,cy,BORDER)
            self._box_match(rqf[i+2],QF_R_X1,ym)
            self._linea(QF_R_X1,cy,(QF_R_X1+SF_R_X2)//2,cy,BORDER)
            self._linea(xrr,ya,xrr,yb_,BORDER); self._linea(QF_R_X2,cy,xrr,cy,BORDER)

        cyl=cyr=SF_Y+BRACKET_BOX_H//2
        self._box_match(rsf[0],SF_L_X1,SF_Y)
        self._linea(SF_L_X2,cyl,(SF_L_X2+FINAL_X1)//2,cyl,BORDER)
        xrl2=(QF_L_X2+SF_L_X1)//2
        self._linea(xrl2,BRACKET_TOP+QF_SLOT//2,xrl2,BRACKET_TOP+QF_SLOT+QF_SLOT//2,BORDER)
        self._linea(xrl2,cyl,SF_L_X1,cyl,BORDER)
        self._box_match(rsf[1],SF_R_X1,SF_Y)
        self._linea(SF_R_X1,cyr,(SF_R_X1+FINAL_X2)//2,cyr,BORDER)
        xrr2=(QF_R_X1+SF_R_X2)//2
        self._linea(xrr2,BRACKET_TOP+QF_SLOT//2,xrr2,BRACKET_TOP+QF_SLOT+QF_SLOT//2,BORDER)
        self._linea(SF_R_X2,cyr,xrr2,cyr,BORDER)

        self._box_match(rf[0],FINAL_X1,SF_Y)
        cf=SF_Y+BRACKET_BOX_H//2
        self._linea((SF_L_X2+FINAL_X1)//2,cf,FINAL_X1,cf,BORDER)
        self._linea(FINAL_X2,cf,(SF_R_X1+FINAL_X2)//2,cf,BORDER)

        if self.mostra_continua:
            if self.messaggio_risultato:
                c_msg=TXT if self.tema=="chiaro" else ACCENT
                self._txt(W//2,H-110,self.messaggio_risultato,self.font_grassetto,col(c_msg),"center")
            self._btn_continua()

    def _box_match(self, match, x, y):
        na=match.get("a","?"); nb=match.get("b","?"); vc=match.get("vincitore")
        ng=self.nome_pokemon_giocatore
        e_gio_box = bool(ng) and (na==ng or nb==ng)
        c_bordo   = VIOLA_PLAYER if e_gio_box else (col(OK) if vc else col(BORDER))

        pygame.draw.rect(self.schermo,(0,0,0),pygame.Rect(x+3,y+3,BRACKET_BOX_W,BRACKET_BOX_H))
        pygame.draw.rect(self.schermo,col(BG2),pygame.Rect(x,y,BRACKET_BOX_W,BRACKET_BOX_H))
        pygame.draw.rect(self.schermo,c_bordo, pygame.Rect(x,y,BRACKET_BOX_W,BRACKET_BOX_H),2)

        def _col_nome(nome):
            if bool(ng) and nome==ng: return VIOLA_PLAYER
            if vc==nome: return col(OK)
            return col(TXT2) if vc else col(TXT)

        meta=BRACKET_BOX_H//2
        self._txt(x+8,y+meta//2,   ("▶ " if vc==na else "  ")+na[:16],self.font_simboli_s,_col_nome(na),"w")
        pygame.draw.rect(self.schermo,col(BORDER),pygame.Rect(x+3,y+meta,BRACKET_BOX_W-6,1))
        self._txt(x+8,y+meta+meta//2,("▶ " if vc==nb else "  ")+nb[:16],self.font_simboli_s,_col_nome(nb),"w")

    # -----------------------------------------------------------
    # SCHERMATA: BATTAGLIA
    # -----------------------------------------------------------

    def _disegna_battaglia(self):
        if self.pokemon_giocatore is None or self.pokemon_avversario is None: return

        if self.wallpaper_corrente is not None:
            self.schermo.blit(self.wallpaper_corrente,(0,BAR))
        else:
            alt=H-LOW-BAR
            for i in range(8):
                p=i/8
                pygame.draw.rect(self.schermo,
                    (int(0x0a+(0x14-0x0a)*p),int(0x0e+(0x1c-0x0e)*p),int(0x1a+(0x35-0x1a)*p)),
                    (0,BAR+int(i*alt/8),W,int(alt/8)+1))

        self._linea(0,H-LOW,W,H-LOW,ACCENT,2)
        self._barre_pokemon(self.pokemon_giocatore,  14,   BAR+8,300,True)
        self._barre_pokemon(self.pokemon_avversario,W-314, BAR+8,300,False)

        sx=self.offset_shake_x; sy=self.offset_shake_y
        for sl in self.speed_lines:
            prog=sl["eta"]/sl["durata"]
            if prog<0.9:
                lx2=int(sl["x1"]+sl["dir_x"]*sl["lunghezza"]*prog*1.5)
                pygame.draw.line(self.schermo,(220,220,255),(int(sl["x1"]),int(sl["y1"])),(lx2,int(sl["y1"])),max(1,int(3*(1-prog))))

        cxg=GX+self.offset_x_giocatore+SPR_B//2+sx
        cyg=GY+SPR_B//2-int(SPR_B*SPR_OFF)+sy
        if self.opacita_giocatore>0:
            self._sprite_battaglia(self.pokemon_giocatore,cxg,cyg,self.opacita_giocatore,specchiato=True)

        cxa=AX+self.offset_x_avversario+SPR_B//2+sx
        cya=AY+SPR_B//2-int(SPR_B*SPR_OFF)+sy
        if self.opacita_avversario>0:
            self._sprite_battaglia(self.pokemon_avversario,cxa,cya,self.opacita_avversario)

        for o in self.onde_impatto:
            if o["raggio"]>0:
                prog=o["eta"]/o["durata"]
                if int(o["alpha"]*(1-prog))>10:
                    cxt=(cxg if o["chi_bersaglio"]=="giocatore" else cxa)
                    cyt=(cyg if o["chi_bersaglio"]=="giocatore" else cya)+int(SPR_B*0.1)
                    r,g,b=o["colore"]
                    fade=lambda v: min(255,v+int((255-v)*prog*0.5))
                    pygame.draw.circle(self.schermo,(fade(r),fade(g),fade(b)),
                        (int(cxt),int(cyt)),o["raggio"],max(1,int(4*(1-prog))))

        for p in self.particelle_speciali:
            prog=p["eta"]/p["durata"]; ra=max(1,int(p["raggio"]*(1-prog*0.6)))
            if prog<0.92:
                pygame.draw.circle(self.schermo,p["colore"],(int(p["x"]),int(p["y"])),ra)
                if ra>=3: pygame.draw.circle(self.schermo,(255,255,255),(int(p["x"]),int(p["y"])),max(1,ra//3))

        for p in self.particelle_impatto:
            prog=p["eta"]/p["durata"]; ra=max(1,int(p["raggio"]*(1-prog)))
            r,g,b=p["colore"]
            fade=lambda v: min(255,v+int((255-v)*prog*0.6))
            pygame.draw.circle(self.schermo,(fade(r),fade(g),fade(b)),(int(p["x"]),int(p["y"])),ra)

        for b in self.bolle_cura:
            if b["eta"]>0 and b["eta"]/b["durata"]<0.95:
                r,g,bv=b["colore"]
                pygame.draw.circle(self.schermo,(r,g,bv),(int(b["x"]),int(b["y"])),b["raggio"],2)
                pygame.draw.circle(self.schermo,(255,255,255),
                    (int(b["x"]-b["raggio"]*0.3),int(b["y"]-b["raggio"]*0.3)),max(1,b["raggio"]//4))

        lw_log=int(W*0.72)
        self._rett(0,H-LOW,lw_log,H,sfondo=BG2)
        self._rett(lw_log,H-LOW,W,H,sfondo=BG)
        self._rett_r(8,H-LOW+8,lw_log-8,H-8,raggio=10,sfondo=BG,bordo=BORDER)

        y_log=H-LOW+14; alt_r=(H-16-y_log)//LOG_N
        for i,(testo,cm) in enumerate(self.log_battaglia[-LOG_N:]):
            self._txt(16,y_log+i*alt_r,testo[:88],self.font_log,col(cm) if cm else col(TXT))

        nomi_btn=["ATTACCO","ATT. SPECIALE","POZIONE","POZ. SPECIALE"]
        col_btn=[COL_ATK,COL_SPA,COL_HP,COL_SPD]
        det_btn=["ATK:"+str(self.pokemon_giocatore["stats"]["attack"]),
                 "SpA:"+str(self.pokemon_giocatore["stats"]["sp_attack"]),
                 "x"+str(self.pozioni_norm),"x"+str(self.pozioni_spec)]
        dis=[False,False,self.pozioni_norm<=0,self.pozioni_spec<=0]
        for i,(x1,y1,x2,y2) in enumerate(self._rett_mosse()):
            cm=col_btn[i]; eh=(self.hover_mossa==i and self.e_turno_mio and not dis[i])
            if   dis[i]:          csf,cbr,ct,cd = BG3,BORDER,TXT2,TXT2
            elif eh:              csf,cbr,ct,cd = cm,cm,BG,BG
            elif self.e_turno_mio:csf,cbr,ct,cd = BG2,cm,cm,TXT2
            else:                 csf,cbr,ct,cd = BG3,BORDER,TXT2,TXT2
            self._rett_r(x1,y1,x2,y2,raggio=8,sfondo=csf,bordo=cbr,sp=2)
            cy_=(y1+y2)//2
            self._txt(x1+10,cy_-8,nomi_btn[i],self.font_normale,col(ct),"w")
            self._txt(x1+10,cy_+8,det_btn[i], self.font_piccolo,col(cd),"w")

        for n in self.numeri_fluttuanti:
            prog=n["eta"]/n["durata"]; cs=n["colore"]
            try:
                rv=int(cs[1:3],16); gv=int(cs[3:5],16); bv=int(cs[5:7],16)
                cf_=(max(0,min(255,int(rv*(1-prog)+0x0a*prog))),
                     max(0,min(255,int(gv*(1-prog)+0x0e*prog))),
                     max(0,min(255,int(bv*(1-prog)+0x1a*prog))))
            except: cf_=col(cs)
            self._txt(int(n["x"]),int(n["y"]),n["testo"],self.font_titolo,cf_,"center")

        if self.mostra_continua and self.animazione_ko is None:
            self._overlay()
            if self.messaggio_risultato:
                self._txt(W//2,H//2-60,self.messaggio_risultato,self.font_grassetto,(255,255,255),"center")
            self._btn_continua()

    def _barre_pokemon(self, pokemon, x, y0, lw, e_giocatore):
        self._txt(x,y0,pokemon["nome"],self.font_grassetto,col(ACCENT if e_giocatore else ACCENT2))
        y=y0+36
        for nome,valore,massimo,cb in [
            ("HP", pokemon["hp_attuale"],       pokemon["stats"]["hp"],         COL_HP),
            ("DEF",pokemon["difesa_attuale"],    pokemon["stats"]["defense"],    COL_DEF),
            ("SpD",pokemon["sp_difesa_attuale"], pokemon["stats"]["sp_defense"], COL_SPD),
        ]:
            self._txt(x,y+1,nome,self.font_piccolo,col(TXT2))
            xb=x+34; lwb=lw-80
            r_=pygame.Rect(xb,y,lwb,10)
            pygame.draw.rect(self.schermo,col(self.barra_bg_colore),r_,0,border_radius=5)
            pygame.draw.rect(self.schermo,col(BORDER),r_,1,border_radius=5)
            if massimo>0:
                pieni=max(0,int(lwb*min(valore,massimo)/massimo))
                if pieni>0:
                    pygame.draw.rect(self.schermo,col(cb),pygame.Rect(xb,y,pieni,10),0,border_radius=5)
            self._txt(x+lw,y+1,f"{int(valore)}/{massimo}",self.font_piccolo,col(TXT),"ne")
            y+=16

    # -----------------------------------------------------------
    # SCHERMATA: CAMPIONE
    # -----------------------------------------------------------

    def _disegna_campione(self):
        pk = self.pokemon_campione

        # Sfondo gradiente scuro
        for iy in range(H):
            p = iy / H
            r = int(10  + (30  - 10)  * p)
            g = int(8   + (18  - 8)   * p)
            b = int(20  + (50  - 20)  * p)
            pygame.draw.line(self.schermo, (r, g, b), (0, iy), (W, iy))

        # Raggi dorati dal centro
        cx_ray = W // 2
        cy_ray = H // 2 - 30
        n_raggi = 24
        for i in range(n_raggi):
            a = i * (2 * math.pi / n_raggi)
            colore_raggio = (255, 215, 0) if i % 2 == 0 else (255, 180, 0)
            pygame.draw.line(self.schermo, colore_raggio,
                             (cx_ray, cy_ray),
                             (cx_ray + int(math.cos(a) * 700),
                              cy_ray + int(math.sin(a) * 700)), 1)

        # Cerchio dorato sotto lo sprite
        pygame.draw.circle(self.schermo, (50, 40, 0),    (cx_ray, cy_ray), 202)
        pygame.draw.circle(self.schermo, (255, 215, 0),  (cx_ray, cy_ray), 200, 4)
        pygame.draw.circle(self.schermo, (255, 240, 100),(cx_ray, cy_ray), 185, 1)

        # Sprite del Pokemon campione
        SPR_C = 340
        if pk is not None:
            img = self._carica_immagine(pk["nome"], SPR_C)
            if img:
                self.schermo.blit(img, (cx_ray - SPR_C // 2, cy_ray - SPR_C // 2 - 60))
            else:
                tipo0 = pk["tipi"][0] if pk["tipi"] else "Normal"
                self._txt(cx_ray, cy_ray - 20,
                          pk["nome"][0].upper(),
                          self.font_grande, col(TIPO_COL.get(tipo0, TXT2)), "center")

        # Titolo CAMPIONE DEL TORNEO
        titolo_y = BAR + 28
        self._txt(W // 2 + 3, titolo_y + 3, "CAMPIONE DEL TORNEO",
                  self.font_simboli_xl, (0, 0, 0), "n")
        self._txt(W // 2, titolo_y, "CAMPIONE DEL TORNEO",
                  self.font_simboli_xl, col(GOLD), "n")

        # Nome del Pokemon — dentro il cerchio dorato, in basso
        if pk is not None:
            nome_y = cy_ray + 105
            self._txt(W // 2 + 2, nome_y + 2, pk["nome"],
                      self.font_grande, (0, 0, 0), "center")
            self._txt(W // 2, nome_y, pk["nome"],
                      self.font_grande, (255, 255, 255), "center")

        if self.mostra_continua:
            self._btn_continua("[ GIOCA ANCORA ]")
