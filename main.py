import pygame
import random
import json

pygame.init()

#abertura do .JSON, acessível ao código como um dicionário
with open('dados.json', 'r') as file:
    dados = json.load(file)

#configurações gerais
largura, altura = 1280, 720
TELA = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Space Guardians')

fonte = pygame.font.SysFont('arial', 30, False, False)
fonteInicio = pygame.font.SysFont('arial', 50, False, False)
fonteMaior = pygame.font.SysFont('arial', 52, False, False)

inativoInput = (255, 255, 255)
ativoInput = (22, 176, 227)

#naves

#inimigos
naveVermelha = pygame.image.load('media/naveVermelha.png')
naveVerde = pygame.image.load('media/naveVerde.png')
naveAmarela = pygame.image.load('media/naveAmarela.png')

#jogador
nave1 = pygame.image.load('media/playerSkin/atena.png').convert()
nave1 = pygame.transform.scale(nave1, (250, 150))
corNave1 = (228, 228, 227)
corNave1d = (179, 177, 179)

nave2 = pygame.image.load('media/playerSkin/catalina.png').convert()
nave2 = pygame.transform.scale(nave2, (250, 150))
corNave2 = (3, 119, 188)
corNave2d = (63, 81, 181)

nave3 = pygame.image.load('media/playerSkin/ozomatli.png').convert()
nave3 = pygame.transform.scale(nave3, (250, 150))
corNave3 = (211, 132, 61)
corNave3d = (127, 202, 201)

nave4 = pygame.image.load('media/playerSkin/selene.png').convert()
nave4 = pygame.transform.scale(nave4, (250, 150))
corNave4 = (56, 60, 124)
corNave4d = (45, 224, 199)

nave5 = pygame.image.load('media/playerSkin/tonatiuh.png').convert()
nave5 = pygame.transform.scale(nave5, (250, 150))
corNave5 = (212, 29, 13)
corNave5d = (6, 120, 94)

nave6 = pygame.image.load('media/playerSkin/seth.png').convert()
nave6 = pygame.transform.scale(nave6, (250, 150))
corNave6 = (58, 101, 140)
corNave6d = (212, 239, 252)

#lasers
laserVermelho = pygame.image.load('media/laserVermelho.png')
laserVerde = pygame.image.load('media/laserVerde.png')
laserAmarelo = pygame.image.load('media/laserAmarelo.png')
laserAzul = pygame.image.load('media/laserAzul.png')

#background
fundo = pygame.transform.scale(pygame.image.load('media/espaco.jpg'), (largura,altura))
imagemFundoInicio = pygame.image.load('media/background.png').convert()
imagemFundoInicio = pygame.transform.scale(imagemFundoInicio, (largura / 1.5, altura / 1.5))

#imagem auxiliar
foguete = pygame.image.load('media/rocket.png').convert()
foguete = pygame.transform.scale(foguete, (350, 350))

#musica de fundo
pygame.mixer.music.load('sounds/space-chillout.mp3')
pygame.mixer.music.play(-1)

#som de disparo
fogoP = pygame.mixer.Sound('sounds/laser0.wav')
fogoP.set_volume(0.4)
fogoI = pygame.mixer.Sound('sounds/laser1.wav')
fogoI.set_volume(0.4)

#som de explosão
boom = pygame.mixer.Sound('sounds/boom.wav')
explosao = pygame.mixer.Sound('sounds/explosao.wav')

#definições globais
dificuldade = 1
naveEscolhida = 1
nome = ''

#classes

#classe do laser
class Laser:
	#construtor da classe
	def __init__(self, x, y, img):
		self.x = x
		self.y = y 
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	#desenho do laser na tela
	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	#movimentação do laser
	def move(self, vel):
		self.y += vel

	#laser fora da tela
	def off_screen(self, altura):
		return not(self.y <= altura and self.y >= 0)

	#colisão do laser
	def collision(self, obj):
		return collide(self, obj)

#classe da nave
class Nave:
	#tempo de espera a cada disparo
	COOLDOWN = 30

	#construtor da classe
	def __init__(self, x, y, health = 100):
		self.x = x
		self.y = y
		self.health = health
		self.nave_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	#desenho das naves na tela
	def draw(self, window):
		window.blit(self.nave_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)

	#movimento dos lasers
	def move_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(altura):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	#tempo de espera a cada disparo
	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0:
			self.cool_down_counter += 1

	#mecânica de disparo
	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1

	#largura da nave
	def get_width(self):
		return self.nave_img.get_width()

	#altura da nave
	def get_height(self):
		return self.nave_img.get_height()

#classe do jogador
class Player(Nave):
	#contrutor da classe
	def __init__(self, x, y, nave_player, pontuacao, health = 100):
		super().__init__(x, y, health)
		self.nave_img = nave_player
		self.laser_img = laserAzul
		self.mask = pygame.mask.from_surface(self.nave_img)
		self.max_health = health
		self.pontuacao = pontuacao

	#movimento do laser
	def move_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(altura):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						if laser in self.lasers:
							self.lasers.remove(laser)
							somaPontos(self.pontuacao)
							boom.play()

	#desenho jogador + barra de vida na tela
	def draw(self, window):
		super().draw(window)
		self.healthbar(window)

	#barra de vida
	def healthbar(self, window):
		pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.nave_img.get_height() + 10, self.nave_img.get_width(), 10))
		pygame.draw.rect(window, (0, 255, 0), (self.x ,self.y + self.nave_img.get_height() + 10, self.nave_img.get_width() * (self.health / self.max_health), 10))

#classe dos inimigos
class Inimigo(Nave):
	#mapeamento das cores dos inimigos
	COLOR_MAP =	{
				'red': (naveVermelha, laserVermelho),
				'green': (naveVerde, laserVerde),
				'yellow': (naveAmarela, laserAmarelo)
				}

	#construtor da classe
	def __init__(self, x, y, color, health = 100):
		super().__init__(x, y, health)
		self.nave_img, self.laser_img = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.nave_img)

	#movimentacao dos inimigos
	def move(self, vel):
		self.y += vel

	#mecânica de disparo
	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x - 20, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1
			fogoI.play()

#classe da caixa de texto
class InputBox:
	#construtor da classe
	def __init__(self, x, y, w, h, text=''):
		self.rect = pygame.Rect(x, y, w, h)
		self.color = inativoInput
		self.text = text
		self.txt_surface = fonte.render(text, True, self.color)
		self.active = False

	#captura do evento
	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.rect.collidepoint(event.pos):
				self.active = not self.active
			else:
				self.active = False
			if self.active:
				self.color = ativoInput  
			else:
				self.color = inativoInput
		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_RETURN:
					novoNome(self.text)
					selecaoDificuldade()
					self.text = ''
				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
					pygame.display.flip()
				else:
					self.text += event.unicode
				self.txt_surface = fonte.render(self.text, True, self.color)

	#atualiza a caixa de texto e sua largura
	def update(self):
		width = max(200, self.txt_surface.get_width()+10)
		self.rect.w = width

	#desenhar caixa de texto na tela
	def draw(self, screen):
		screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
		pygame.draw.rect(screen, self.color, self.rect, 2)

#mecânica de colisão
def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#atualição do placar
def somaPontos(x):
	global pontos
	pontos += x

#atualização do nome
def novoNome(x):
    global nome
    nome = x

#visualiza os dados do .JSON e monta o ranking dos pontuadores
def visualizarDados():
	lista = []
	maiores = []
	lideres = []

	for user in dados:
		lista.append(dados[user]['pontos'])
		maiores.append(dados[user]['pontos'])
	maiores = sorted(maiores, reverse=True)

	for c in range(0, len(maiores)):
		x = maiores[c]
		if lista.index(x) not in lideres:
			lideres.append(lista.index(x))
		else:
			lideres.append(lista.index(x)+1)
            
	pessoas = []
	for z in dados:
		pessoas.append(dados[z])

	ranking = []
	for z in lideres:
		ranking.append(pessoas[z])
	return ranking

#novo placar para o .JSON
def novoPlacar(nome, pontos):
    novaJogada = {'nome': '', 'pontos': 0}
    novaJogada['nome'] = nome
    novaJogada['pontos'] = pontos
    dados[len(dados)] = (novaJogada)

#salvar o .JSON com as alterações do novo placar registrado
def atualizarRanking(dados):
    with open('dados.json', 'w') as file:
        json.dump(dados, file, indent=4)

#tela com ranking, atualizado a cada partida
def lideresRanking():
	ranking = visualizarDados()
	
	nickMsg = 'SUA IDENTIFICAÇÃO'
	nickMsg1 = 'Clique na caixa de texto'
	nickMsg2 = 'Após definir, pressione ENTER'
	nickMsg3 = 'RANKING'
	nickMsg4 = 'ID.                                  pts.'
	nickMsg5 = f'{(ranking[0]["nome"]) if len(ranking) > 0 else "------------------"}'
	nickMsg6 = f'{(ranking[0]["pontos"]) if len(ranking) > 0 else "------------------"}'
	nickMsg7 = f'{(ranking[1]["nome"]) if len(ranking) > 1 else "------------------"}'
	nickMsg8 = f'{(ranking[1]["pontos"]) if len(ranking) > 1 else "------------------"}'
	nickMsg9 = f'{(ranking[2]["nome"]) if len(ranking) > 2 else "------------------"}'
	nickMsg10 = f'{(ranking[2]["pontos"]) if len(ranking) > 2 else "------------------"}'
	nickMsg11 = f'{(ranking[3]["nome"]) if len(ranking) > 3 else "------------------"}'
	nickMsg12 = f'{(ranking[3]["pontos"]) if len(ranking) > 3 else "------------------"}'
	nickMsg13 = f'{(ranking[4]["nome"]) if len(ranking) > 4 else "------------------"}'
	nickMsg14 = f'{(ranking[4]["pontos"]) if len(ranking) > 4 else "------------------"}'
	nickMsg15 = f'{(ranking[5]["nome"]) if len(ranking) > 5 else "------------------"}'
	nickMsg16 = f'{(ranking[5]["pontos"]) if len(ranking) > 5 else "------------------"}'
	nickMsg17 = f'{(ranking[6]["nome"]) if len(ranking) > 6 else "------------------"}'
	nickMsg18 = f'{(ranking[6]["pontos"]) if len(ranking) > 6 else "------------------"}'
	nickMsg19 = f'{(ranking[7]["nome"]) if len(ranking) > 7 else "------------------"}'
	nickMsg20 = f'{(ranking[7]["pontos"]) if len(ranking) > 7 else "------------------"}'
	nickMsg21 = f'{(ranking[8]["nome"]) if len(ranking) > 8 else "------------------"}'
	nickMsg22 = f'{(ranking[8]["pontos"]) if len(ranking) > 8 else "------------------"}'
	nickMsg23 = f'{(ranking[9]["nome"]) if len(ranking) > 9 else "------------------"}'
	nickMsg24 = f'{(ranking[9]["pontos"]) if len(ranking) > 9 else "------------------"}'
	nickMsg25 = f'{(ranking[10]["nome"]) if len(ranking) > 10 else "------------------"}'
	nickMsg26 = f'{(ranking[10]["pontos"]) if len(ranking) > 10 else "------------------"}'
	nickMsg27 = f'{(ranking[11]["nome"]) if len(ranking) > 11 else "------------------"}'
	nickMsg28 = f'{(ranking[11]["pontos"]) if len(ranking) > 11 else "------------------"}'

	formatadoNick = fonteInicio.render(nickMsg, True, (255, 255, 255))
	formatadoNick1 = fonte.render(nickMsg1, True, (255, 255, 255))
	formatadoNick2 = fonte.render(nickMsg2, True, (255, 255, 255))
	formatadoNick3 = fonteInicio.render(nickMsg3, True, (255, 255, 255))
	formatadoNick4 = fonte.render(nickMsg4, True, (255, 255, 255))
	formatadoNick5 = fonte.render(nickMsg5, True, (255, 255, 255))
	formatadoNick6 = fonte.render(nickMsg6, True, (255, 255, 255))
	formatadoNick7 = fonte.render(nickMsg7, True, (255, 255, 255))
	formatadoNick8 = fonte.render(nickMsg8, True, (255, 255, 255))
	formatadoNick9  = fonte.render(nickMsg9, True, (255, 255, 255))
	formatadoNick10 = fonte.render(nickMsg10, True, (255, 255, 255))
	formatadoNick11 = fonte.render(nickMsg11, True, (255, 255, 255))
	formatadoNick12 = fonte.render(nickMsg12, True, (255, 255, 255))
	formatadoNick13 = fonte.render(nickMsg13, True, (255, 255, 255))
	formatadoNick14 = fonte.render(nickMsg14, True, (255, 255, 255))
	formatadoNick15 = fonte.render(nickMsg15, True, (255, 255, 255))
	formatadoNick16 = fonte.render(nickMsg16, True, (255, 255, 255))
	formatadoNick17 = fonte.render(nickMsg17, True, (255, 255, 255))
	formatadoNick18 = fonte.render(nickMsg18, True, (255, 255, 255))
	formatadoNick19 = fonte.render(nickMsg19, True, (255, 255, 255))
	formatadoNick20 = fonte.render(nickMsg20, True, (255, 255, 255))
	formatadoNick21 = fonte.render(nickMsg21, True, (255, 255, 255))
	formatadoNick22 = fonte.render(nickMsg22, True, (255, 255, 255))
	formatadoNick23 = fonte.render(nickMsg23, True, (255, 255, 255))
	formatadoNick24 = fonte.render(nickMsg24, True, (255, 255, 255))
	formatadoNick25 = fonte.render(nickMsg25, True, (255, 255, 255))
	formatadoNick26 = fonte.render(nickMsg26, True, (255, 255, 255))
	formatadoNick27 = fonte.render(nickMsg27, True, (255, 255, 255))
	formatadoNick28 = fonte.render(nickMsg28, True, (255, 255, 255))

	TELA.blit(formatadoNick, (70, 60))
	TELA.blit(formatadoNick1, (largura / 2 - formatadoNick1.get_width() / 2, 600))
	TELA.blit(formatadoNick2, (largura / 2 - formatadoNick2.get_width() / 2, 630))
	TELA.blit(formatadoNick3, (1000, 60))
	TELA.blit(formatadoNick4, (largura  - formatadoNick4.get_width() - 20, 110))
	TELA.blit(formatadoNick5, (900, 150))
	TELA.blit(formatadoNick6, (largura  - formatadoNick6.get_width() - 20, 150))
	TELA.blit(formatadoNick7, (900, 180))
	TELA.blit(formatadoNick8, (largura  - formatadoNick8.get_width() - 20, 180))
	TELA.blit(formatadoNick9, (900, 210))
	TELA.blit(formatadoNick10, (largura  - formatadoNick10.get_width() - 20, 210))
	TELA.blit(formatadoNick11, (900, 240))
	TELA.blit(formatadoNick12, (largura  - formatadoNick12.get_width() - 20, 240))
	TELA.blit(formatadoNick13, (900, 270))
	TELA.blit(formatadoNick14, (largura  - formatadoNick14.get_width() - 20, 270))
	TELA.blit(formatadoNick15, (900, 300))
	TELA.blit(formatadoNick16, (largura  - formatadoNick16.get_width() - 20, 300))
	TELA.blit(formatadoNick17, (900, 330))
	TELA.blit(formatadoNick18, (largura  - formatadoNick18.get_width() - 20, 330))
	TELA.blit(formatadoNick19, (900, 360))
	TELA.blit(formatadoNick20, (largura  - formatadoNick20.get_width() - 20, 360))
	TELA.blit(formatadoNick21, (900, 390))
	TELA.blit(formatadoNick22, (largura  - formatadoNick22.get_width() - 20, 390))
	TELA.blit(formatadoNick23, (900, 420))
	TELA.blit(formatadoNick24, (largura  - formatadoNick24.get_width() - 20, 420))
	TELA.blit(formatadoNick25, (900, 450))
	TELA.blit(formatadoNick26, (largura  - formatadoNick26.get_width() - 20, 450))
	TELA.blit(formatadoNick27, (900, 480))
	TELA.blit(formatadoNick28, (largura  - formatadoNick28.get_width() - 20, 480))

#função principal, o inicio do jogo
def main():
	global pontos

	if dificuldade == 1:
		dificuldadeA = 'F'
		vidas = 5
		wave_length = 3
		inimigo_vel = 2
		player_vel = 14
		laser_vel = 25
		pontuacao = 20
	elif dificuldade == 2:
		dificuldadeA = 'M'
		vidas = 4
		wave_length = 4
		inimigo_vel = 3
		player_vel = 10
		laser_vel = 20
		pontuacao = 30
	elif dificuldade == 3:
		dificuldadeA = 'D'
		vidas = 3
		wave_length = 5
		inimigo_vel = 5
		player_vel = 10
		laser_vel = 25
		pontuacao = 50

	run = True
	FPS = 60
	nivel = 0
	pontos = 0
	main_font = pygame.font.SysFont('verdana', 40)
	lost_font = pygame.font.SysFont('verdana', 50)

	inimigos = []

	if naveEscolhida == 1:
		NAVE_PLAYER = pygame.transform.scale(pygame.image.load('media/playerSkin/atena.png'), (100, 90))
	elif naveEscolhida == 2:
		NAVE_PLAYER = pygame.transform.scale(pygame.image.load('media/playerSkin/catalina.png'), (100, 90))
	elif naveEscolhida == 3:
		NAVE_PLAYER = pygame.transform.scale(pygame.image.load('media/playerSkin/ozomatli.png'), (100, 90))
	elif naveEscolhida == 4:
		NAVE_PLAYER = pygame.transform.scale(pygame.image.load('media/playerSkin/selene.png'), (100, 90))
	elif naveEscolhida == 5:
		NAVE_PLAYER = pygame.transform.scale(pygame.image.load('media/playerSkin/tonatiuh.png'), (100, 90))
	elif naveEscolhida == 6:
		NAVE_PLAYER = pygame.transform.scale(pygame.image.load('media/playerSkin/seth.png'), (100, 90))

	player = Player(largura / 2 - 250 / 2, 500, NAVE_PLAYER, pontuacao)
	clock = pygame.time.Clock()

	lost = False
	lost_count = 0

	def redraw_window():

		if naveEscolhida == 1:
			corNavePrincipal = corNave1
			corNaveSecundaria = corNave1d
		elif naveEscolhida == 2:
			corNavePrincipal = corNave2
			corNaveSecundaria = corNave2d
		elif naveEscolhida == 3:
			corNavePrincipal = corNave3
			corNaveSecundaria = corNave3d
		elif naveEscolhida == 4:
			corNavePrincipal = corNave4
			corNaveSecundaria = corNave4d
		elif naveEscolhida == 5:
			corNavePrincipal = corNave5
			corNaveSecundaria = corNave5d
		elif naveEscolhida == 6:
			corNavePrincipal = corNave6
			corNaveSecundaria = corNave6d

		TELA.blit(fundo, (0, 0))
		lives_label = main_font.render(f'Vidas: {vidas}', 1, corNavePrincipal)
		level_label = main_font.render(f'Nível: {nivel}', 1, corNavePrincipal)
		points_label = main_font.render(f'Pontos: {pontos}', 1, corNavePrincipal)
		name_label = main_font.render(f'ID: {nome}', 1, corNaveSecundaria)
		difficulty_label = main_font.render(f'Dificuldade: {dificuldadeA}', 1, corNaveSecundaria)

		TELA.blit(lives_label, (20, 20))
		TELA.blit(level_label, (20, 70))
		TELA.blit(points_label, (20, 120))
		TELA.blit(name_label, (largura - name_label.get_width() - 20, 20))
		TELA.blit(difficulty_label, (largura - difficulty_label.get_width() - 20, 70))

		for inimigo in inimigos:
			inimigo.draw(TELA)

		player.draw(TELA)

		if lost:
			TELA.blit(fundo, (0, 0))
			lost_label = lost_font.render('SUA NAVE FOI DESTRUIDA', 1, (255, 255, 255))
			lost_label1 = lost_font.render('R para retornar', 1, (255, 255, 255))
			lost_label2 = lost_font.render('Z para alterar a dificuldade', 1, (255, 255, 255))
			lost_label3 = main_font.render(f'ID: {nome}', 1, (255, 255, 255))
			lost_label4 = main_font.render(f'Dificuldade: {dificuldadeA}', 1, (255, 255, 255))
			lost_label5 = main_font.render(f'Pontos: {pontos}', 1, (255, 255, 255))

			TELA.blit(lost_label, (largura / 2 - lost_label.get_width() / 2, 350))
			TELA.blit(lost_label1, ((largura / 2 - lost_label1.get_width() / 2), 550))
			TELA.blit(lost_label2, ((largura / 2 - lost_label2.get_width() / 2), 600))
			TELA.blit(lost_label3, (largura - lost_label3.get_width() - 20, 20))
			TELA.blit(lost_label4, (largura - lost_label4.get_width() - 20, 70))
			TELA.blit(lost_label5, (largura - lost_label5.get_width() - 20, 120))

			novoPlacar(nome, pontos)
			atualizarRanking(dados)

			pygame.display.update()

			while True:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						pygame.quit()
						exit()
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_z:
							main_menu()
						elif event.key == pygame.K_r:
							main()

		pygame.display.update()

	while run:
		clock.tick(FPS)
		redraw_window()

		if vidas <= 0 or player.health <= 0:
			lost = True
			lost_count += 1

		if lost:
			if lost_count > FPS * 3:
				run = False
			else:
				continue

		if len(inimigos) == 0:
			nivel += 1
			wave_length += 1
			for i in range(wave_length):
				inimigo = Inimigo(random.randrange(50, largura - 100),  random.randrange(-1500, -100),random.choice(['red', 'green', 'yellow']))
				inimigos.append(inimigo)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				exit()

		keys = pygame.key.get_pressed()
		if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_vel > 0:
			player.x -= player_vel
		if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_vel + player.get_width() < largura:
			player.x += player_vel
		if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_vel > 0:
			player.y -= player_vel
		if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_vel + player.get_height() + 15 < altura:
			player.y += player_vel
		if keys[pygame.K_SPACE]:
			fogoP.play()
			player.shoot()

		for inimigo in inimigos[:]:
			inimigo.move(inimigo_vel)
			inimigo.move_lasers(laser_vel, player)

			if random.randrange(0, 2 * 60) == 1:
				inimigo.shoot()

			if collide(inimigo, player):
				player.health -= 10
				inimigos.remove(inimigo)
				pontos += pontuacao
				explosao.play()
			if inimigo.y + inimigo.get_height() > altura:
				vidas -= 1
				inimigos.remove(inimigo)

		player.move_lasers(-laser_vel, inimigos)

#menu principal, tela de apresentação
def main_menu():
	run = True
	while run:
		TELA.fill((0, 0, 0))
		TELA.blit(imagemFundoInicio, (200, 100))

		msgInicio = 'SPACE GUARDIANS'
		msgInicio1 =  'pressione ENTER'

		formatadoInicio = fonteInicio.render(msgInicio, True, (255, 255, 255))
		formatadoInicio1 = fonte.render(msgInicio1, True, (255, 255, 255))

		TELA.blit(formatadoInicio, (70, 60))
		TELA.blit(formatadoInicio1, (largura / 2 - formatadoInicio1.get_width() / 2, 620))

		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					selecaoNick()

#tela para definição do nome + apresentação das melhores pontuações
def selecaoNick():
	run = True
	while run:
		TELA.fill((0, 0, 0))
		TELA.blit(imagemFundoInicio, (60, 160))
		input_box1 = InputBox(70, 130, 140, 50)
		input_boxes = [input_box1]
		done = False

		lideresRanking()

		while not done:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					done = True
					pygame.quit()
					exit()
				for box in input_boxes:
					box.handle_event(event)

			for box in input_boxes:
				box.update()
			TELA.fill((0, 0, 0))
			TELA.blit(imagemFundoInicio, (60, 160))
			lideresRanking()
			for box in input_boxes:
				box.draw(TELA)
			pygame.display.flip()

	pygame.display.flip()

#tela para selecao da dificuldade
def selecaoDificuldade():
	run = True
	while run:
		global dificuldade
		TELA.fill((0, 0, 0))

		msg1TelaDificuldade = 'DEFINA A DIFICULDADE:'
		msg2TelaDificuldade = '1 - FÁCIL'
		msg3TelaDificuldade = '2 - NORMAL'
		msg4TelaDificuldade = '3 - DIFÍCIL'
		msg5TelaDificuldade = 'pressione a tecla correspondente'

		formatado1TelaDificuldade = fonteMaior.render(msg1TelaDificuldade, True, (255, 255, 255))
		formatado2TelaDificuldade = fonteMaior.render(msg2TelaDificuldade, True, (56, 228, 174))
		formatado3TelaDificuldade = fonteMaior.render(msg3TelaDificuldade, True, (97, 15, 127))
		formatado4TelaDificuldade = fonteMaior.render(msg4TelaDificuldade, True, (255, 0, 0))
		formatado5TelaDificuldade = fonte.render(msg5TelaDificuldade, True, (255, 255, 255))

		TELA.blit(formatado1TelaDificuldade, (410, 60))
		TELA.blit(formatado2TelaDificuldade, (100, 200))
		TELA.blit(formatado3TelaDificuldade, (100, 270))
		TELA.blit(formatado4TelaDificuldade, (100, 340))
		TELA.blit(formatado5TelaDificuldade, (400, 620))

		TELA.blit(foguete, (720, 230))

		pygame.display.flip()

		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
					pygame.quit()
					exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_1:
						dificuldade = 1
						selecionarNave()
					elif event.key == pygame.K_2:
						dificuldade = 2
						selecionarNave()
					elif event.key == pygame.K_3:
						dificuldade = 3
						selecionarNave()

#tela para selecao da nave do jogador
def selecionarNave():
	global naveEscolhida

	run = True
	while run:
		TELA.fill((0, 0, 0))

		msg1nave = 'ESCOLHA O SEU VEÍCULO'
		msg2nave = '1 - ATENA'
		msg3nave = '2 - CATALINA'
		msg4nave = '3 - OZOMATLI'
		msg5nave = '4 - SELENE'
		msg6nave = '5 - TONATIUH'
		msg7nave = '6 - SETH'

		formatado1nave = fonteMaior.render(msg1nave, True, (255, 255, 255))
		formatado2nave = fonte.render(msg2nave, True, (255, 255, 255))
		formatado3nave = fonte.render(msg3nave, True, (255, 255, 255))
		formatado4nave = fonte.render(msg4nave, True, (255, 255, 255))
		formatado5nave = fonte.render(msg5nave, True, (255, 255, 255))
		formatado6nave = fonte.render(msg6nave, True, (255, 255, 255))
		formatado7nave = fonte.render(msg7nave, True, (255, 255, 255))

		TELA.blit(formatado1nave, (320, 60))
		TELA.blit(formatado2nave, (100, 570))
		TELA.blit(formatado3nave, (280, 570))
		TELA.blit(formatado4nave, (500, 570))
		TELA.blit(formatado5nave, (100, 620))
		TELA.blit(formatado6nave, (280, 620))
		TELA.blit(formatado7nave, (500, 620))

		TELA.blit(nave1, (215, 170))
		TELA.blit(nave2, (515, 170))
		TELA.blit(nave3, (815, 170))
		TELA.blit(nave4, (215, 370))
		TELA.blit(nave5, (515, 370))
		TELA.blit(nave6, (815, 370))

		pygame.display.flip()

		while True:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						run = False
						pygame.quit()
						exit()
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_1:
							naveEscolhida = 1
							main()
						elif event.key == pygame.K_2:
							naveEscolhida = 2
							main()
						elif event.key == pygame.K_3:
							naveEscolhida = 3
							main()
						elif event.key == pygame.K_4:
							naveEscolhida = 4
							main()
						elif event.key == pygame.K_5:
							naveEscolhida = 5
							main()
						elif event.key == pygame.K_6:
							naveEscolhida = 6
							main()

#iniciando a primeira tela do jogo
main_menu()
