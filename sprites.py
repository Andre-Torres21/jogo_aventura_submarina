import pygame

class Sprites:
    def __init__(self):
        self.submarino = pygame.image.load('assets/submarino.png')
        self.submarino = pygame.transform.scale(self.submarino, (50, 50))
        self.tesouro = pygame.image.load('assets/tesouro.png')
        self.tesouro = pygame.transform.scale(self.tesouro, (50, 50))
        self.coral = pygame.image.load('assets/coral.png')
        self.coral = pygame.transform.scale(self.coral, (50, 50))
        self.torpedo = pygame.image.load('assets/torpedo.png')
        self.torpedo = pygame.transform.scale(self.torpedo, (40, 40))
        self.torpedo = pygame.transform.rotate(self.torpedo, 180)
        self.fundos = [
            pygame.image.load('assets/fundo1.png'),
            pygame.image.load('assets/fundo2.png'),
            pygame.image.load('assets/fundo3.png')
        ]