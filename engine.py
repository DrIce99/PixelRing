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

    def render(self, dest_surf, punti_sel=[], area_sel=None):
        for i, area in enumerate(self.aree):
            pts = [self.punti_globali[idx] for idx in area["punti"]]
            area_id = (tuple(area["punti"]), area["tipo"])
            
            if area_id not in self.cache_texture:
                t_surf = pygame.Surface(RES_LOGICA)
                t_surf.fill(TIPI_SUPERFICIE[area["tipo"]]["colori"][0])
                self.genera_noise_avanzato(t_surf, area["tipo"])
                self.cache_texture[area_id] = t_surf

            poly_mask = pygame.Surface(RES_LOGICA, pygame.SRCALPHA)
            pygame.draw.polygon(poly_mask, (255, 255, 255), pts)
            poly_mask.blit(self.cache_texture[area_id], (0,0), special_flags=pygame.BLEND_RGBA_MIN)
            
            # Evidenzia se selezionata per delete
            if i == area_sel: pygame.draw.polygon(poly_mask, (255, 0, 0, 100), pts)
            dest_surf.blit(poly_mask, (0,0))
            
        for i, p in enumerate(self.punti_globali):
            col = (255, 255, 0) if i in punti_sel else (200, 200, 200)
            pygame.draw.circle(dest_surf, col, p, 2)

    def salva_mappa(self):
        with open(FILE_MAPPA, "w") as f:
            json.dump({"punti": self.punti_globali, "aree": self.aree}, f)

    def carica_mappa(self):
        if os.path.exists(FILE_MAPPA):
            with open(FILE_MAPPA, "r") as f:
                data = json.load(f)
                self.punti_globali = [tuple(p) for p in data["punti"]]
                self.aree = data["aree"]

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