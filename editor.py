import pygame
from config import *

class Editor:
    def __init__(self):
        self.punti_selezionati = []
        self.tipo_corrente = 1
        self.mode = "ADD" # ADD, EDIT, DELETE
        self.punto_trascinato = None

    def gestisci_click(self, pos, mappa):
        if self.mode == "ADD":
            idx = self._get_vicino(pos, mappa)
            if idx is None:
                mappa.punti_globali.append(pos)
                idx = len(mappa.punti_globali) - 1
            if idx not in self.punti_selezionati: self.punti_selezionati.append(idx)
            
        elif self.mode == "EDIT":
            self.punto_trascinato = self._get_vicino(pos, mappa)
            
        elif self.mode == "DELETE":
            for i, area in enumerate(mappa.aree):
                poly = [mappa.punti_globali[p] for p in area["punti"]]
                if self._point_in_poly(pos, poly):
                    mappa.aree.pop(i)
                    mappa.cache_texture = {} # Invalida la cache grafica
                    # PULIZIA PUNTI ORFANI
                    mappa.pulisci_punti_inutilizzati() 
                    break


    def _get_vicino(self, pos, mappa):
        for i, p in enumerate(mappa.punti_globali):
            if pygame.Vector2(p).distance_to(pos) < 5: return i
        return None

    def _point_in_poly(self, pos, poly):
        # Semplice collisione punto-poligono
        p = pygame.mask.from_surface(pygame.Surface(RES_LOGICA, pygame.SRCALPHA))
        surf = pygame.Surface(RES_LOGICA, pygame.SRCALPHA)
        pygame.draw.polygon(surf, (255,255,255), poly)
        mask = pygame.mask.from_surface(surf)
        return mask.get_at(pos)

    def update_edit(self, pos, mappa):
        if self.mode == "EDIT" and self.punto_trascinato is not None:
            mappa.punti_globali[self.punto_trascinato] = pos
            mappa.cache_texture = {} # Invalida cache per aggiornare forme

    def crea_area(self, mappa):
        if len(self.punti_selezionati) >= 3:
            mappa.aree.append({"punti": list(self.punti_selezionati), "tipo": self.tipo_corrente, "z": 0})
            self.punti_selezionati = []
            mappa.salva_mappa()

    def draw_ui(self, screen):
        # Sidebar Materiali
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, SIDEBAR_WIDTH, RES_FINESTRA[1]))
        for i, (tid, cfg) in enumerate(TIPI_SUPERFICIE.items()):
            col = cfg["colori"][0]
            rect = pygame.Rect(10, 40 + i*50, 40, 40)
            pygame.draw.rect(screen, col, rect)
            if self.tipo_corrente == tid: pygame.draw.rect(screen, (255,255,255), rect, 2)
        
        # Topbar Modalità
        pygame.draw.rect(screen, (30, 30, 30), (0, 0, RES_FINESTRA[0], TOPBAR_HEIGHT))
        font = pygame.font.SysFont("Arial", 14)
        for i, m in enumerate(["ADD", "EDIT", "DELETE"]):
            col = (255, 255, 0) if self.mode == m else (200, 200, 200)
            txt = font.render(m, True, col)
            screen.blit(txt, (SIDEBAR_WIDTH + 20 + i*80, 5))

    