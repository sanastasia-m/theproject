import pygame
import random
import sys
import math
import numpy as np
import csv  # для записи рекордов
import datetime

pygame.font.init()

# инициализация игрового поля
size = width, height = 1000, 800
screen = pygame.display.set_mode(size)
pygame.init()
pygame.display.set_caption('PlayTag')
fps = 50
# pygame.mouse.set_visible(False)


# функции переливания
clr = [255, 0, 0]
ite = 1
doing = True
step = 4  # скорость

back_clr = [0, 255, 255]  # для противоположной функции
back_ite = 1
back_doing = False

blue_null = 0  # для бонуса
blue_doing = True

game_over_var = False  # окончена ли игра

font_name = None  # определение шрифта в игре

main_menu_activ = True  # показывать главное меню

show_records = False
'''Для каждого цвета он смещается вниз или вверх
в соответствии с его начальным значением (0 или 255)
Так же работает для обратной функции, но с другими входными данными

'''


def gradient():  # переливание
    global doing, ite
    if doing:
        clr[ite] += step
    else:
        clr[ite] -= step
    clr[ite] = in_border(clr[ite])
    if clr[ite] <= 0 or clr[ite] >= 255:
        if doing:
            doing = False
        else:
            doing = True
        ite -= 1
        if ite == -1:
            ite = 2
    return (clr[0], clr[1], clr[2])


def back_gradient():  # противоположность gradient()
    global back_doing, back_ite
    if back_doing:
        back_clr[back_ite] += step
    else:
        back_clr[back_ite] -= step
    back_clr[back_ite] = in_border(back_clr[back_ite])
    if back_clr[back_ite] <= 0 or back_clr[back_ite] >= 255:
        if back_doing:
            back_doing = False
        else:
            back_doing = True
        back_ite -= 1
        if back_ite == -1:
            back_ite = 2
    return (back_clr[0], back_clr[1], back_clr[2])


'''Поднимает значение соответствующих пикселей до 255 и обратно,
так получается переливание к белому и назад
шаг делится на количество бонусов,
чтобы переливания всегда казались с более менее одинаковой скоростью

'''


def gradient_blue(mode):  # удвоенный счет бонуса
    global blue_null, blue_doing
    try:  # если бонусов нет, то ничего не происходит
        if blue_doing:
            blue_null += 7 / len(bonus.sprites())
        else:
            blue_null -= 7 / len(bonus.sprites())
        blue_null = in_border(blue_null)
        if blue_null <= 0 or blue_null >= 250:
            if blue_doing:
                blue_doing = False
            else:
                blue_doing = True
        if mode == 0:
            return (math.ceil(blue_null), math.ceil(blue_null), 255)
        elif mode == 1:
            return (math.ceil(blue_null), 255, math.ceil(blue_null))
    except ZeroDivisionError:
        return (0, 0, 0, 0)  # полностью прозрачный


def in_border(num, minimum=0, maximum=255):
    if num > maximum:
        return maximum
    elif num < minimum:
        return minimum
    return num


# Добавление текста на экран


def draw_text(color, text, size, x=0, y=0):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)


'''Вектор, направленный от столкнувшегося объекта к главному прибавляется 
к вектору направления движения главного объекта, модуль приводится
к модулю начального вектора движения вектора по подобию треугольников

'''


def repulsion(main_class, collision_class):  # реалистичные отталкивания
    main_vec = np.array(main_class.rect.center)
    col_vec = np.array(collision_class.rect.center)
    vec_pos = main_vec - col_vec
    vec_move = np.array([main_class.vx, main_class.vy])
    abs_vec_move = (vec_move[0] ** 2 + vec_move[1] ** 2) ** 0.5
    # сложение вектора направления столкновения и вектора движения
    vec_move = vec_move + vec_pos
    abs_new_vec_move = (vec_move[0] ** 2 + vec_move[1] ** 2) ** 0.5
    # приведение к начальной скорости по подобию треугольников
    vec_move = vec_move * (abs_vec_move / abs_new_vec_move)
    return (vec_move[0], vec_move[1])


# функции, связанные с завершением игры
def game_over(killer):
    global game_over_var
    # удаляет все, кроме игрока, шара, с которым он столкнулся,
    # рамок и прогрессбаров
    for i in all_sprites.sprites():
        if i != hero and i != killer and i not in borders.sprites() and i not in progress_bar.sprites():
            i.kill()
    game_over_var = True
    try:  # файловая система не поддерживает csv файлы
        date_now = datetime.datetime.now()  # сохранение рекорда
        with open("information.csv", mode="a", encoding="utf-8") as w_file:
            writer_file = csv.writer(w_file, delimiter=";", lineterminator="\r")
            writer_file.writerow([[score],
                                  [str(f'Дата : {date_now.day}-{date_now.month}-{date_now.year} Время :  {date_now.hour}:{date_now.minute}:{date_now.second}')]])
        w_file.close()
    except PermissionError:
        pass


def restart():  # установка начальных значений внутриигровых переменных
    global b, kb, x, y, kx, ky, per, power, per_speed, count_time_red_ball, count_time_bonus_ball, paused
    global bonus_score, text_color, screen_color, score_text_color, game_over_var
    # остается только игрок и рамки
    for i in all_sprites.sprites():
        if i != hero and i not in borders.sprites() and i not in progress_bar.sprites():
            i.kill()
    game.game_frames = 0
    hero.helth = 700
    hero.image = pygame.Surface((math.ceil(hero.helth ** 0.5), math.ceil(hero.helth ** 0.5)))
    hero.rect.center = width / 2, height / 2
    for i in range(4):
        Ball(15)
    b = Bonus(5, 0)
    kb = Bonus(5, 1)
    x, y = hero.rect.center
    kx = 0
    ky = 0
    per = 0
    power = 0
    per_speed = True

    hero.bonus_time = 250
    hero.found_bonus = False  # Нашел ли игрок бонус переливания
    hero.found_kill_bonus = False  # Нашел ли игрок бонус инверсии

    count_time_red_ball = 150  # счетчик до создания нового шара
    count_time_bonus_ball = 1000  # счетчик до создания нового бонуса

    paused = False

    bonus_score = 0
    text_color = (0, 0, 0)
    screen_color = (255, 228, 225)
    score_text_color = (0, 0, 0)

    game_over_var = False

    main_menu_activ = False

    show_records = False


def clear_screen():
    for i in all_sprites.sprites():
        if i not in borders.sprites() and i != hero:
            i.kill()
    # выводим за рамки, чтобы не удалять, но его было не видно
    hero.rect.center = -1000, -1000  


class Game():  # класс для хранения игровых значений
    def __init__(self):
        self.game_frames, self.game_time, self.game_speed = 0, 0, 1

    def update(self):
        self.game_frames += 1
        self.game_time = self.game_frames / fps
        self.game_speed = (2 ** (self.game_frames / 1000)) ** 0.5  # коэффециент скорости красных шаров


class Ball(pygame.sprite.Sprite):  # красные шары
    def __init__(self, radius):
        x, y = random.randint(25, width - 25), random.randint(85, height - 25)
        super().__init__(all_sprites)
        self.add(red_balls)
        self.radius = radius
        self.x, self.y = x, y
        self.pos_vec = np.array([x, y])
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, (gradient()),
                           (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.vx = random.randint(1, 5)  # определяем начальное направление
        self.vy = random.randrange(1, 5)
        self.permissionx = True
        self.permissiony = True  # более точная коллизия стен
        self.collision = True  # проверка на коллизию своих братьев
        self.count_red_ball = 50  # время интервала увеличения размера
        # если с самого начала они накладываются, то один удаляется
        for i in red_balls.sprites():
            if self != i:
                if pygame.sprite.collide_rect(self, i):
                    self.kill()

    # движение с проверкой столкновение шара со стенками
    def update(self):
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, (225, 0, 0),
                           (self.radius, self.radius), self.radius)
        self.x += math.ceil(self.vx * game.game_speed)  # ускорение в зависимости от времени, проведенного в игре
        self.y += math.ceil(self.vy * game.game_speed)
        self.pos_vec = np.array(self.rect.center)
        self.rect = pygame.Rect(self.x, self.y, 2 * self.radius, 2 * self.radius)
        if hero.found_bonus:
            pygame.draw.circle(self.image, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                               (self.radius, self.radius), self.radius)
        self.rect = self.rect.move(math.ceil(self.vx * game.game_speed), math.ceil(self.vy * game.game_speed))
        self.posx, self.posy = self.rect.center
        if self.posx - self.radius <= 5 or self.posx + self.radius >= width - self.radius - 5:
            if self.permissionx:
                self.permissionx = False
                self.vx = -self.vx
                '''Если шар влетел в стену, но еще не вылетел из нее, то он уже поменял направление,
                и менять его еще раз нет смысла: пусть движется дальше, пока не выйдет из нее, иначе он в ней застрянет

                '''
        elif self.posy - self.radius <= 60 or self.posy + self.radius >= height - self.radius - 5:
            if self.permissiony:
                self.vy = -self.vy
                self.permissiony = False
        else:
            self.permissionx = True
            self.permissiony = True
        if pygame.sprite.spritecollideany(self, black_ball):  # коллизия с игроком
            hero.pos_vec = np.array(hero.rect.center)
            if hero.found_kill_bonus:
                # жизнь игрока изменяется пропорционально размеру шара, с которым он столкнулся
                hero.helth += self.radius ** 1.3
                back = hero.rect.center
                hero.image = pygame.Surface((math.ceil(hero.helth ** 0.5), math.ceil(hero.helth ** 0.5)))
                hero.rect = hero.image.get_rect()
                hero.rect.center = back
                Particle(self.radius / 2, hero.pos_vec - self.pos_vec, self, 1)
                self.kill()
            else:
                if hero.helth <= self.radius ** 2:
                    game_over(self)
                else:
                    hero.helth -= self.radius ** 2
                    back = hero.rect.center
                    hero.image = pygame.Surface((math.ceil(hero.helth ** 0.5), math.ceil(hero.helth ** 0.5)))
                    hero.rect = hero.image.get_rect()
                    hero.rect.center = back
                    new_vec = hero.pos_vec - self.pos_vec
                    Particle(self.radius, new_vec, hero, 0)  # частицы - отображение, что игрока покусали
                    Particle(self.radius, (new_vec[1], -new_vec[0]), hero, 0)  # в 4 разные стороны
                    Particle(self.radius, (-new_vec[0], -new_vec[1]), hero, 0)
                    Particle(self.radius, (-new_vec[1], new_vec[0]), hero, 0)
                    self.kill()
        for i in red_balls.sprites():
            if self != i:
                if pygame.sprite.collide_rect(self, i):  # отталкивание друг от друга
                    if self.collision:
                        self.vx, self.vy = repulsion(self, i)
                    else:
                        self.collision = True
        # увеличение размера
        if self.count_red_ball == 0:
            if self.radius < 15 and self.collision:  # не увеличивает размер пока взоимодействует с другими шарами,
                # иначе может застрять в них
                self.radius += 1
                self.image = pygame.Surface((2 * self.radius, 2 * self.radius),
                                            pygame.SRCALPHA, 32)
            self.count_red_ball = 50
        else:
            self.count_red_ball -= 1


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        self.add(borders)
        self.image = pygame.Surface([x2 - x1 + 1, y2 - y1 + 1])  # + 1 это компенсация при y1 = y2 или x1 = x2
        self.rect = pygame.Rect(x1, y1, x2 - x1 + 1, y2 - y1 + 1)


class Bonus(pygame.sprite.Sprite):  # бонусы в одной группе
    def __init__(self, radius, mode):
        super().__init__(all_sprites)
        x, y = random.randint(25, width - 25), random.randint(85, height - 25)
        self.add(bonus)
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, (gradient_blue(0)),
                           (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.vx = random.randint(1, 5)  # определяем начальное направление
        self.vy = random.randrange(1, 5)
        self.permissionx = True
        self.permissiony = True
        self.bonus_mode = mode

    # движение с проверкой столкновения со стенами
    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if self.bonus_mode == 0:
            pygame.draw.circle(self.image, (gradient_blue(0)),
                               (self.radius, self.radius), self.radius)
        elif self.bonus_mode == 1:
            pygame.draw.circle(self.image, (gradient_blue(1)),
                               (self.radius, self.radius), self.radius)
        self.posx, self.posy = self.rect.center
        if self.posx - self.radius <= 0 or self.posx + self.radius >= width - self.radius:
            if self.permissionx:
                self.permissionx = False
                self.vx = -self.vx
        elif self.posy - self.radius <= 60 or self.posy + self.radius >= height - self.radius:
            if self.permissiony:
                self.vy = -self.vy
                self.permissiony = False
        else:
            self.permissionx = True
            self.permissiony = True
        if pygame.sprite.spritecollideany(self, black_ball):  # взоимодействие с игроком
            if self.bonus_mode == 0:
                hero.found_bonus = True
                hero.found_kill_bonus = False
                Speed_load(250, 0)
            elif self.bonus_mode == 1:
                hero.found_bonus = False
                hero.found_kill_bonus = True
                Speed_load(250, 1)
            hero.bonus_time = 250
            self.kill()


class Speed_load(pygame.sprite.Sprite):  # отображение счетчика действий
    def __init__(self, value, mode):  # прогрессбары для режимов или скачка
        super().__init__(all_sprites)
        self.add(progress_bar)
        self.mode = mode
        self.value = 20 / value
        self.radius = 20
        if self.mode == 0:  # режим переливаний
            self.x, self.y = 30, 30
            self.color = (103, 103, 103)
        elif self.mode == 1:  # режим инверсии
            self.x, self.y = 90, 30
            self.color = (39, 240, 159)
        elif self.mode == 2:  # показывает перезарядку перед рывком
            self.x, self.y = width - 30, 30
            if hero.found_kill_bonus:
                self.color = (255, 228, 225)
            else:
                self.color = (0, 27, 30)
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, self.color,
                           (self.radius, self.radius), self.radius)
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)

    def update(self):
        if self.mode == 0:
            if hero.found_bonus:  # длительность мода инверсии
                self.radius -= self.value
                self.color = back_gradient()
                if self.radius <= 0:
                    self.kill()
            else:
                self.kill()
        elif self.mode == 1:  # длительность мода переливания
            if hero.found_kill_bonus:
                self.radius -= self.value
                if self.radius <= 0:
                    self.kill()
            else:
                self.kill()
        elif self.mode == 2:  # длительность задержки перед возможностью рывка
            self.radius -= self.value
            if self.radius <= 0:
                self.kill()
        self.image = pygame.Surface((2 * math.ceil(self.radius), 2 * math.ceil(self.radius)),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, self.color,
                           (math.ceil(self.radius), math.ceil(self.radius)), math.ceil(self.radius))
        self.rect = pygame.Rect(self.x - math.ceil(self.radius), self.y - math.ceil(self.radius),
                                2 * math.ceil(self.radius), 2 * math.ceil(self.radius))


class Particle(pygame.sprite.Sprite):  # частицы, возникающие при взаимодействии игрока с шарами
    def __init__(self, part_size, new_pos_vec, work_class, mode):
        super().__init__(all_sprites)
        self.add(particles)
        self.part_size = part_size
        self.go_to_x, self.go_to_y = work_class.pos_vec[0] + new_pos_vec[0], work_class.pos_vec[1] + new_pos_vec[1]
        self.opasity = 255
        if mode == 0:  # частицы черного квадрата
            self.image = pygame.Surface((self.part_size, self.part_size))
            self.image.fill((30, 30, 30))
            self.rect = self.image.get_rect()
        elif mode == 1:  # частицы красного круга
            self.image = pygame.Surface((2 * part_size, 2 * part_size),
                                        pygame.SRCALPHA, 32)
            pygame.draw.circle(self.image, ((166, 72, 72)),
                               (part_size, part_size), part_size)
            self.rect = self.image.get_rect()
        self.rect.center = work_class.rect.center
        self.live = 10

    def update(self):  # медленное движение и плавное исчезание
        if self.live == 0:
            self.kill()
        self.posx, self.posy = self.rect.center
        self.rect.center = (self.posx + (self.go_to_x - self.posx) / 5, self.posy + (self.go_to_y - self.posy) / 5)
        self.image.set_alpha(self.opasity)
        self.opasity -= 25
        self.live -= 1


game = Game()

all_sprites = pygame.sprite.Group()
borders = pygame.sprite.Group()
red_balls = pygame.sprite.Group()
black_ball = pygame.sprite.Group()
bonus = pygame.sprite.Group()
progress_bar = pygame.sprite.Group()
particles = pygame.sprite.Group()

hero = pygame.sprite.Sprite(all_sprites)  # работа со спрайтом героя
hero.helth = 700
hero.image = pygame.Surface((math.ceil(hero.helth ** 0.5), math.ceil(hero.helth ** 0.5)))
hero.image.fill((0, 0, 0))
hero.rect = hero.image.get_rect()
hero.add(black_ball)

b1 = Border(5, 60, width - 5, 60)  # Создание рамок
b2 = Border(5, height - 5, width - 5, height - 5)
b3 = Border(5, 60, 5, height - 5)
b4 = Border(width - 5, 60, width - 5, height - 5)

bk1 = Border(85, 140, width - 85, 140)
bk2 = Border(85, height - 85, width - 85, height - 85)
bk3 = Border(85, 140, 85, height - 85)
bk4 = Border(width - 85, 140, width - 85, height - 85)

bk1.image.set_alpha(50)
bk2.image.set_alpha(50)
bk3.image.set_alpha(50)
bk4.image.set_alpha(50)

restart()  # инициализация игры
clear_screen()

clock = pygame.time.Clock()

running = True

while running:
    pygame.display.update()

    for event in pygame.event.get():  # события
        if event.type == pygame.KEYDOWN and not main_menu_activ:
            if event.key == pygame.K_ESCAPE and not game_over_var and not main_menu_activ:  # поставить на паузу
                if paused:
                    paused = False
                else:
                    paused = True
            elif (event.key == pygame.K_F4 or event.key == pygame.K_BACKSPACE) and (paused or game_over_var or
                                                                                    show_records):
                # выйти в меню
                if main_menu_activ:
                    main_menu_activ = False
                else:
                    main_menu_activ = True
                if show_records:
                    show_records = False
                if paused:
                    paused = False
                if game_over_var:
                    game_over_var = False
            elif event.key == pygame.K_DELETE and (paused or game_over_var):  # рестарт
                restart()
        if event.type == pygame.MOUSEBUTTONDOWN and main_menu_activ:  # кнопки в меню
            if event.button == 1:
                mouse = event.pos
                if 85 < mouse[0] < 500:
                    if 300 < mouse[1] < 400:  # Начать игру
                        main_menu_activ = False
                        restart()
                    elif 400 < mouse[1] < 500:  # рекорды
                        show_records = True
                        if main_menu_activ:
                            main_menu_activ = False
                    elif 500 < mouse[1] < 600:  # выход
                        running = False
        if event.type == pygame.QUIT:
            running = False
        if not paused and not game_over_var and not main_menu_activ:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and per_speed:  # рывок
                    mx, my = hero.rect.center
                    kx = (x - mx) / 7
                    ky = (y - my) / 7
                    per = 5
                    power = 10
                    bonus_score -= 3
                    per_speed = False
                    Speed_load(10, 2)
            if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                x, y = event.pos
                if y < 140 + math.ceil(hero.helth ** 0.5 / 2):  # запрещавется выход игрока за пределы
                    # малого куба с возможностью скользить вдоль стен
                    y = 140 + math.ceil(hero.helth ** 0.5 / 2) + 5
                    # "hero.helth ** 0.5" используется как ширина спрайта для компенсации границы
                    x = x + (x - hero.rect.center[0]) / 2 + 5
                elif y > height - 85 - math.ceil(hero.helth ** 0.5 / 2):
                    y = height - 85 - math.ceil(hero.helth ** 0.5 / 2) + 5
                    x = x + (x - hero.rect.center[0]) / 2 + 5
                if x < 85 + math.ceil(hero.helth ** 0.5 / 2):
                    x = 85 + math.ceil(hero.helth ** 0.5 / 2) + 5
                    if height - 85 + math.ceil(hero.helth ** 0.5 / 2) < y < 135 - math.ceil(hero.helth ** 0.5 / 2):
                        y = y + (y - hero.rect.center[1]) / 2 + 5
                elif x > width - 85 - math.ceil(hero.helth ** 0.5 / 2):
                    x = width - 85 - math.ceil(hero.helth ** 0.5 / 2)
                    if height - 85 + math.ceil(hero.helth ** 0.5 / 2) < y < 140 - math.ceil(hero.helth ** 0.5 / 2):
                        y = y + (y - hero.rect.center[1]) / 2 + 5

    if not paused and not game_over_var and not main_menu_activ and not show_records:
        # заполнение экрана в зависимости от бонуса
        hero.image.fill((0, 0, 0))
        for i in borders.sprites():
            i.image.fill((0, 0, 0))
        if hero.found_bonus:  # удвоенный счет
            screen_color = gradient()
            text_color = (0, 0, 0)
            bonus_score += 1 / 30  # прибавление бонусного счета
            if hero.bonus_time <= -3:
                hero.found_bonus = False
                hero.found_kill_bonus = False
        elif hero.found_kill_bonus:  # инверсия
            if hero.bonus_time <= -3:
                hero.found_bonus = False
                hero.found_kill_bonus = False
            if 11 < hero.bonus_time < 19 or 31 < hero.bonus_time < 39 or hero.bonus_time <= 0:
                # красивое мелькание перед окончанием действия бонуса
                screen_color = (255, 228, 225)
                text_color = (0, 0, 0)
                hero.image.fill((0, 0, 0))
                for i in borders.sprites():
                    i.image.fill((0, 0, 0))
            elif hero.bonus_time > 0:
                screen_color = (0, 27, 30)
                text_color = (194, 194, 194)
                hero.image.fill(text_color)
                for i in borders.sprites():
                    i.image.fill(text_color)
        else:  # нет бонусов
            screen_color = (255, 228, 225)
            text_color = (0, 0, 0)
            hero.bonus_time = 250
        hero.bonus_time -= 1

        all_sprites.update()
        game.update()  # обновление внутриигровых значений

        # обновление размеров хитбокса героя
        mx, my = hero.rect.center
        hero.rect.center = (mx + (x - mx) * 2 / (hero.helth ** 0.5) + kx, my + (y - my) * 2 / (hero.helth ** 0.5) + ky)

        if per == 0:  # перерыв перед возможностью нового рывка
            kx = 0
            ky = 0
        if power == 0:
            per_speed = True
        power -= 1
        if power > -10:  # красный счет из-за снятия баллов с возможностью мелькания
            score_text_color = (255, 0, 0)
            pix0 = in_border(score_text_color[0] - (11 - (7 * int(text_color[0] == 194))) * (10 - power))
            pix1 = in_border(score_text_color[1] + (11 * (10 - power) * int(text_color[1] == 194)))
            score_text_color = (pix0, pix1, pix1)
        else:
            score_text_color = text_color
        per -= 1

        if count_time_red_ball == 0:  # создание красных шаров
            Ball(3)
            count_time_red_ball = 150
        else:
            count_time_red_ball -= 1

        if count_time_bonus_ball == 0:  # создание бонусов
            if random.randint(0, 1) == 0:
                Bonus(5, 0)
            else:
                Bonus(5, 1)
            count_time_bonus_ball = 1000
        else:
            count_time_bonus_ball -= 1

    screen.fill(screen_color)
    all_sprites.draw(screen)

    if len(all_sprites.sprites()) > 150:  # перегрузка
        sys.exit()

    # отрисовка счета и текста подсказок
    score = math.ceil(game.game_time + bonus_score)
    if main_menu_activ:  # показание меню в приоритете
        clear_screen()
        text_color = (0, 0, 0)
        screen_color = (255, 228, 225)
        for i in borders.sprites():
            i.image.fill(text_color)
        draw_text(text_color, "PlayTag", 100, 30, 70)
        draw_text(text_color, 'играть', 100, 100, 325)
        draw_text(text_color, 'рекорды', 100, 100, 425)
        draw_text(text_color, 'выход', 100, 100, 525)
    elif paused:
        draw_text(score_text_color, str(score), 70, width / 4, 5)
        draw_text(text_color, 'esc - продолжить игру', 16, width / 4 + 100, 7)
        draw_text(text_color, 'delete - рестарт', 16, width / 4 + 100, 25)
        draw_text(text_color, 'F4 / Backspace - главное меню', 16, width / 4 + 100, 43)
        draw_text(text_color, "Pause", 24, 15, 65)
    elif game_over_var:
        draw_text(score_text_color, str(score), 70, width / 4, 5)
        draw_text(text_color, "Game Over", 100, width / 2 - 200, height / 2 - 50)
        draw_text(text_color, 'delete - рестарт', 16, width / 4 + 100, 7)
        draw_text(text_color, 'F4 / Backspace - главное меню', 16, width / 4 + 100, 25)
    elif show_records:
        draw_text(text_color, "РЕКОРДЫ", 80, 30, 80)
        with open('information.csv', newline='') as File:
            reader = csv.reader(File)
            k = 150
            txt = [row for row in reader]
            last = txt[-1]
            txt.sort()
            k += 35
            # draw_text(text_color, str(' : '.join(''.join(text).split(';'))), 30, 100, k)
            draw_text(text_color, str("Наилудший результат: "), 30, 100, k)
            k += 35
            draw_text(text_color, str(' : '.join(''.join(txt[-1]).split(';'))), 30, 100, k)
            k += 35
            draw_text(text_color, str("Наихудший результат: "), 30, 100, k)
            k += 35
            draw_text(text_color, str(' : '.join(''.join(txt[0]).split(';'))), 30, 100, k)
            k += 35
            draw_text(text_color, str("Последний результат: "), 30, 100, k)
            k += 35
            draw_text(text_color, str(' : '.join(''.join(last).split(';'))), 30, 100, k)

        draw_text(text_color, "Backspace - выйти отсюда", 20, 25, height - 50)

    else:
        draw_text(score_text_color, str(score), 70, width / 4, 5)
        draw_text(text_color, 'esc - поставить на паузу', 16, width / 4 + 100, 7)

    pygame.display.flip()
    clock.tick(fps)
pygame.quit()