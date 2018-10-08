# Neal Chen(hc4pa)
# Daniel Sykes(djs4yt)

# All images used in this game are from Internet
# This game is inspired by the original "Gold Miner" game.
# Dependency : pygame/gamebox

import pygame
import gamebox
import random
import math


# 0-preparation
# general
camera=gamebox.Camera(1000, 700)
money=0
radins=-70
chain_distance=30
value_caught = 0 ; pict_index = 0 
speed = 5
weight_item_caught = speed +5
counter = 5
counter_up = 0
level = 1
shop_list = []
shop_price = []
money_goal=[1000,2200,3600,5400,7500,10000,12500,17000,21500,26000,30000,45000]
scene = 0 # scene index: 0 = starting scene 1 = game rule scene 2 = game scene 3 = shop scene 4 = you die
index = 0
popped_up_word_counterdown = 16
shop_selection = 0
sound = gamebox.load_sound("mining_music.wav")
sound.play()
#sound = gamebox.load_sound("fishing_poll.wav")
#sound.play()
# item references
item_caught= gamebox.from_color(500,100,"black",1,1)
picture_list=["picture/gold_small.png","picture/gold_middle.png","picture/gold_big.png","picture/rock_small.png","picture/rock_big.png","picture/dimaond.png","picture/mystery_bag.png","picture/background.png","picture/background2.png","picture/machine.png","picture/Starting screen.png","picture/shop.png","picture/intro.png"]

item_picture_list = ["picture/gold samd.png","picture/polisher.png","picture/lamp.png","picture/red gem.png","picture/purple gem.png","picture/green gem.png","picture/lucky rock.png"]
text_list = ["Gold sands:Small gold worths more in the next level","Diamond polisher:Diamond worths 50% more in the next level","Lamp:More diamond would appear in the next level","The Gem of Time:You have 20 more seconds in the next level","The Gem of Luck:You have higher chance of getting good stuff from the random bags.","The Gem of Strength:Pulling minerals back takes less time in the next level","The lucky Rock:Rock worths 300% more in the next level","SOLD OUT!"]

# animation set up
frame= 0
frame2 = 0
sheet1 = gamebox.load_sprite_sheet("picture/animation1.png", 1, 7)
sheet2 = gamebox.load_sprite_sheet("picture/character1_1.png", 1, 7)
sheet3= gamebox.load_sprite_sheet("picture/character1_2.png", 1, 8)
chainhead = gamebox.from_image(200, 200, sheet1[frame])
character = gamebox.from_image(475, 50, sheet2[frame2])

# booleans
direction_left_to_right=True
chain_thrown_out= False
chain_thrown_out_away = True
chain_thrown_out_catchsomething = False
#items
item_gold_modifer = False
item_polisher = False
item_lamp = False
item_time = False
item_luck = False
item_rocks = False

# lists
gold_middle = [gamebox.from_image(400,400,picture_list[1])]
gold_small = [gamebox.from_image(500,500,picture_list[0])]
gold_large = []
gold_dimaond = [gamebox.from_image(700, 500, picture_list[5])]
gold_small_rock = [gamebox.from_image(400, 600, picture_list[3])]
gold_big_rock = [gamebox.from_image(600, 600, picture_list[4])]
gold_random_big = [gamebox.from_image(200, 300,picture_list[6])]

def tick(keys):
    # 1-global-set up all required data
    global radins, money , direction_left_to_right, chain_thrown_out , chain_thrown_out_away , chain_distance , chainhead
    global chain_thrown_out_catchsomething , item_caught , weight_item_caught , speed , background
    global value_caught , pict_index , counter , level, surface, counter_up, frame, frame2, scene, index
    global popped_up_word_counterdown, shop_selection, shop_list, shop_price
    global item_gold_modifer, item_polisher, item_lamp, item_time, item_luck, item_rocks
    camera.clear('grey')


    # differetiate on scenes
    if scene == 0:
        screen = gamebox.from_image(500, 350,picture_list[10])
        screen.scale_by(0.70)
        camera.draw(screen)
        camera.draw(gamebox.from_text(500,500,"Press SPACE to continue","arial",30,"red"))

        # animations
        frame += 1
        if frame == 7:
            frame = 0

        chainhead.image = sheet1[frame]
        if index == 0:
            chainhead = gamebox.from_image(240, 546, sheet1[frame])
        else:
            chainhead = gamebox.from_image(570, 546, sheet1[frame])
        chainhead.scale_by(0.5)
        camera.draw(chainhead)

        if pygame.K_LEFT in keys and index == 1:
            index= 0
        if pygame.K_RIGHT in keys and index == 0:
            index= 1
        if pygame.K_SPACE in keys and index == 0:
            scene= 2
            level_generation(level)
        if pygame.K_SPACE in keys and index == 1:
            keys = []
            scene= 1

    if scene == 1:
        picture = gamebox.from_image(500,350,picture_list[12])
        picture.scale_by(0.5)
        camera.draw(picture)
        if pygame.K_SPACE in keys :
            keys = []
            scene = 0


    if scene == 2:
        counter_up += 1
        picture = gamebox.from_image(500, 380, picture_list[7])
        picture2 = gamebox.from_image(500, 37.5, picture_list[8])
        picture3 = gamebox.from_image(500, 37.5, picture_list[9])
        picture3.scale_by(0.2)

        picture2.scale_by(0.45)
        picture.scale_by(0.7)
        camera.draw(picture)
        camera.draw(picture2)
        camera.draw(picture3)

        # camera.draw(character)

        # animations
        frame += 1
        if frame == 7:
            frame = 0
        chainhead.image = sheet1[frame]

        if chain_thrown_out == False:
            character = gamebox.from_image(455, 50, sheet2[int(frame2)])
            frame2 += 0.5
            if frame2 == 7:
                frame2 = 0
            character.image = sheet2[int(frame2)]
        else:
            character = gamebox.from_image(455, 50, sheet3[int(frame2)])
            frame2 += 0.5
            if frame2 == 8:
                frame2 = 0
            character.image = sheet3[int(frame2)]

        camera.draw(character)

        # 2-when chain available
        # degree regular changes
        if chain_thrown_out == False:
            if popped_up_word_counterdown >= 16:
                if direction_left_to_right == True:
                    radins += 3
                else:
                    radins -= 3

            if radins <= -70:
                direction_left_to_right = True
            if radins >= 70:
                direction_left_to_right = False

            # chain head displays
            chainhead.x = 500 + math.sin(radins / 57.29) * 75
            chainhead.y = 75 + math.cos(radins / 57.29) * 75

            camera.draw(chainhead)

            # chains display
            item = gamebox.from_color(500, 75, "black", 5, 5)
            for i in range(0, 25):
                item = gamebox.from_color(500 + math.sin(radins / 57.29) * 2.5 * i,
                                          75 + math.cos(radins / 57.29) * 2.5 * i, "black", 5, 5)
                camera.draw(item)

        # 3-chain_thrown_out
        # set up throwing chain
        if pygame.K_DOWN in keys and chain_thrown_out == False and popped_up_word_counterdown >= 16:
            chain_thrown_out = True
            chain_thrown_out_away = True
            chain_thrown_out_catchsomething = False
            chain_distance = 30
            character.scale_by(1.2)

        # chain animation
        if chain_thrown_out == True and chain_thrown_out_away == True:
            chain_distance += speed
            for i in range(1, chain_distance):
                item = gamebox.from_color(500 + math.sin(radins / 57.29) * 2.5 * i,
                                          75 + math.cos(radins / 57.29) * 2.5 * i, "black", 5, 5)
                camera.draw(item)
            chainhead.x = 500 + math.sin(radins / 57.29) * (10 + 2.5 * chain_distance)
            chainhead.y = 75 + math.cos(radins / 57.29) * (10 + 2.5 * chain_distance)
            camera.draw(chainhead)

        if chain_thrown_out == True and chain_thrown_out_away == False:
            chain_distance -= weight_item_caught
            for i in range(1, chain_distance):
                item = gamebox.from_color(500 + math.sin(radins / 57.29) * 2.5 * i,
                                          75 + math.cos(radins / 57.29) * 2.5 * i, "black", 5, 5)
                camera.draw(item)
            chainhead.x = 500 + math.sin(radins / 57.29) * (10 + 2.5 * chain_distance)
            chainhead.y = 75 + math.cos(radins / 57.29) * (10 + 2.5 * chain_distance)
            camera.draw(chainhead)

        # boolans for throw/retriving chains
        if chainhead.x < 0 or chainhead.x > 1000 or chainhead.y > 700:
            chain_thrown_out_away = False

        if chain_distance <= 29 and chain_thrown_out == True:
            if chain_thrown_out_catchsomething == True:
                if value_caught != 0:
                    popped_up_word_counterdown = 1
                money += value_caught
                chain_thrown_out_catchsomething = False
            chain_thrown_out = False
            character.scale_by(0.833)
            frame2 = 0  # prevent "out of range" error
            weight_item_caught = speed + 5

        # 4-golds processing
        # catching items
        for gold in gold_middle:
            if gold.touches(chainhead) and chain_thrown_out_catchsomething == False:
                chain_thrown_out_away = False
                chain_thrown_out_catchsomething = True
                weight_item_caught = speed - 2
                pict_index = 1
                value_caught = 200
                gold_middle.remove(gold)
            camera.draw(gold)

        for gold in gold_small:
            if gold.touches(chainhead) and chain_thrown_out_catchsomething == False:
                chain_thrown_out_away = False
                chain_thrown_out_catchsomething = True
                weight_item_caught = speed
                pict_index = 0
                if item_gold_modifer == True:
                    value_caught = 125 + 25 * level
                else:
                    value_caught = 75
                gold_small.remove(gold)
            camera.draw(gold)

        for gold in gold_large:
            if gold.touches(chainhead) and chain_thrown_out_catchsomething == False:
                chain_thrown_out_away = False
                chain_thrown_out_catchsomething = True
                weight_item_caught = speed - 4
                pict_index = 2
                value_caught = 500
                gold_large.remove(gold)
            camera.draw(gold)

        for gold in gold_dimaond:
            if gold.touches(chainhead) and chain_thrown_out_catchsomething == False:
                chain_thrown_out_away = False
                chain_thrown_out_catchsomething = True
                weight_item_caught = speed + 4
                pict_index = 5
                if item_polisher == True:
                    value_caught = 900 + 75 * level
                else:
                    value_caught = 600 + 50 * level
                gold_dimaond.remove(gold)
            camera.draw(gold)

        for gold in gold_small_rock:
            if gold.touches(chainhead) and chain_thrown_out_catchsomething == False:
                chain_thrown_out_away = False
                chain_thrown_out_catchsomething = True
                weight_item_caught = speed - 2
                pict_index = 3
                value_caught = 20
                if item_rocks == True:
                    value_caught = value_caught * 4
                gold_small_rock.remove(gold)
            camera.draw(gold)

        for gold in gold_big_rock:
            if gold.touches(chainhead) and chain_thrown_out_catchsomething == False:
                chain_thrown_out_away = False
                chain_thrown_out_catchsomething = True
                weight_item_caught = speed - 4
                pict_index = 4
                value_caught = 60
                if item_rocks == True:
                    value_caught = value_caught * 4
                gold_big_rock.remove(gold)
            camera.draw(gold)

        for gold in gold_random_big:
            if gold.touches(chainhead) and chain_thrown_out_catchsomething == False:
                if chain_thrown_out_catchsomething == False:
                    weight_item_caught = speed + random.randint(-4, 5)
                chain_thrown_out_away = False
                chain_thrown_out_catchsomething = True
                pict_index = 6
                if item_luck == True:
                    value_caught = random.randint(500, 1000)
                else:
                    value_caught = random.randint(-300, 700)
                gold_random_big.remove(gold)
            camera.draw(gold)

        if chain_thrown_out_catchsomething == True:
            item = gamebox.from_image(500 + math.sin(radins / 57.29) * 2.5 * (chain_distance+10),
                                      75 + math.cos(radins / 57.29) * 2.5 * (chain_distance+10), picture_list[pict_index])
            camera.draw(item)

        # 6-score/time/environments display
        counter -= 1
        camera.draw(
            gamebox.from_text(850, 100, "Level:" + str(level) + " Money goal:" + str(money_goal[level - 1]), "arial",
                              24, "white"))
        camera.draw(gamebox.from_text(135, 25, "Your money:" + str(money), "arial", 24, "yellow"))
        camera.draw(gamebox.from_text(145, 55, "Time remaining:" + str(int(counter / 15)), "arial", 22, "black"))
        camera.draw(gamebox.from_color(500, 75, "black", 40000, 10))
        popped_up_word_counterdown += 1
        if popped_up_word_counterdown <= 15:
            if value_caught > 0:
                camera.draw(gamebox.from_text(300, 25, "+" + str(value_caught), "arial", 30, "green", bold=True))
            else:
                camera.draw(gamebox.from_text(300, 25,  str(value_caught), "arial", 30, "red", bold=True))

        elif popped_up_word_counterdown == 16:
            value_caught = 0

        # 7 transition/time runs out
        if counter == 0 :
            if money < money_goal[level-1]:
                scene = 4
            else:
                level += 1
                # shop generations
                random_list = [0, 1, 2, 3, 4, 5, 6]
                random.shuffle(random_list)
                shop_list = []
                shop_price = []
                shop_selection = 0
                shop_list.append(random_list[0])
                shop_list.append(random_list[1])
                shop_list.append(random_list[2])
                for stuff in shop_list:
                    if level != 12:
                        if stuff == 0:
                            shop_price.append(random.randint(25 + level * 10, 300 + level * 50))
                        elif stuff == 1:
                            shop_price.append(random.randint(400, 600 + level * 50))
                        elif stuff == 2:
                            shop_price.append(random.randint(50 + level * 20, 300 + level * 30))
                        elif stuff == 3:
                            shop_price.append(random.randint(200 + level * 20, 600 + level * 75))
                        elif stuff == 4:
                            shop_price.append(random.randint(50 + level * 20, 200 + level * 50))
                        elif stuff == 5:
                            shop_price.append(random.randint(50 + level * 30, 400 + level * 150))
                        else:
                            shop_price.append(random.randint(5 + level * 20, 200 + level * 10))
                    else:
                        shop_price.append(0)

                # set value to default

                speed = 5
                item_gold_modifer = False
                item_polisher = False
                item_lamp = False
                item_time = False
                item_luck = False
                item_rocks = False
                scene = 3
                chain_thrown_out_catchsomething = False
                chain_thrown_out = False
                character.scale_by(0.833)
                frame2 = 0  # prevent "out of range" error
                weight_item_caught = speed + 5
                value_caught = 0


    # scene 3 : the shop scene
    if scene == 3:
        picture = gamebox.from_image(500, 360, picture_list[11])
        picture.scale_by(0.8)
        camera.draw(picture)
        if shop_list[0] != 7:
            camera.draw(gamebox.from_image(170, 320, item_picture_list[shop_list[0]]))
        if shop_list[1] != 7:
            camera.draw(gamebox.from_image(500, 320, item_picture_list[shop_list[1]]))
        if shop_list[2] != 7:
            camera.draw(gamebox.from_image(850, 320, item_picture_list[shop_list[2]]))
        camera.draw(gamebox.from_text(500, 570, text_list[shop_list[shop_selection]], "arial", 20, "white"))
        if shop_list[shop_selection] != 7:
            camera.draw(gamebox.from_text(500, 620, "Cost:" + str(shop_price[shop_selection]), "arial", 22, "yellow"))
        camera.draw(
            gamebox.from_text(800, 50, "Next level:" + str(level) + " Money goal:" + str(money_goal[level - 1]), "arial",
                              24, "white"))
        camera.draw(gamebox.from_text(850, 25, "Your money:" + str(money), "arial", 24, "yellow"))
        if level == 12:
            camera.draw(gamebox.from_text(500, 100, "FINAL LEVEL, EVERYTHING FREE", "arial", 35, "yellow",bold=True))

        if pygame.K_LEFT in keys and shop_selection != 0 :
            shop_selection -= 1
        if pygame.K_RIGHT in keys and shop_selection != 2:
            shop_selection += 1
        if pygame.K_UP in keys:
            scene = 2
            level_generation(level)

        if pygame.K_SPACE in keys and shop_list[shop_selection] != 7:
            if shop_price[shop_selection] <= money:
                money -= shop_price[shop_selection]
                if shop_list[shop_selection] == 0:
                    item_gold_modifer = True
                if shop_list[shop_selection] == 1:
                    item_polisher = True
                if shop_list[shop_selection] == 2:
                    item_lamp = True
                if shop_list[shop_selection] == 3:
                    item_time = True
                if shop_list[shop_selection] == 4:
                    item_luck = True
                if shop_list[shop_selection] == 5:
                    speed = 7
                if shop_list[shop_selection] == 6:
                    item_rocks = True
                shop_list[shop_selection] = 7

        #animation
        frame += 1
        if frame == 7:
            frame = 0

        chainhead.image = sheet1[frame]
        if shop_selection == 0:
            chainhead = gamebox.from_image(170, 420, sheet1[frame])
        elif shop_selection == 1:
            chainhead = gamebox.from_image(500, 420, sheet1[frame])
        else:
            chainhead = gamebox.from_image(850, 420, sheet1[frame])
        camera.draw(chainhead)
        chainhead.scale_by(0.5)

    if scene == 4:
        camera.draw(gamebox.from_text(500, 350, "YOU DID NOT REACH YOUR GOAL", "arial", 40, "red"))

    camera.display()

def level_generation(level):
    # 5-golds generations
    global counter, gold_small_rock ,gold_large, gold_middle, gold_small, gold_random_big, gold_dimaond, gold_big_rock, chainhead
    gold_middle = []
    gold_small = []
    gold_large = []
    gold_dimaond = []
    gold_small_rock = []
    gold_big_rock = []
    gold_random_big = []
    # item evaluation
    if item_time == True:
        counter = 1200
    else:
        counter = 900

    if item_lamp == True:
        no_diamond = 3
    else:
        no_diamond = 0

    # generative algorithm
    if level % 4 == 0:
        no_diamond += 2
        no_diamond += int(level/3)
    if level % 2 == 0:
        no_random = 3
        no_random += int(level/2)
    else:
        no_random = 1
    if level >= 3:
        no_big = 1
        no_big += level//2
    else:
        no_big = 0
    if level >= 6:
        no_diamond += 2
        no_big += 2
        no_random += 2
        base = 1
    else:
        base = 0

    if level >= 8:
        no_diamond += 4
        no_big += 3
        no_random += 3
        base = 2
    if level == 12:
        no_diamond += 10
        base = 5
        no_big = 6
        no_random = 6

    if level >= 8:
        for c in range(0, random.randint(2,3)):
            item = gamebox.from_image(random.randint(50, 950), random.randint(200, 690), picture_list[0])
            gold_small.append(item)
        for c in range(0, 2):
            touched = True
            while touched:
                item = gamebox.from_image(random.randint(50, 950), random.randint(200, 690), picture_list[3])
                touched = False
                for evaluated_item in gold_small:
                    if item.touches(evaluated_item) == True:
                        touched = True
                for evaluated_item in gold_small_rock:
                    if item.touches(evaluated_item) == True:
                        touched = True
            gold_small_rock.append(item)

    else:
        for c in range(0, random.randint(5 + level // 2, 12 + level // 2)):
            item = gamebox.from_image(random.randint(50, 950), random.randint(200, 690), picture_list[0])
            gold_small.append(item)
        for c in range(0, random.randint(5, 7)):
            touched = True
            while touched:
                item = gamebox.from_image(random.randint(50, 950), random.randint(200, 690), picture_list[3])
                touched = False
                for evaluated_item in gold_small:
                    if item.touches(evaluated_item) == True:
                        touched = True
                for evaluated_item in gold_small_rock:
                    if item.touches(evaluated_item) == True:
                        touched = True
            gold_small_rock.append(item)



    for c in range(0, random.randint(5+level//2, 8+level//2)):
        touched = True
        while touched:
            item = gamebox.from_image(random.randint(50, 950), random.randint(200, 690), picture_list[1])
            touched = False
            for evaluated_item in gold_small:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_small_rock:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_middle:
                if item.touches(evaluated_item) == True:
                    touched = True
        gold_middle.append(item)

    for c in range(0, random.randint(1+level//4+base, 3+level//4+base)):
        touched = True
        while touched:
            item = gamebox.from_image(random.randint(50, 950), random.randint(275, 690), picture_list[4])
            touched = False
            for evaluated_item in gold_small:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_small_rock:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_middle:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_big_rock:
                if item.touches(evaluated_item) == True:
                    touched = True
        gold_big_rock.append(item)

    for c in range(0, random.randint(base, no_big)):
        touched = True
        while touched:
            item = gamebox.from_image(random.randint(50, 950), random.randint(200, 690), picture_list[2])
            touched = False
            for evaluated_item in gold_small:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_small_rock:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_middle:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_big_rock:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_large:
                if item.touches(evaluated_item) == True:
                    touched = True
        gold_large.append(item)

    for c in range(0, random.randint(base, no_diamond)):
        touched = True
        while touched:
            item = gamebox.from_image(random.randint(50, 950), random.randint(200, 690), picture_list[5])
            touched = False
            for evaluated_item in gold_small:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_small_rock:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_middle:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_big_rock:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_large:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_dimaond:
                if item.touches(evaluated_item) == True:
                    touched = True
        gold_dimaond.append(item)

    for c in range(0, random.randint(base, no_random)):
        touched = True
        while touched:
            item = gamebox.from_image(random.randint(50, 950), random.randint(200, 690), picture_list[6])
            touched = False
            for evaluated_item in gold_small:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_small_rock:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_middle:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_big_rock:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_large:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_dimaond:
                if item.touches(evaluated_item) == True:
                    touched = True
            for evaluated_item in gold_random_big:
                if item.touches(evaluated_item) == True:
                    touched = True
        gold_random_big.append(item)

ticks_per_second = 30
# keep this line the last one in your program
gamebox.timer_loop(ticks_per_second, tick)