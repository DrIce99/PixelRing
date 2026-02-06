import pygame
from core.config import *
from core.engine import Mappa
from editor.editor import Editor

def main():
    pygame.init()
    screen_real = pygame.display.set_mode(RES_FINESTRA)
    canvas_logica = pygame.Surface(RES_LOGICA)
    clock = pygame.time.Clock()
    
    mappa = Mappa()
    editor = Editor()
    
    while True:
        m_pos_real = pygame.mouse.get_pos()
        # Calcolo posizione relativa alla canvas (escludendo UI)
        m_pos_logica = editor.trasforma_pos(m_pos_real)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            
            # ZOOM: Funziona sempre, basta che il mouse sia sulla mappa
            if event.type == pygame.MOUSEWHEEL:
                editor.gestisci_zoom(event, m_pos_real)
                mappa.cache_texture = {} # Invalida cache per rigenerare noise alla nuova scala
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 1. GESTIONE PAN (Tasti 2 o 3)
                if event.button in [2, 3]:
                    editor.is_panning = True
                    pygame.mouse.get_rel()
                
                # 2. CLICK UI (Tasto 1)
                elif event.button == 1:
                    if m_pos_real[0] < SIDEBAR_WIDTH: 
                        idx = (m_pos_real[1] - 40) // 50 + 1
                        if idx in TIPI_SUPERFICIE: editor.tipo_corrente = idx
                    
                    elif m_pos_real[1] < TOPBAR_HEIGHT: 
                        start_x = SIDEBAR_WIDTH + 20
                        if start_x <= m_pos_real[0] <= start_x + 60: editor.mode = "ADD"
                        elif start_x + 80 <= m_pos_real[0] <= start_x + 140: editor.mode = "EDIT"
                        elif start_x + 160 <= m_pos_real[0] <= start_x + 220: editor.mode = "DELETE"
                        elif start_x + 240 <= m_pos_real[0] <= start_x + 300: editor.mode = "PAN"
                        elif start_x + 320 <= m_pos_real[0] <= start_x + 380: editor.mode = "FILL"
                        elif start_x + 400 <= m_pos_real[0] <= start_x + 480: editor.mode = "COLLISION"
                    
                    # 3. CLICK MAPPA (Solo se siamo in modalità disegno e non PAN)
                    elif editor.mode != "PAN":
                        editor.gestisci_click(m_pos_logica, mappa)
                    
                    if not (m_pos_real[0] < SIDEBAR_WIDTH or m_pos_real[1] < TOPBAR_HEIGHT):
                        if editor.mode == "COLLISION":
                            # QUI avviene l'azione, solo al click!
                            if editor.segmento_selezionato:
                                a_idx, p1, p2 = editor.segmento_selezionato
                                area = mappa.aree[a_idx]
                                if "segmenti_solidi" not in area: area["segmenti_solidi"] = []
                                
                                seg = [p1, p2]
                                # Toggle del segmento
                                if seg in area["segmenti_solidi"] or [p2, p1] in area["segmenti_solidi"]:
                                    if seg in area["segmenti_solidi"]: area["segmenti_solidi"].remove(seg)
                                    else: area["segmenti_solidi"].remove([p2, p1])
                                else:
                                    area["segmenti_solidi"].append(seg)
                                mappa.salva_mappa()
                                
                            elif editor.area_selezionata_del is not None:
                                area = mappa.aree[editor.area_selezionata_del]
                                area["collisione_totale"] = not area.get("collisione_totale", False)
                                mappa.salva_mappa()
                        else:
                            # Altre modalità (ADD, EDIT, ecc)
                            editor.gestisci_click(m_pos_logica, mappa)
            
            if editor.mode == "COLLISION":
                editor.gestisci_collisione(m_pos_logica, mappa)
            
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button in [1, 2, 3]:
                    editor.is_panning = False
                    
            if event.type == pygame.MOUSEBUTTONUP:
                editor.punto_trascinato = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: editor.crea_area(mappa)
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    editor.tipo_corrente = int(event.unicode)

        editor.update_edit(m_pos_logica, mappa)
        editor.update_pan()
        editor.aggiorna_cursore()
        
        canvas_logica.fill((20, 20, 25))
        
        editor.area_selezionata_del = None
        if editor.mode in ["DELETE", "FILL"]:
            for i, area in enumerate(mappa.aree):
                poly = [mappa.punti_globali[p] for p in area["punti"]]
                if len(poly) >= 3 and editor._point_in_poly(m_pos_logica, poly):
                    editor.area_selezionata_del = i
                    break
            
        if editor.mode == "COLLISION":
            editor.gestisci_collisione(m_pos_logica, mappa)
            
        mappa.render(canvas_logica, editor)
        
        screen_real.fill((0,0,0))
        # Rendering della canvas logica nell'area rimanente
        canvas_scalata = pygame.transform.scale(canvas_logica, (RES_FINESTRA[0]-SIDEBAR_WIDTH, RES_FINESTRA[1]-TOPBAR_HEIGHT))
        screen_real.blit(canvas_scalata, (SIDEBAR_WIDTH, TOPBAR_HEIGHT))
        
        editor.draw_ui(screen_real)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__": main()