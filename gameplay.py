import pygame
from random import randint
from sprites import SpriteLoader
from api import *
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class Game:
    TORPEDO_COOLDOWN = 1000  # Tempo de recarga em milissegundos

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Aventura submarina")
        self.clock = pygame.time.Clock()
        self.sprites = SpriteLoader()
        self.running = True
        self.score = 0
        self.phase = 1

        # Inicializa nave e objetos do jogo
        self.submarino = pygame.Rect(50, 300, 50, 50)
        self.corais = []
        self.tesouros = []
        self.torpedos = []

        # Controle de tempo para recarga dos torpedos
        self.last_torpedo_time = 0
        # Nome do jogador
        self.player_name = ""

    def main_menu(self):
        """Exibe o menu principal."""
        font = pygame.font.Font(None, 64)
        small_font = pygame.font.Font(None, 36)
        menu_options = ["Jogar", "Ranking"]
        selected_option = 0

        while self.running:
            self.screen.fill((0, 0, 0))
            title_text = font.render("Aventura submarina", True, (255, 255, 255))
            self.screen.blit(
                title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100)
            )

            for i, option in enumerate(menu_options):
                color = (255, 255, 255) if i == selected_option else (150, 150, 150)
                option_text = small_font.render(option, True, color)
                self.screen.blit(
                    option_text,
                    (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 200 + i * 50),
                )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:
                            self.get_player_name()
                            self.run()
                        elif selected_option == 1:
                            self.display_ranking()

    def get_player_name(self):
        """Tela para o jogador inserir seu nome."""
        font = pygame.font.Font(None, 36)
        name_input = ""
        input_active = True

        while input_active:
            self.screen.fill((0, 0, 0))
            prompt_text = font.render("Digite seu nome:", True, (255, 255, 255))
            self.screen.blit(
                prompt_text,
                (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 200),
            )

            name_text = font.render(name_input, True, (255, 255, 255))
            self.screen.blit(
                name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 250)
            )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    input_active = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.player_name = name_input
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        name_input += event.unicode

    def display_ranking(self):
        """Exibe a lista de rankings com barra de rolagem."""
        font = pygame.font.Font(None, 36)
        scroll_offset = 0  # Controle do deslocamento inicial
        scroll_speed = 20  # Velocidade do scroll

        try:
            # Obter rankings da API
            rankings = get_rankings()
        except requests.RequestException as e:
            rankings = []
            print(f"Erro ao carregar rankings: {e}")

        # Configurações da tela
        line_height = 40  # Altura de cada linha
        visible_height = 400  # Altura da área visível (caixa de exibição do ranking)

        # Altura total do conteúdo
        content_height = len(rankings) * line_height

        while True:
            self.screen.fill((0, 0, 0))  # Limpa a tela

            # Renderizar título
            title_text = font.render("Ranking", True, (255, 255, 255))
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

            # Limitar o deslocamento máximo e mínimo
            max_scroll = max(0, content_height - visible_height)
            scroll_offset = max(0, min(scroll_offset, max_scroll))

            # Exibe rankings
            if rankings:
                start_index = scroll_offset // line_height
                end_index = start_index + (visible_height // line_height) + 1
                visible_rankings = rankings[start_index:end_index]

                for i, entry in enumerate(visible_rankings):
                    nome_jogador = entry.get('nome_jogador', '---')
                    score = entry.get('pontos', 0)
                    ranking_text = font.render(f"{start_index + i + 1}. {nome_jogador}: {score} pontos", True, (255, 255, 255))
                    y_position = 100 + (i * line_height)
                    self.screen.blit(ranking_text, (SCREEN_WIDTH // 2 - ranking_text.get_width() // 2, y_position))
            else:
                # Caso não haja rankings
                error_text = font.render("Nenhum ranking disponível.", True, (255, 255, 255))
                self.screen.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, 100))

            # Mensagem de voltar
            back_text = font.render("Pressione ESC para voltar", True, (255, 255, 255))
            self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 520))

            # Atualizar a tela
            pygame.display.flip()

            # Lidar com eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_UP:
                        scroll_offset -= scroll_speed
                    elif event.key == pygame.K_DOWN:
                        scroll_offset += scroll_speed
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll para cima
                        scroll_offset -= scroll_speed
                    elif event.button == 5:  # Scroll para baixo
                        scroll_offset += scroll_speed

            """Exibe a lista de rankings com barra de rolagem."""
            font = pygame.font.Font(None, 36)
            scroll_offset = 0  # Controle do deslocamento inicial
            scroll_speed = 20  # Velocidade do scroll

            try:
                # Obter rankings da API
                rankings = get_rankings()
            except requests.RequestException as e:
                rankings = []
                print(f"Erro ao carregar rankings: {e}")

            # Configurações da tela e cálculo da altura do conteúdo
            line_height = 40  # Altura de cada linha
            content_height = len(rankings) * line_height  # Altura total do conteúdo
            visible_height = 400  # Altura da área visível

            while True:
                self.screen.fill((0, 0, 0))  # Limpa a tela

                # Renderizar título
                title_text = font.render("Ranking", True, (255, 255, 255))
                self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

                # Renderizar rankings em uma superfície separada
                scrollable_surface = pygame.Surface((SCREEN_WIDTH, content_height))
                scrollable_surface.fill((0, 0, 0))

                if rankings:
                    # Exibe rankings
                    for i, entry in enumerate(rankings):
                        nome_jogador = entry.get('nome_jogador', '---')
                        score = entry.get('pontos', 0)
                        ranking_text = font.render(f"{i + 1}. {nome_jogador}: {score} pontos", True, (255, 255, 255))
                        scrollable_surface.blit(ranking_text, (SCREEN_WIDTH // 2 - ranking_text.get_width() // 2, i * line_height))
                else:
                    # Caso não haja rankings
                    error_text = font.render("Nenhum ranking disponível.", True, (255, 255, 255))
                    scrollable_surface.blit(error_text, (SCREEN_WIDTH // 2 - error_text.get_width() // 2, 0))

                # Ajustar o deslocamento para evitar espaços em branco
                max_scroll = max(0, content_height - visible_height)
                scroll_offset = max(0, min(scroll_offset, max_scroll))

                # Exibir a superfície com a parte visível (clipping)
                visible_rect = pygame.Rect(0, scroll_offset, SCREEN_WIDTH, visible_height)
                self.screen.blit(scrollable_surface, (0, 100), visible_rect)

                # Mensagem de voltar
                back_text = font.render("Pressione ESC para voltar", True, (255, 255, 255))
                self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, 520))

                # Atualizar a tela
                pygame.display.flip()

                # Lidar com eventos
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return
                        elif event.key == pygame.K_UP:
                            # Role para cima
                            scroll_offset -= scroll_speed
                        elif event.key == pygame.K_DOWN:
                            # Role para baixo
                            scroll_offset += scroll_speed
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 4:  # Scroll para cima
                            scroll_offset -= scroll_speed
                        elif event.button == 5:  # Scroll para baixo
                            scroll_offset += scroll_speed

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_events(self):
        """Lidar com eventos durante o jogo."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                salvar_score(self.player_name, self.score)
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Voltar ao menu principal
                    self.main_menu()
                
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.submarino.y > 0:
            self.submarino.y -= 5
        if keys[pygame.K_DOWN] and self.submarino.y < SCREEN_HEIGHT - 50:
            self.submarino.y += 5

        if self.phase == 1:
            self.update_phase_1()
        elif self.phase == 2:
            self.update_phase_2()
        elif self.phase == 3:
            self.update_phase_3()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.sprites.fundos[self.phase - 1], (0, 0))
        self.screen.blit(self.sprites.submarino, self.submarino)

        for tesouro in self.tesouros:
            self.screen.blit(self.sprites.tesouro, tesouro)

        for coral in self.corais:
            self.screen.blit(self.sprites.coral, coral)

        for torpedo in self.torpedos:
            self.screen.blit(self.sprites.torpedo, torpedo)

        # Exibe pontuação
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Pontuação: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    def update_phase_1(self):
        self.spawn_tesouros(limit=5, speed=2, score_increment=2)
        if self.score >= 10:
            self.phase = 2

    def update_phase_2(self):
        self.spawn_tesouros(limit=5, speed=3, score_increment=5)
        self.spawn_corais(limit=3, speed=4)
        if self.score >= 200:
            self.phase = 3

    def update_phase_3(self):
        self.spawn_tesouros(limit=7, speed=4, score_increment=10)
        self.spawn_corais(limit=5, speed=5)

        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and current_time - self.last_torpedo_time >= self.TORPEDO_COOLDOWN:
            self.shoot_torpedo()
            self.last_torpedo_time = current_time

        # Atualiza torpedos
        self.update_torpedos()

        # Condição de vitória
        if self.score >= 400:
            if self.score == 400:
                salvar_score(self.player_name, self.score)
            self.display_victory_screen()
            self.running = False

    def spawn_tesouros(self, limit, speed, score_increment):
        if len(self.tesouros) < limit:
            self.tesouros.append(
                pygame.Rect(randint(SCREEN_WIDTH, SCREEN_WIDTH + 200), randint(0, SCREEN_HEIGHT - 50), 50, 50)
            )

        for tesouro in self.tesouros[:]:
            tesouro.x -= speed
            if tesouro.colliderect(self.submarino):
                self.tesouros.remove(tesouro)
                self.score += score_increment
            elif tesouro.x < 0:
                self.tesouros.remove(tesouro)

    def spawn_corais(self, limit, speed):
        if len(self.corais) < limit:
            self.corais.append(
                pygame.Rect(randint(SCREEN_WIDTH, SCREEN_WIDTH + 200), randint(0, SCREEN_HEIGHT - 50), 50, 50)
            )

        for coral in self.corais[:]:
            coral.x -= speed
            if coral.colliderect(self.submarino):
                salvar_score(self.player_name, self.score)
                self.main_menu()
            elif coral.x < 0:
                self.corais.remove(coral)

    def shoot_torpedo(self):
        torpedo = pygame.Rect(self.submarino.x + 40, self.submarino.y + 20, 30, 10)
        self.torpedos.append(torpedo)

    def update_torpedos(self):
        for torpedo in self.torpedos[:]:
            torpedo.x += 10
            for coral in self.corais[:]:
                if torpedo.colliderect(coral):
                    self.corais.remove(coral)
                    self.torpedos.remove(torpedo)
                    self.score += 20
                    break
            if torpedo.x > SCREEN_WIDTH:
                self.torpedos.remove(torpedo)

    def display_victory_screen(self):
        """Tela de vitória com opção de voltar ao menu principal."""
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 40)

        text = font.render("Parabéns! Você venceu!", True, (255, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        back_text = font.render("Pressione ENTER para voltar ao menu", True, (255, 255, 255))
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Voltar ao menu principal
                        self.main_menu()
                        waiting = False