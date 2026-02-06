import pygame
from config import *

class Editor:
    def __init__(self):
        self.mode = "ADD"
        self.punti_selezionati = []
        self.tipo_corrente = 1
        self.punto_trascinato = None
        self.area_selezionata_del = None
        
        # Camera State
        self.camera_offset = pygame.Vector2(0, 0)
        self.zoom_level = 1.0
        self.is_panning = False

    def aggiorna_cursore(self):
        if self.mode in ["ADD", "EDIT"]:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        elif self.mode == "DELETE":
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif self.mode == "PAN":
            if self.is_panning:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND) # In pygame-ce si può usare cursore personalizzato
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    def trasforma_pos(self, m_pos_real):
        # 1. Sottrai l'origine della zona di disegno (Topbar e Sidebar)
        # m_pos_real è la coordinata della finestra intera (es. 1280x720)
        p_finestra = pygame.Vector2(m_pos_real[0] - SIDEBAR_WIDTH, m_pos_real[1] - TOPBAR_HEIGHT)
        
        # 2. Rapporto tra risoluzione logica e area di disegno reale
        area_disegno_w = RES_FINESTRA[0] - SIDEBAR_WIDTH
        area_disegno_h = RES_FINESTRA[1] - TOPBAR_HEIGHT
        
        # 3. Trasforma in coordinate "canvas" (0-320, 0-180)
        p_canvas = pygame.Vector2(
            p_finestra.x * RES_LOGICA[0] / area_disegno_w,
            p_finestra.y * RES_LOGICA[1] / area_disegno_h
        )
        
        # 4. Inverti Zoom e Pan per ottenere le coordinate del MONDO
        return (p_canvas / self.zoom_level) - self.camera_offset

    def gestisci_zoom(self, event, m_pos_real):
        if event.type == pygame.MOUSEWHEEL:
            # 1. Salva la posizione del mouse nel mondo PRIMA dello zoom
            pos_mondo_pre = self.trasforma_pos(m_pos_real)
            
            # 2. Applica lo zoom
            vecchio_zoom = self.zoom_level
            self.zoom_level = max(ZOOM_MIN, min(ZOOM_MAX, self.zoom_level + event.y * 0.1))
            
            # 3. Calcola la differenza e compensa l'offset
            # Questo sposta la camera in modo che il punto sotto il mouse resti lo stesso
            if vecchio_zoom != self.zoom_level:
                # Calcoliamo dove finirebbe il mouse nel mondo dopo lo zoom
                pos_mondo_post = self.trasforma_pos(m_pos_real)
                # Spostiamo la camera della differenza per "riancorare" il punto
                self.camera_offset += (pos_mondo_post - pos_mondo_pre)

    def update_pan(self):
        # Rimuoviamo il controllo if self.mode == "PAN" se vuoi che 
        # il pan funzioni SEMPRE (magari col tasto destro o centrale)
        if self.is_panning:
            rel_x, rel_y = pygame.mouse.get_rel()
            # Dividiamo per lo zoom: se siamo molto zoomati, 
            # il pan deve essere più lento/preciso
            self.camera_offset.x += rel_x / self.zoom_level
            self.camera_offset.y += rel_y / self.zoom_level
        else:
            pygame.mouse.get_rel() # Consuma il movimento

    def gestisci_click(self, pos, mappa):
        if self.mode == "ADD":
            idx = self._get_vicino(pos, mappa)
            if idx is None:
                mappa.punti_globali.append((float(pos.x), float(pos.y)))
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
        
        elif self.mode == "FILL":
            # 1. Prova a fillare area esistente
            for area in mappa.aree:
                poly = [mappa.punti_globali[p] for p in area["punti"]]
                if len(poly) >= 3 and self._point_in_poly(pos, poly):
                    area["tipo"] = self.tipo_corrente
                    mappa.cache_texture = {}
                    mappa.salva_mappa()
                    return

            # 2. Nessuna area trovata → prova a creare nuova area chiusa
            nuovo_poligono = self._trova_area_chiusa_da_vuoto(pos, mappa)

            if nuovo_poligono and len(nuovo_poligono) >= 3:
                indici = []
                for p in nuovo_poligono:
                    mappa.punti_globali.append((float(p[0]), float(p[1])))
                    indici.append(len(mappa.punti_globali) - 1)

                mappa.aree.append({
                    "punti": indici,
                    "tipo": self.tipo_corrente,
                    "z": 0
                })

                mappa.cache_texture = {}
                mappa.salva_mappa()


    def _get_vicino(self, pos, mappa):
        for i, p in enumerate(mappa.punti_globali):
            if pygame.Vector2(p).distance_to(pos) < 5 / self.zoom_level: return i
        return None

    def _point_in_poly(self, pos, poly):
        x, y = pos
        inside = False
        n = len(poly)
        
        px1, py1 = poly[0]
        for i in range(n + 1):
            px2, py2 = poly[i % n]
            if y > min(py1, py2):
                if y <= max(py1, py2):
                    if x <= max(px1, px2):
                        if py1 != py2:
                            xinters = (y - py1) * (px2 - px1) / (py2 - py1) + px1
                        if px1 == px2 or x <= xinters:
                            inside = not inside
            px1, py1 = px2, py2
        
        return inside

    def update_edit(self, pos, mappa):
        if self.mode == "EDIT" and self.punto_trascinato is not None:
            mappa.punti_globali[self.punto_trascinato] = (float(pos.x), float(pos.y))
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
        for i, m in enumerate(["ADD", "EDIT", "DELETE", "PAN", "FILL"]):
            col = (255, 255, 0) if self.mode == m else (200, 200, 200)
            txt = font.render(m, True, col)
            # Spaziatura: SIDEBAR + 20px di margine + 80px per ogni pulsante
            screen.blit(txt, (SIDEBAR_WIDTH + 20 + i*80, 5))

    