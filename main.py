import pygame
import random
import math
import datetime
from numba import njit
pygame.init()

f = open('data.txt', 'a')

def writeData(string):
	f.write(string + '\n')

D_WIDHT = 640
D_HEIGHT = D_WIDHT
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_WIDHT = D_WIDHT
C = 255
LAYERS = random.randint(1, 8)
writeData('LAYERS = ' + str(LAYERS))

sc = pygame.display.set_mode((D_WIDHT, D_HEIGHT))
clock = pygame.time.Clock()

@njit(fastmath = True)
def getGrad(x1, y1, a_angle, g_w):
	x1 = x1 / g_w
	y1 = y1 / g_w
	x2 = math.cos(a_angle)
	y2 = math.sin(a_angle)
	if (x1 == 0) and (y1 == 0):
		cos_b = 0
	else:
		cos_b = (x1 * x2 + y1 * y2)
	return cos_b

@njit(fastmath = True)
def interpolation(t, g_w):
	t /= g_w
	return t * t * t * (t * (t * 6 - 15) + 10)

noise_layers = []
for k in range(LAYERS):
	GW = GRID_WIDHT // pow(2, random.randint(1, 8))
	writeData('LAYER_' + str(k) + ' = ' + str(GW))
	NODE_NUM = D_WIDHT // GW
	grid = []
	for i in range(NODE_NUM):
		row = []
		for j in range(NODE_NUM):
			row.append(random.random() * 2 * 3.1415926)
		row.append(row[0])
		grid.append(row)
	grid.append(grid[0])

	pic = []
	for x in range(D_WIDHT):
		row = []
		for y in range(D_WIDHT):
			i = x // GW
			j = y // GW
			u = x - i * GW
			v = y - j * GW
			n00 = getGrad(u, v, grid[i][j], GW)
			n01 = getGrad(u - GW, v, grid[i + 1][j], GW)
			n10 = getGrad(u, v - GW, grid[i][j + 1], GW)
			n11 = getGrad(u - GW, v - GW, grid[i + 1][j + 1], GW)
			nx0 = n00 + (n01 - n00) * (interpolation(u, GW))
			nx1 = n10 + (n11 - n10) * (interpolation(u, GW))
			nxy = nx0 + (nx1 - nx0) * (interpolation(v, GW))
			row.append(nxy)
		pic.append(row)
	noise_layers.append(pic)

sc.fill(BLACK)

rgb = []
for k in range(LAYERS):
	rand_r = random.randint(0, 255) // LAYERS
	rand_g = random.randint(0, 255) // LAYERS
	rand_b = random.randint(0, 255) // LAYERS
	rgb.append((rand_r, rand_g, rand_b))
	writeData('RGB_' + str(k) + ' = (' + str(rand_r) + ', ' + str(rand_g) + ', ' + str(rand_b) + ')')

noise_on_off = random.randint(0, 1)
writeData('NOISE_ON_OFF = ' + str(noise_on_off))

for x in range(D_WIDHT):
	for y in range(D_WIDHT):
		color = 0
		r = 0
		g = 0
		b = 0
		for k in range(LAYERS):
			dot = noise_layers[k]
			color = C * (1 + dot[x][y]) / 2 / LAYERS
			color *= pow(k, noise_on_off * 2 * random.random())
			r += int(color / 255 * rgb[k][0]) + rgb[k][0]
			g += int(color / 255 * rgb[k][1]) + rgb[k][1]
			b += int(color / 255 * rgb[k][2]) + rgb[k][2]
			if r > 255:
				r = 255
			elif r < 0:
				r = 0
			if g > 255:
				g = 255
			elif g < 0:
				g = 0
			if b > 255:
				b = 255
			elif b < 0:
				b = 0
		pygame.draw.circle(sc, (r, g, b), (x, y), 1)
start = True
pygame.display.update()

time = datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")
pygame.image.save(sc, time + '_perlin_noise.jpg')

writeData(time)
writeData('')

f.close()

pygame.quit()

