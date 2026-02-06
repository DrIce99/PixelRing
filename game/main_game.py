import pygame
from core.config import *
from core.engine import Mappa
from game.entities import Player

def main():
    pygame.init()
    # Il gioco usa tutta la finestra, quindi non sottraiamo Sidebar/Topbar
    screen_real = pygame.display.set_mode(RES_FINESTRA)
    canvas_logica = pygame.Surface(RES_LOGICA)
    clock = pygame.time.Clock()

    mappa = Mappa()
    # Inizializziamo il giocatore al centro della mappa o in un punto salvato
    player = Player(RES_LOGICA[0] // 2, RES_LOGICA[1] // 2)

    # Creiamo un oggetto "camera" fittizio per riutilizzare mappa.render()
    # In futuro potresti creare una classe Camera dedicata in core/engine.py
    class Camera:
        def __init__(self):
            self.camera_offset = pygame.Vector2(0, 0)
            self.zoom_level = 2.0  # Zoom più ravvicinato per il gioco
            self.mode = "GAME"     # Per disattivare gli hover dell'editor
            self.punti_selezionati = []
            self.area_selezionata_del = None
            self.segmento_selezionato = None

    cam = Camera()

    running = True
    while running:
        # --- 1. INPUT ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Zoom manuale opzionale anche in gioco
            if event.type == pygame.MOUSEWHEEL:
                cam.zoom_level = max(1.0, min(4.0, cam.zoom_level + event.y * 0.1))

        player.handle_input()

        # --- 2. UPDATE ---
        player.update(mappa)

        # LOGICA TELECAMERA: Segue il giocatore
        # L'offset deve essere tale che il player sia al centro della canvas logica
        centro_canvas = pygame.Vector2(RES_LOGICA[0] / 2, RES_LOGICA[1] / 2)
        # Formula: Centro - (PosizionePlayer * Zoom) / Zoom... 
        # Semplificato: vogliamo che Player + Offset = Centro
        cam.camera_offset = (centro_canvas / cam.zoom_level) - player.pos

        # --- 3. DRAW ---
        canvas_logica.fill((15, 15, 20)) # Sfondo scuro dungeon

        # Disegna la mappa (il render usa cam.camera_offset e cam.zoom_level)
        mappa.render(canvas_logica, cam)
        
        # Disegna il player
        player.draw(canvas_logica, cam)

        # Rendering finale pixelato
        screen_real.fill((0, 0, 0))
        # In gioco usiamo tutto lo schermo
        frame_scalato = pygame.transform.scale(canvas_logica, RES_FINESTRA)
        screen_real.blit(frame_scalato, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
