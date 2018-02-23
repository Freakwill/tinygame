# -*- coding: utf-8 -*-

import random
import collections

from pytz import utc

from pymongo import MongoClient
from apscheduler.schedulers.blocking import *
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.events import *

import threading

lock = threading.Lock()


host = '127.0.0.1'
port = 27017
client = MongoClient(host, port)

jobstores = {
    'mongo': MongoDBJobStore(collection='job', database='game', client=client),
    'default': MemoryJobStore()
}
executors = {
    'default': ThreadPoolExecutor(10),
    'processpool': ProcessPoolExecutor(3)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}


class Unit:
    def __init__(self,name):
        self.name = name

    def __str__(self):
        return self.name

    def after_dead(self):
        pass

    def when_init(self):
        pass


class Hero(Unit):
    '''Hero: a role of the game
    name: the name of the hero
    life: the life of the hero
    damage: damage per second
    shield: the life of shield
    '''
    def __init__(self, name, life, damage, shield, speed):
        self.name = name
        self.life0 = self.life = life
        self.damage = damage
        self.shield0 = self.shield = shield
        self.speed = speed
        self._army = None

    @staticmethod
    def fromStr(s):
        # str -> Hero
        name, life, damage, shield, speed = s.split()
        return Hero(name, int(life), int(damage), int(shield), float(speed))
    
    def hit(self, other):
        assert isinstance(other, Army)
        with lock:
            if other:
                hero = other.random()
            else:
                raise ValueError('there is no hero left in the army %s'%other)
            print('%s 攻击 %s'%(self, hero))
            if not hero.shieldbreak():
                hero.shield -= self.damage
                if hero.shieldbreak():
                    print('%s 护盾破裂'%hero)
            else:
                hero.life -= self.damage
                if hero.isdead():
                    other -= hero
            return hero, other

    def shieldbreak(self):
        return self.shield <= 0

    def isdead(self):
        return self.life <= 0
    
    def reset(self):
        self.life = self.life0
        self.shield = self.shield0


class Army(Unit, collections.UserList):
    def __init__(self, name, heros):
        self.name = name
        self.data = heros

    def copy(self):
        import copy
        return copy.deepcopy(self)

    def random(self):
        return random.choice(self)

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

    @property
    def damage(self):
        return sum(hero.damage for hero in self)
 
    def isdead(self):
        return len(self) == 0



class Game(object):
    '''Game has 3 (principal) propteries
    title: title
    army1: army1
    army2: army2'''
    def __init__(self, title, army1=None, army2=None):
        self.title = title
        self.army1 = army1
        self.army2 = army2
        self._scheduler = None

    def init(self):
        # override the method to create a new game
        army1 = Army.fromStr('袁军', '袁绍 500 10 100 1;颜良 200 30 30 1;文丑 200 30 30 2')
        army2 = Army.fromStr('曹军', '曹操 800 30 200 2;荀彧 100 20 600 3;许褚 100 20 10 1')

        scheduler = BlockingScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

        for h in army1:
            scheduler.add_job(h.hit, 'interval', args=(army2,), seconds=h.speed, id=str(h))
        for h in army2:
            scheduler.add_job(h.hit, 'interval', args=(army1,), seconds=h.speed, id=str(h))

        # def check(army1, army2):
        #     if army1.isdead() or army2.isdead():
        #         scheduler.shutdown()
        # scheduler.add_job(check, 'interval', args=(army1, army2), seconds=5, id='check')

        def rmjob(evt):
            # remove a job
            hero, army = evt.retval
            if hero:
                if hero.isdead():
                    scheduler.remove_job(str(hero))
                    print('%s 阵亡'%hero)
                else:
                    print('%s 还剩余生命值 %d'%(hero, hero.life))
                if army.isdead():
                    try:
                        scheduler.shutdown()
                    except RuntimeError:
                        print('%s 全军覆没'%army)

        scheduler.add_listener(rmjob, EVENT_JOB_EXECUTED)
        self._scheduler = scheduler


    def start(self):
        try:
            self._scheduler.start()
        except ValueError as v:
            print(v)
        finally:
            client.close()


if __name__ =="__main__":

    threeKingdoms = Game('官渡之战：东汉末年三大战役之一')
    threeKingdoms.init()
    threeKingdoms.start()
    


