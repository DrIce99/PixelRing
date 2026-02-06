# game/entities.py
import pygame
from core.config import *

class Player:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.speed = 1.5
        self.radius = 4  # Hitbox del giocatore

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel.x = (keys[pygame.K_d] - keys[pygame.K_a])
        self.vel.y = (keys[pygame.K_s] - keys[pygame.K_w])
        
        if self.vel.length() > 0:
            self.vel = self.vel.normalize() * self.speed

    def check_collisions(self, mappa):
        """Controlla i segmenti solidi e corregge la posizione del player"""
        for area in mappa.aree:
            # 1. Collisione con i segmenti specifici
            segmenti = area.get("segmenti_solidi", [])
            
            # Se l'area ha collisione totale, consideriamo tutti i suoi lati
            if area.get("collisione_totale", False):
                punti = area["punti"]
                for i in range(len(punti)):
                    segmenti.append([punti[i], punti[(i + 1) % len(punti)]])

            for seg in segmenti:
                p1 = pygame.Vector2(mappa.punti_globali[seg[0]])
                p2 = pygame.Vector2(mappa.punti_globali[seg[1]])
                
                # Trova il punto sul segmento più vicino al player
                v = p2 - p1
                w = self.pos - p1
                t = max(0, min(1, w.dot(v) / v.length_squared()))
                punto_vicino = p1 + t * v
                
                # Distanza tra player e il punto più vicino sul muro
                dist_vec = self.pos - punto_vicino
                distanza = dist_vec.length()
                
                # Se la distanza è minore del raggio, c'è collisione!
                if 0 < distanza < self.radius:
                    # Spingi il player fuori dal muro
                    push_out = dist_vec.normalize() * (self.radius - distanza)
                    self.pos += push_out

    def update(self, mappa):
        # 1. Muovi il player
        self.pos += self.vel
        # 2. Risolvi le collisioni con la mappa
        self.check_collisions(mappa)

    def draw(self, surface, cam):
        # Disegno scalato basato sulla camera
        draw_pos = (self.pos + cam.camera_offset) * cam.zoom_level
        pygame.draw.circle(surface, (255, 255, 255), 
                          (int(draw_pos.x), int(draw_pos.y)), 
                          int(self.radius * cam.zoom_level))