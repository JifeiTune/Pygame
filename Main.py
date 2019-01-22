import pygame,sys
import time
import random
import math
"""
这是一个躲避游戏，用户需要使用鼠标控制游戏角色躲避不断增加和移动的子弹的射击
坚持不被击中的秒数即为游戏得分
"""

#窗口大小
WindowSize=(800,600)
#时钟对象
clock=pygame.time.Clock()
#系统初始化
pygame.init()
#隐藏鼠标
pygame.mouse.set_visible(0)
#设置窗口大小
screen=pygame.display.set_mode(WindowSize)
#设置标题
pygame.display.set_caption("Beat")
#载入背景图片
bg=pygame.image.load("res/TitleBackground.jpg").convert()
pygame.display.update()
#载入角色图片
playerImg=pygame.image.load("res/player.png").convert_alpha()
#载入子弹，等待态时使用两张图片切换达到闪动效果
waitAImg=pygame.image.load("res/waitA.png").convert_alpha()
waitBImg=pygame.image.load("res/waitB.png").convert_alpha()
bulletImg=pygame.image.load("res/bullet.png").convert_alpha()
font=pygame.font.SysFont("arial", 30)
#游戏结束画面
overImg=pygame.image.load("res/over.png").convert_alpha()
#背景音乐
pygame.mixer.music.load("res/bgm.mp3")
#子弹射击音效
bsound=pygame.mixer.Sound("res/bullet.wav")
#游戏结束音效
overSound=pygame.mixer.Sound("res/over.wav")
#子弹所有的速度选择
allSpeed={0:150,1:200,2:300,3:400,4:450,5:500,6:600}

#定义一个子弹精灵
class bullet(pygame.sprite.Sprite):
    #构造函数，mx和my分别是鼠标坐标
    def __init__(self):
        mx,my=pygame.mouse.get_pos()
        pygame.sprite.Sprite.__init__(self)
        #载入图片，等待态时为两张图片交替显示
        self.choice=0
        self.image=waitAImg
        #随机初始位置
        self.px=random.randint(0,800)
        self.py=random.randint(0,600)
        self.rect=self.image.get_rect()
        self.rect.topleft=self.trans((self.px,self.py))
        #随机生成速度，单位是像素/s
        self.speed=allSpeed[random.randint(0,6)]
        #计算单位向量，方向由精灵生成的初始位置指向当前鼠标位置
        self.vector=bullet.calV((self.px,self.py),(mx,my))
        #等待部分，子弹一出来应该先停留一小段时间再发射，留给玩家准备时间
        self.wait=True#是否处于等待态
        self.crtime=time.time()#创建时的unix时间

    #根据自身长宽和中心位置求左上角位置
    def trans(self,pos):
        return (pos[0]-self.image.get_width()/2,pos[1]-self.image.get_height()/2)

    #移动,dur是距上一帧刷新经过的毫秒时间
    def update(self,dur):
        #如果已经越界，则移除
        if(self.px<0 or self.px>800 or self.py<0 or self.py>600):
            self.kill()
        #子弹每秒有一定的概率改变方向，跟踪角色，预设概率20%
        if(random.random()<=0.2*dur/1000):
            mx, my = pygame.mouse.get_pos()
            self.vector = bullet.calV((self.px, self.py), (mx, my))
        #不处于等待态才更新位置
        elif(not self.wait):
            #计算x与y轴上的偏移量
            cx = self.speed * self.vector[0] * (dur / 1000)
            cy = self.speed * self.vector[1] * (dur / 1000)
            self.px += cx
            self.py += cy
            #移动
            self.rect.topleft = self.trans((self.px, self.py))
        #等待1.5秒设为活动态，播放发射音效，替换图片
        elif(time.time()-self.crtime>1.5):
            self.wait=False
            bsound.play()
            self.image=bulletImg
        else:
            #两张图片交替显示，每10帧切换一次
            self.choice+=1
            self.choice%=20
            if(self.choice<10):
                self.image=waitAImg
            else:
                self.image=waitBImg


    #根据起点和终点计算单位向量
    @classmethod
    def calV(cls,be,ed):
        v=(ed[0]-be[0],ed[1]-be[1])
        length=math.sqrt(v[0]**2+v[1]**2)
        ans=(v[0]/length,v[1]/length)
        return ans

#玩家精灵
class player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #载入图片
        self.image=playerImg
        #初始位置跟随鼠标
        self.px,self.py=pygame.mouse.get_pos()
        self.rect=self.image.get_rect()
        self.rect.topleft=self.trans((self.px,self.py))

    # 根据自身长宽和中心位置求左上角位置
    def trans(self, pos):
            return (pos[0] - self.image.get_width() / 2, pos[1] - self.image.get_height() / 2)

    #位置始终跟随鼠标
    def update(self):
        self.px, self.py = pygame.mouse.get_pos()
        self.rect.topleft = self.trans((self.px, self.py))

#圆圈渐变效果
class circle(pygame.sprite.Sprite):
    def __init__(self,pos):
        pygame.sprite.Sprite.__init__(self)
        self.lastTime=time.time()#上次更新时间
        self.pos=pos#出现的位置
        self.width=random.randint(1,10)#宽度
        #是增大还是减小
        if(random.randint(0,1)==0):
            self.increase=True#增大
            self.radius=self.width
            self.change=random.randint(1,5)#半径每次增大量
            self.MAX=random.randint(30,500)#最大半径
        else:
            self.increase=False#减小
            self.radius=random.randint(30,500)
            self.change=random.randint(-5,-1)#半径每次增大量

    def update(self):
        self.lastTime=time.time()
        #每次更新变色
        self.radius+=self.change
        if((self.increase and self.radius>self.MAX) or ((not self.increase) and self.radius<=self.width) ):
            self.kill()
        else:
            color=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
            pygame.draw.circle(screen, color, (self.pos[0], self.pos[1]),self.radius, self.width)

#游戏结束异常
class GameOver(Exception):
    pass

#整个游戏的循环
while(True):
    # 每秒期望生成的子弹个数，会随时间不断增大
    bNum = 1
    # 建立子弹精灵组
    bgroup = pygame.sprite.Group()
    #圆圈效果精灵组
    cirgroup=pygame.sprite.Group()
    # 建立玩家精灵
    pl=player()
    # 开始游戏时的时间
    begin = time.time()
    # 上一次增加子弹时的秒数
    last = 0
    # 播放背景音乐
    pygame.mixer.music.play()
    #开始一轮游戏
    while(True):
        #每秒60帧，并记录上次刷新至今时间
        interval=clock.tick(60)
        #游戏开始至今的时间
        dur=time.time() - begin
        screen.blit(bg, (0, 0))
        #随机生成子弹
        intdur=int(dur)
        if(intdur%15==0 and intdur!=last):
            last=intdur
            bNum+=1#每15秒增加一次每秒生成的子弹数
        #根据期望的个数概率添加
        if(random.random()<=bNum*interval/1000):
            newB=bullet()
            bgroup.add(newB)
            #高速子弹以自己为中心产生一个变化的圆圈
            if(newB.speed>=500):
                cirgroup.add(circle((newB.px,newB.py)))

        bgroup.update(interval)
        bgroup.draw(screen)
        cirgroup.update()
        pl.update()
        screen.blit(pl.image,pl.rect)
        #显示游戏开始至今已经过秒数
        dur="Score: %.2f" % (dur)#保留两位小数
        text=font.render(dur, True,(255, 255, 255))
        screen.blit(text,(780-text.get_width(),20))#显示在右上角
        #更新画面
        pygame.display.update()
        #碰撞检测，如果子弹击中玩家，抛出异常
        try:
            list=pygame.sprite.spritecollide(pl,bgroup,False)
            #存在碰撞，但还得判断子弹是否处于活动态，处于活动态才判为游戏结束
            if(len(list)!=0):
                for v in list:
                    if(not v.wait):
                        raise GameOver
        except GameOver:
            #绘制游戏结束画面
            screen.blit(overImg, (0,0))  # 显示在画面中间
            gf = pygame.font.SysFont("arial", 60)
            sstr = "Your score: " + dur
            text = font.render(sstr, True, (255, 0, 0))
            screen.blit(text, (20, 20))  # 显示在左上
            pygame.display.update()
            #停止播放背景音乐，播放游戏结束音效
            pygame.mixer.music.stop()
            overSound.play()
            break
        else:
            #事件处理
            for event in pygame.event.get():
                #点击X键退出游戏
                if(event.type==pygame.QUIT):
                    sys.exit()
                #按下ESC键退出游戏
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
    #运行到此处说明游戏结束，处理重玩按键
    wait=True
    while(wait):
        for event in pygame.event.get():
            #点击X键退出游戏
            if (event.type == pygame.QUIT):
                sys.exit()
            #R键重玩，ESC退出
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    wait=False
                    break
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()