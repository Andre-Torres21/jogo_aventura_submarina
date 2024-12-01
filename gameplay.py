import pygame
from random import randint
from sprites import Sprites
from api import *
from settings import LARGURA_TELA, ALTURA_TELA, FPS

class Jogo:
    RECARGA_TORPEDO = 1000  # Tempo de recarga em milissegundos

    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("Aventura submarina")
        self.clock = pygame.time.Clock()
        self.sprites = Sprites()
        self.rodando = True
        self.score = 0
        self.fase = 1
        self.score_salvo = False  # Indica se a pontuação já foi salva

        # Inicializa nave e objetos do jogo
        self.submarino = pygame.Rect(50, 300, 50, 50)
        self.corais = []
        self.tesouros = []
        self.torpedos = []

        # Controle de tempo para recarga dos torpedos
        self.tempo_ultimo_torpedo = 0
        # Nome do jogador
        self.nome_jogador = ""

    def menu_principal(self):
        """Exibe o menu principal."""
        fonte = pygame.font.Font(None, 64)
        fonte_pequena = pygame.font.Font(None, 36)
        opcoes_menu = ["Jogar", "Ranking"]
        opcao_selecionada = 0

        while self.rodando:
            self.tela.fill((0, 0, 0))
            texto_titulo = fonte.render("Aventura submarina", True, (255, 255, 255))
            self.tela.blit(
                texto_titulo, (LARGURA_TELA // 2 - texto_titulo.get_width() // 2, 100)
            )

            for i, opcao in enumerate(opcoes_menu):
                cor = (255, 255, 255) if i == opcao_selecionada else (150, 150, 150)
                texto_opcao = fonte_pequena.render(opcao, True, cor)
                self.tela.blit(
                    texto_opcao,
                    (LARGURA_TELA // 2 - texto_opcao.get_width() // 2, 200 + i * 50),
                )

            pygame.display.flip()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_DOWN:
                        opcao_selecionada = (opcao_selecionada + 1) % len(opcoes_menu)
                    elif evento.key == pygame.K_UP:
                        opcao_selecionada = (opcao_selecionada - 1) % len(opcoes_menu)
                    elif evento.key == pygame.K_RETURN:
                        if opcao_selecionada == 0:
                            self.get_nome_jogador()
                            self.rodar()
                        elif opcao_selecionada == 1:
                            self.exibir_ranking()

    def get_nome_jogador(self):
        """Tela para o jogador inserir seu nome."""
        fonte = pygame.font.Font(None, 36)
        input_nome = ""
        input_ativo = True

        while input_ativo:
            self.tela.fill((0, 0, 0))
            texto_prompt = fonte.render("Digite seu nome:", True, (255, 255, 255))
            self.tela.blit(
                texto_prompt,
                (LARGURA_TELA // 2 - texto_prompt.get_width() // 2, 200),
            )

            texto_nome = fonte.render(input_nome, True, (255, 255, 255))
            self.tela.blit(
                texto_nome, (LARGURA_TELA // 2 - texto_nome.get_width() // 2, 250)
            )

            pygame.display.flip()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                    input_ativo = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        self.nome_jogador = input_nome
                        input_ativo = False
                    elif evento.key == pygame.K_BACKSPACE:
                        input_nome = input_nome[:-1]
                    else:
                        input_nome += evento.unicode

    def exibir_ranking(self):
        """Exibe a lista de ranking com barra de rolagem."""
        fonte = pygame.font.Font(None, 36)
        deslocamento_scroll = 0  # Controle do deslocamento inicial
        velocidade_scroll = 20  # Velocidade do scroll

        try:
            # Obter ranking da API
            ranking = get_ranking()
        except requests.RequestException as e:
            ranking = []
            print(f"Erro ao carregar ranking: {e}")

        # Configurações da tela
        altura_linha = 40  # Altura de cada linha
        altura_visivel = 400  # Altura da área visível (caixa de exibição do ranking)
        altura_conteudo = len(ranking) * altura_linha  # Altura total do conteúdo
        max_scroll = max(0, altura_conteudo - altura_visivel)

        while True:
            self.tela.fill((0, 0, 0))  # Limpa a tela

            # renderizar título
            texto_titulo = fonte.render("Ranking", True, (255, 255, 255))
            self.tela.blit(texto_titulo, (LARGURA_TELA // 2 - texto_titulo.get_width() // 2, 50))

            # Limitear o deslocamento máximo e mínimo
            deslocamento_scroll = max(0, min(deslocamento_scroll, max_scroll))

            # Exibe ranking visíveis
            indice_comeco = deslocamento_scroll // altura_linha
            indice_fim = indice_comeco + (altura_visivel // altura_linha) + 1
            ranking_visivel = ranking[indice_comeco:indice_fim]

            if ranking_visivel:
                for i, entrada in enumerate(ranking_visivel):
                    nome_jogador = entrada.get('nome_jogador', '---')
                    score = entrada.get('pontos', 0)
                    texto_ranking = fonte.render(
                        f"{indice_comeco + i + 1}. {nome_jogador}: {score} pontos", True, (255, 255, 255)
                    )
                    posicao_y = 100 + (i * altura_linha)
                    self.tela.blit(texto_ranking, (LARGURA_TELA // 2 - texto_ranking.get_width() // 2, posicao_y))
            else:
                texto_erro = fonte.render("Nenhum ranking disponível.", True, (255, 255, 255))
                self.tela.blit(texto_erro, (LARGURA_TELA // 2 - texto_erro.get_width() // 2, 100))

            # Mensagem de voltar
            texto_voltar = fonte.render("Pressione ESC para voltar", True, (255, 255, 255))
            self.tela.blit(texto_voltar, (LARGURA_TELA // 2 - texto_voltar.get_width() // 2, 520))

            # Atualizar a tela
            pygame.display.flip()

            # Lidar com eventoos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                    return
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        return
                    elif evento.key == pygame.K_UP:
                        deslocamento_scroll -= velocidade_scroll
                    elif evento.key == pygame.K_DOWN:
                        deslocamento_scroll += velocidade_scroll
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 4:  # Scroll para cima
                        deslocamento_scroll -= velocidade_scroll
                    elif evento.button == 5:  # Scroll para baixo
                        deslocamento_scroll += velocidade_scroll

    def rodar(self):
        while self.rodando:
            self.controle_eventos()
            self.atualizar()
            self.renderizar()
            self.clock.tick(FPS)
        pygame.quit()

    def controle_eventos(self):
        """Lidar com eventoos durante o jogo."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salvar_score(self.nome_jogador, self.score)
                self.rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    # Voltar ao menu principal
                    self.menu_principal()
                
    def atualizar(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP] and self.submarino.y > 0:
            self.submarino.y -= 5
        if teclas[pygame.K_DOWN] and self.submarino.y < ALTURA_TELA - 50:
            self.submarino.y += 5

        if self.fase == 1:
            self.atualizar_fase_1()
        elif self.fase == 2:
            self.atualizar_fase_2()
        elif self.fase == 3:
            self.atualizar_fase_3()

    def renderizar(self):
        self.tela.fill((0, 0, 0))
        self.tela.blit(self.sprites.fundos[self.fase - 1], (0, 0))
        self.tela.blit(self.sprites.submarino, self.submarino)

        for tesouro in self.tesouros:
            self.tela.blit(self.sprites.tesouro, tesouro)

        for coral in self.corais:
            self.tela.blit(self.sprites.coral, coral)

        for torpedo in self.torpedos:
            self.tela.blit(self.sprites.torpedo, torpedo)

        # Exibe pontuação
        fonte = pygame.font.Font(None, 36)
        texto_score = fonte.render(f"Pontuação: {self.score}", True, (255, 255, 255))
        self.tela.blit(texto_score, (10, 10))

        pygame.display.flip()

    def atualizar_fase_1(self):
        self.desenhar_tesouros(limite=5, velocidade=2, aumento_score=2)
        if self.score >= 50:
            self.fase = 2

    def atualizar_fase_2(self):
        self.desenhar_tesouros(limite=5, velocidade=3, aumento_score=5)
        self.desenhar_corais(limite=3, velocidade=4)
        if self.score >= 200:
            self.fase = 3

    def atualizar_fase_3(self):
        self.desenhar_tesouros(limite=7, velocidade=4, aumento_score=10)
        self.desenhar_corais(limite=5, velocidade=5)

        teclas = pygame.key.get_pressed()
        tempo_atual = pygame.time.get_ticks()
        if teclas[pygame.K_SPACE] and tempo_atual - self.tempo_ultimo_torpedo >= self.RECARGA_TORPEDO:
            self.disparar_torpedo()
            self.tempo_ultimo_torpedo = tempo_atual

        # Atualiza torpedos
        self.atualizar_torpedos()

        # Condição de vitória
        if self.score >= 400:
            salvar_score(self.nome_jogador, self.score)
            self.exibir_tela_vitoria()
            self.rodando = False

    def desenhar_tesouros(self, limite, velocidade, aumento_score):
        if len(self.tesouros) < limite:
            self.tesouros.append(
                pygame.Rect(randint(LARGURA_TELA, LARGURA_TELA + 200), randint(0, ALTURA_TELA - 50), 50, 50)
            )

        for tesouro in self.tesouros[:]:
            tesouro.x -= velocidade
            if tesouro.colliderect(self.submarino):
                self.tesouros.remove(tesouro)
                self.score += aumento_score
            elif tesouro.x < 0:
                self.tesouros.remove(tesouro)

    def desenhar_corais(self, limite, velocidade):
        if len(self.corais) < limite:
            self.corais.append(
                pygame.Rect(randint(LARGURA_TELA, LARGURA_TELA + 200), randint(0, ALTURA_TELA - 50), 50, 50)
            )

        for coral in self.corais[:]:
            coral.x -= velocidade
            if coral.colliderect(self.submarino):
                if not self.score_salvo:
                    salvar_score(self.nome_jogador, self.score)
                    self.score_salvo = True  # Evita salvar novamente
                self.tela_game_over()
            elif coral.x < 0:
                self.corais.remove(coral)

    def disparar_torpedo(self):
        torpedo = pygame.Rect(self.submarino.x + 40, self.submarino.y + 20, 30, 10)
        self.torpedos.append(torpedo)

    def atualizar_torpedos(self):
        for torpedo in self.torpedos[:]:
            torpedo.x += 10
            for coral in self.corais[:]:
                if torpedo.colliderect(coral):
                    self.corais.remove(coral)
                    self.torpedos.remove(torpedo)
                    self.score += 20
                    break
            if torpedo.x > LARGURA_TELA:
                self.torpedos.remove(torpedo)

    def tela_game_over(self):
        if not self.score_salvo:
            salvar_score(self.nome_jogador, self.score)
            self.score_salvo = True  # Pontuação salva apenas uma vez

        
        """Exibe a tela de fim de jogo com pontuação e opções."""
        fonte = pygame.font.Font(None, 64)
        fonte_pequena = pygame.font.Font(None, 36)

        while True:
            self.tela.fill((0, 0, 0))

            # Texto de fim de jogo
            texto_game_over = fonte.render("Fim de Jogo!", True, (255, 0, 0))
            self.tela.blit(
                texto_game_over, (LARGURA_TELA // 2 - texto_game_over.get_width() // 2, 100)
            )

            # Pontuação
            texto_score = fonte_pequena.render(f"Pontuação: {self.score}", True, (255, 255, 255))
            self.tela.blit(
                texto_score, (LARGURA_TELA // 2 - texto_score.get_width() // 2, 200)
            )

            # Instruções
            texto_instrucoes = fonte_pequena.render("Pressione J para jogar novamente", True, (255, 255, 255))
            self.tela.blit(
                texto_instrucoes, (LARGURA_TELA // 2 - texto_instrucoes.get_width() // 2, 300)
            )
            texto_ranking = fonte_pequena.render("Pressione R para ver o ranking", True, (255, 255, 255))
            self.tela.blit(
                texto_ranking, (LARGURA_TELA // 2 - texto_ranking.get_width() // 2, 350)
            )

            pygame.display.flip()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                    return
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_j:  # Jogar novamente
                        self.reset_jogo()
                        return
                    elif evento.key == pygame.K_r:  # Ver ranking
                        self.exibir_ranking()
                        return

    def reset_jogo(self):
        """Reseta o jogo para iniciar uma nova partida."""
        self.score = 0
        self.fase = 1
        self.submarino = pygame.Rect(50, 300, 50, 50)
        self.corais = []
        self.tesouros = []
        self.torpedos = []
        self.tempo_ultimo_torpedo = 0
        self.score_salvo = False  # Permite salvar pontuação na nova partida
        self.get_nome_jogador()
        self.rodar()  # Inicia o jogo novamente

    def exibir_tela_vitoria(self):
        """Tela de vitória com opção de voltar ao menu principal."""
        self.tela.fill((0, 0, 0))
        fonte = pygame.font.Font(None, 40)

        texto = fonte.render("Parabéns! Você venceu!", True, (255, 255, 255))
        self.tela.blit(texto, (LARGURA_TELA // 2 - texto.get_width() // 2, ALTURA_TELA // 2 - 50))

        texto_voltar = fonte.render("Pressione ENTER para voltar ao menu", True, (255, 255, 255))
        self.tela.blit(texto_voltar, (LARGURA_TELA // 2 - texto_voltar.get_width() // 2, ALTURA_TELA // 2 + 50))

        pygame.display.flip()

        esperando = True
        while esperando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                    esperando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN:
                        # Voltar ao menu principal
                        self.menu_principal()
                        esperando = False