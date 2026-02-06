import pygame
from config import *
from engine import Mappa
from editor import Editor

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
                if event.button in [2, 3] or (editor.mode == "PAN" and event.button == 1):
                    editor.is_panning = True
                    pygame.mouse.get_rel()
                if m_pos_real[0] < SIDEBAR_WIDTH: 
                    # Click Sidebar (Materiali)
                    idx = (m_pos_real[1] - 40) // 50 + 1
                    if idx in TIPI_SUPERFICIE: editor.tipo_corrente = idx
                
                elif m_pos_real[1] < TOPBAR_HEIGHT: 
                    # Click Topbar (Modalità)
                    # Definiamo le aree cliccabili per ogni pulsante
                    start_x = SIDEBAR_WIDTH + 20
                    if start_x <= m_pos_real[0] <= start_x + 60: editor.mode = "ADD"
                    elif start_x + 80 <= m_pos_real[0] <= start_x + 140: editor.mode = "EDIT"
                    elif start_x + 160 <= m_pos_real[0] <= start_x + 220: editor.mode = "DELETE"
                    elif start_x + 240 <= m_pos_real[0] <= start_x + 300: editor.mode = "PAN"
                    elif start_x + 320 <= m_pos_real[0] <= start_x + 380: editor.mode = "FILL"
                
                else:
                    # Click sulla mappa (Logica dell'editor)
                    editor.gestisci_click(m_pos_logica, mappa)
            
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
        
        if editor.mode == "DELETE":
            # Controlla quale area si trova sotto il mouse
            editor.area_selezionata_del = None
            for i, area in enumerate(mappa.aree):
                poly = [mappa.punti_globali[p] for p in area["punti"]]
                # Ricorda di usare m_pos_logica che tiene conto di Pan e Zoom
                if editor._point_in_poly(m_pos_logica, poly):
                    editor.area_selezionata_del = i
                    break
        else:
            editor.area_selezionata_del = None

        if editor.mode == "FILL":
            editor.area_selezionata_del = None
            for i, area in enumerate(mappa.aree):
                poly = [mappa.punti_globali[p] for p in area["punti"]]
                if len(poly) >= 3 and editor._point_in_poly(m_pos_logica, poly):
                    editor.area_selezionata_del = i
                    break
        else:
            editor.area_selezionata_del = None
            
        mappa.render(canvas_logica, editor)
        
        screen_real.fill((0,0,0))
        # Rendering della canvas logica nell'area rimanente
        canvas_scalata = pygame.transform.scale(canvas_logica, (RES_FINESTRA[0]-SIDEBAR_WIDTH, RES_FINESTRA[1]-TOPBAR_HEIGHT))
        screen_real.blit(canvas_scalata, (SIDEBAR_WIDTH, TOPBAR_HEIGHT))
        
        editor.draw_ui(screen_real)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__": main()
