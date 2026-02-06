import pygame, random, json, os
from core.config import RES_LOGICA, TIPI_SUPERFICIE, FILE_MAPPA

class Mappa:
    def __init__(self):
        self.punti_globali = []
        self.aree = []
        self.cache_texture = {}
        self.carica_mappa()

    def genera_noise_avanzato(self, surface, tipo):
        cols = TIPI_SUPERFICIE[tipo]["colori"]
        for x in range(0, surface.get_width(), 2):
            for y in range(0, surface.get_height(), 2):
                pygame.draw.rect(surface, random.choice(cols), (x, y, 2, 2))

    def render(self, dest_surf, editor):
        mostra_debug = getattr(editor, "mode", "GAME") != "GAME"
        
        for i, area in enumerate(self.aree):
            # Trasformazione punti (Offset + Zoom)
            pts = [((pygame.Vector2(self.punti_globali[idx]) + editor.camera_offset) * editor.zoom_level) 
                for idx in area["punti"]]
            
            if len(pts) < 3: continue

            # --- 1. DISEGNO SUPERFICIE ---
            area_id = (tuple(area["punti"]), area["tipo"])
            if area_id not in self.cache_texture:
                # Creiamo una texture tileable (es. 128x128)
                t_surf = pygame.Surface((128, 128))
                t_surf.fill(TIPI_SUPERFICIE[area["tipo"]]["colori"][0])
                self.genera_noise_avanzato(t_surf, area["tipo"])
                self.cache_texture[area_id] = t_surf

            # Creiamo la maschera della forma del poligono
            poly_mask = pygame.Surface(RES_LOGICA, pygame.SRCALPHA)
            pygame.draw.polygon(poly_mask, (255, 255, 255, 255), pts)

            # --- IL TRUCCO DEL TILING ---
            # Calcoliamo l'offset infinito per la texture
            # Usiamo il modulo (%) per farla ripetere senza mai "finire"
            off_x = (editor.camera_offset.x * editor.zoom_level) % 128
            off_y = (editor.camera_offset.y * editor.zoom_level) % 128
            
            # Creiamo una superficie d'appoggio grande abbastanza da coprire lo schermo + il tiling
            temp_tex_bg = pygame.Surface((RES_LOGICA[0] + 128, RES_LOGICA[1] + 128))
            for tx in range(0, RES_LOGICA[0] + 128, 128):
                for ty in range(0, RES_LOGICA[1] + 128, 128):
                    temp_tex_bg.blit(self.cache_texture[area_id], (tx, ty))
            
            # Applichiamo la texture "shifttata" alla maschera del poligono
            poly_mask.blit(temp_tex_bg, (off_x - 128, off_y - 128), special_flags=pygame.BLEND_RGBA_MIN)
            
            dest_surf.blit(poly_mask, (0, 0))

            # --- 2. DISEGNO COLLISIONI ATTIVE ---
            # Se l'area è tutta solida, bordo rosso sottile
            if mostra_debug:
                if area.get("collisione_totale", False):
                    pygame.draw.polygon(dest_surf, (200, 0, 0), pts, 1)

                # Se ci sono segmenti solidi specifici
                for seg in area.get("segmenti_solidi", []):
                    # seg è una lista di due indici [idx1, idx2]
                    p1 = (pygame.Vector2(self.punti_globali[seg[0]]) + editor.camera_offset) * editor.zoom_level
                    p2 = (pygame.Vector2(self.punti_globali[seg[1]]) + editor.camera_offset) * editor.zoom_level
                    pygame.draw.line(dest_surf, (25, 20, 255), p1, p2, 2)

            # --- 3. FEEDBACK VISIVO EDITING ---
            if editor.mode == "COLLISION":
                if i == editor.area_selezionata_del: # Hover Area
                    overlay = pygame.Surface(RES_LOGICA, pygame.SRCALPHA)
                    pygame.draw.polygon(overlay, (25, 20, 255, 80), pts)
                    dest_surf.blit(overlay, (0,0))
                
                if editor.segmento_selezionato and editor.segmento_selezionato[0] == i:
                    s = editor.segmento_selezionato
                    p1 = (pygame.Vector2(self.punti_globali[s[1]]) + editor.camera_offset) * editor.zoom_level
                    p2 = (pygame.Vector2(self.punti_globali[s[2]]) + editor.camera_offset) * editor.zoom_level
                    pygame.draw.line(dest_surf, (255, 255, 255), p1, p2, 2)

        # --- 4. DISEGNO NUVOLA PUNTI ---
        if mostra_debug:
            for i, p in enumerate(self.punti_globali):
                pos_vett = (pygame.Vector2(p) + editor.camera_offset) * editor.zoom_level
                
                # Feedback visivo per i punti selezionati nell'editor
                punti_sel = getattr(editor, "punti_selezionati", [])
                col = (255, 255, 0) if i in punti_sel else (200, 200, 200)
                
                raggio = max(1, int(2 * editor.zoom_level))
                pygame.draw.circle(dest_surf, col, pos_vett, raggio)


    def salva_mappa(self):
        punti_serializzabili = [(float(p[0]), float(p[1])) for p in self.punti_globali]
        with open(FILE_MAPPA, "w") as f:
            json.dump({"punti": punti_serializzabili, "aree": self.aree}, f, indent=2)

    def carica_mappa(self):
        if os.path.exists(FILE_MAPPA):
            with open(FILE_MAPPA, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("JSON corrotto, reset mappa")
                    return
                
                self.punti_globali = [tuple(p) for p in data.get("punti", [])]
                self.aree = data.get("aree", [])

    def pulisci_punti_inutilizzati(self):
        # 1. Trova quali indici sono ancora usati da almeno un'area
        indici_usati = set()
        for area in self.aree:
            for idx in area["punti"]:
                indici_usati.add(idx)
        
        # 2. Crea una nuova lista di punti solo con quelli usati
        nuovi_punti = []
        mappa_indici = {} # Vecchio indice -> Nuovo indice
        
        for vecchio_idx, punto in enumerate(self.punti_globali):
            if vecchio_idx in indici_usati:
                mappa_indici[vecchio_idx] = len(nuovi_punti)
                nuovi_punti.append(punto)
        
        # 3. Aggiorna i riferimenti nelle aree esistenti
        for area in self.aree:
            area["punti"] = [mappa_indici[idx] for idx in area["punti"]]
            
        # 4. Sostituisci la lista globale
        self.punti_globali = nuovi_punti
        self.salva_mappa()