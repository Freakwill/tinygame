# -*- coding: utf-8 -*-
# Designer：Haojie Ma 马豪杰

import random
import time

class Unit:
    def __init__(self,name):
        self.name = name

    def __str__(self):
        return self.name


class Hero(Unit):
    '''Hero: a role of the game
    name: the name of the hero
    life: the life of the hero
    damage: damage per second
    shield: the life of shield
    '''
    def __init__(self, name, life, damage, shield):
        self.name = name
        self.life0 = self.life = life
        self.damage = damage
        self.shield0 = self.shield = shield

    @staticmethod
    def fromStr(s):
        # str -> Hero
        name, life, damage, shield = s.split()
        return Hero(name, int(life), int(damage), int(shield))
    
    def hit(self, other):
        other.life -= self.damage

    def shieldbreak(self):
        return self.shield <= 0

    def isdead(self):
        return self.life <= 0
    
    def reset(self):
        self.life = self.life0
        self.damage = self.damage0
        
import collections

class Army(Unit, collections.UserList):
    def __init__(self, name, heros):
        self.name = name
        self.data = heros

    def copy(self):
        import copy
        return copy.deepcopy(self)

    @staticmethod
    def fromStr(name, s):
        # str -> Army
        heros = s.split(';')
        return Army(name, [Hero.fromStr(h) for h in heros])


    def __iadd__(self, other):
        if isinstance(other, Hero):
            self.append(other)
        else:
            self.extend(other)
        return self

    def __add__(self, other):
        cpy = self.copy()
        cpy += other
        return cpy

    def __isub__(self, other):
        if isinstance(other, Hero):
            self.remove(other)
        else:
            for h in other:
                self.remove(h)
        return self

    def __sub__(self, other):
        cpy = self.copy()
        cpy -= other
        return cpy

    # def shield(self):
    #     return sum(hero.shield for hero in self.heros)

    @property
    def damage(self):
        return sum(hero.damage for hero in self)
 
    def hit(self, other):
        # 军队之间进攻核心程序
        # 随机锁定敌方英雄攻击
        hero = random.choice(other)
        print('%s 受到攻击'%hero)
        if not hero.shieldbreak():
            # 护盾在，则由护盾抵抗伤害
            hero.shield -= self.damage
            if hero.shieldbreak():
                # 护盾破裂，将不能再使用，但英雄不会死亡
                print('%s 护盾破裂'%hero)
        else:
            # 护盾不在，由英雄生命抵抗伤害
            hero.life -= self.damage
            if hero.isdead():
                # 英雄死亡
                other -= hero
                print('%s 阵亡'%hero)
            else:
                print('%s 还剩余生命值 %d'%(hero, hero.life))

    def isdead(self):
        return len(self) == 0


_defaultWeapons = ('弓箭', '剑', '刀', '矛', '弩')
class Game(object):
    '''Game has 3 (principal) propteries
    title: title
    army1: army1
    army2: army2'''
    def __init__(self, title, army1, army2):
        self.title = title
        self.army1 = army1
        self.army2 = army2
        self.bgm = ''
        self.weapons = _defaultWeapons

    def start(self):
        weapons = self.weapons
        army1, army2 = self.army1, self.army2
        print(self.title)
        print(self.bgm)
        k = 0
        while True:
            time.sleep(1)
            k += 1
            print('第 %d 回合:'%k)
            if random.random() < 1:
                weapon = random.choice(weapons)
                print('%s 用 %s 攻击 %s'%(army1, weapon, army2))
                army1.hit(army2)

            if random.random() < .5:
                weapon = random.choice(weapons)
                print('%s 用 %s 攻击 %s'%(army2, weapon, army1))
                army2.hit(army1)

            if army1.isdead():
                print('%s 全军覆没'%army1)
                print('%s 剩下 %d 个英雄'%(army2, len(army2)))
                break
            if army2.isdead():
                print('%s 全军覆没'%army2)
                print('%s 剩下 %d 个英雄 '%(army1 , len(army1)))
                break


if __name__ =="__main__":
    army1 = Army.fromStr('袁军', '袁绍 500 10 100;颜良 200 30 30;文丑 200 30 30')
    army2 = Army.fromStr('曹军', '曹操 800 30 200;荀彧 100 20 600;许褚 100 20 10')
    army2 += Hero.fromStr('关羽 200 20 20')

    threeKingdoms = Game('官渡之战：东汉末年三大战役之一', army1, army2)
    threeKingdoms.bgm ='BGM: 滚滚长江东逝水......'
    threeKingdoms.start()


