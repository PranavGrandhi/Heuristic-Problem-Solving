import OptimalTouring as Game

x = Game.OptimalTouring("sites.txt")
i = 1
while x.getTime() < x.getDay()*1440:
    x.sendMove(siteId=i)
    x.sendMove(delayTime=240)
    i += 1
x.settlement()
