# tinygame
create a tiny game.

## Main objects

Hero: name, life, damage, shield
Army: name, list of heros

## example

```python
# create an army
army1 = Army.fromStr('袁军', '袁绍 500 10 100;颜良 200 30 30;文丑 200 30 30')
army2 = Army.fromStr('曹军', '曹操 800 30 200;荀彧 100 20 600;许褚 100 20 10')
army2 += Hero.fromStr('关羽 200 20 20')  # a new hero joins into army2

# create a game (the romantic history of three kingdoms)
threeKingdoms = Game('官渡之战：东汉末年三大战役之一', army1, army2)
threeKingdoms.bgm ='BGM: 滚滚长江东逝水......'
threeKingdoms.start()

army1 = Army.fromStr('大日本帝国太平洋联合舰队', '山本五十六 200 20 20; 南云忠一 50 10 10; 山口多闻 20 20 10')
army2 = Army.fromStr('美利坚太平洋特混舰队', '尼米兹 400 20 20; 弗莱彻 100 10 10; 罗斯福 30 10 10')
pacificWar = Game('第二次世界大战太平洋海战 --- 人类历史上规模最大的海战', army1, army2)
pacificWar.weapons = ('鱼雷', '舰炮', '深水炸弹', '舰载机', '轰炸机', '导弹')
pacificWar.bgm = 'BGM: ...'
pacificWar.start()
```

## motivation
1. culture output
2. entertainment and enjoyment
3. learning the history
