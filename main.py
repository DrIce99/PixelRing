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
        m_pos_logica = ((m_pos_real[0] - SIDEBAR_WIDTH) * RES_LOGICA[0] // (RES_FINESTRA[0] - SIDEBAR_WIDTH),
                        (m_pos_real[1] - TOPBAR_HEIGHT) * RES_LOGICA[1] // (RES_FINESTRA[1] - TOPBAR_HEIGHT))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if m_pos_real[0] < SIDEBAR_WIDTH: # Click Sidebar
                    idx = (m_pos_real[1] - 40) // 50 + 1
                    if idx in TIPI_SUPERFICIE: editor.tipo_corrente = idx
                elif m_pos_real[1] < TOPBAR_HEIGHT: # Click Topbar
                    if SIDEBAR_WIDTH + 20 <= m_pos_real[0] <= SIDEBAR_WIDTH + 80: editor.mode = "ADD"
                    if SIDEBAR_WIDTH + 100 <= m_pos_real[0] <= SIDEBAR_WIDTH + 160: editor.mode = "EDIT"
                    if SIDEBAR_WIDTH + 180 <= m_pos_real[0] <= SIDEBAR_WIDTH + 240: editor.mode = "DELETE"
                else:
                    editor.gestisci_click(m_pos_logica, mappa)
            
            if event.type == pygame.MOUSEBUTTONUP:
                editor.punto_trascinato = None
                mappa.salva_mappa()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: editor.crea_area(mappa)
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    editor.tipo_corrente = int(event.unicode)

        editor.update_edit(m_pos_logica, mappa)
        
        canvas_logica.fill((20, 20, 25))
        mappa.render(canvas_logica, editor.punti_selezionati)
        
        screen_real.fill((0,0,0))
        # Rendering della canvas logica nell'area rimanente
        canvas_scalata = pygame.transform.scale(canvas_logica, (RES_FINESTRA[0]-SIDEBAR_WIDTH, RES_FINESTRA[1]-TOPBAR_HEIGHT))
        screen_real.blit(canvas_scalata, (SIDEBAR_WIDTH, TOPBAR_HEIGHT))
        
        editor.draw_ui(screen_real)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__": main()
