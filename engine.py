import pygame, random, json, os
from config import RES_LOGICA, TIPI_SUPERFICIE, FILE_MAPPA

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
        for i, area in enumerate(self.aree):
            pts = [((pygame.Vector2(self.punti_globali[idx]) + editor.camera_offset) * editor.zoom_level) 
                   for idx in area["punti"]]
            
            if len(pts) < 3: continue

            # --- GESTIONE TEXTURE CACHE ---
            area_id = (tuple(area["punti"]), area["tipo"])
            if area_id not in self.cache_texture:
                # Creiamo una texture "grande" quanto la mappa logica per quel poligono
                t_surf = pygame.Surface(RES_LOGICA)
                t_surf.fill(TIPI_SUPERFICIE[area["tipo"]]["colori"][0])
                self.genera_noise_avanzato(t_surf, area["tipo"])
                self.cache_texture[area_id] = t_surf

            # --- DISEGNO CON MASCHERA E ZOOM ---
            # Creiamo una superficie temporanea per il poligono trasformato
            # (Deve essere grande quanto la finestra logica)
            poly_mask = pygame.Surface(RES_LOGICA, pygame.SRCALPHA)
            pygame.draw.polygon(poly_mask, (255, 255, 255), pts)
            
            # Blittiamo la texture (usando il pan/zoom come offset se vogliamo texture fisse)
            # Per ora la scaliamo per adattarla al poligono
            temp_texture = pygame.transform.scale(self.cache_texture[area_id], RES_LOGICA)
            poly_mask.blit(temp_texture, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
            
            dest_surf.blit(poly_mask, (0,0))

            # Evidenziazione Delete
            if i == editor.area_selezionata_del:
                pygame.draw.polygon(dest_surf, (255, 0, 0), pts, 2)
            if i == editor.area_selezionata_del and editor.mode == "FILL":
                pygame.draw.polygon(dest_surf, (0, 200, 255), pts, 2)

        # 3. Disegno dei Punti (nuvola globale)
        for i, p in enumerate(self.punti_globali):
            pos_vett = (pygame.Vector2(p) + editor.camera_offset) * editor.zoom_level
            col = (255, 255, 0) if i in editor.punti_selezionati else (200, 200, 200)
            pygame.draw.circle(dest_surf, col, pos_vett, max(2, int(2 * editor.zoom_level)))

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