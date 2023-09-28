"""JUEGO CARRETERA"""

from multiprocessing.connection import Client
import traceback
import pygame
import sys, os
import random
import time

#Definimos colores que nos servirán mas adelante
WHITE=(255,255,255)
RED=(190,0,0)
BLUE=(0,0,190)
GREEN=(0,190,0)

#Definimos la resolución
W=800
H=450
SIZE=(W,H)

#Definimos los jugadores
FIRST_PLAYER=0
SECOND_PLAYER=1
THIRD_PLAYER=2
SIDESSTR=["left","centre","right"]
SIDES=["down","up"]

#Definimos las frames por segundo
FPS=120

class Conejo():
#Clase de los conejos, para indicar su tamaño, su posición y sus movimientos.     
    def __init__(self,side):        
        self.side=side
        self.pos=[None,None]

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def set_pos(self,pos):
        self.pos=pos

    def __str__(self):
        return f"C<{SIDES[self.side], self.pos}>"

class Coche():
#Clase de los coches. Habrá tres tipos y tendrán posiciones distintas y velocidades aleatorias.    
    def __init__(self,n):        
        self.pos=[None,None,None]
        self.divider=n

    def get_pos(self):
        return self.pos
        
    def get_index(self):
        return self.divider

    def set_pos(self,pos):
        self.pos = pos

    def __str__(self):
        return f"C<{self.pos}>"

class Game():
    
    def __init__(self):
        self.conejos=[Conejo(i) for i in range(3)]
        self.coche=[Coche(i) for i in range(3)]
        self.running=True

    def get_conejo(self,side):
        return self.conejos[side]

    def set_pos_conejo(self,side,pos):
        self.conejos[side].set_pos(pos)

    def get_coche(self,i): 
        return self.coche[i]
  
    def set_pos_coche(self,i,pos):
        self.coche[i].set_pos(pos)

    def update(self, gameinfo):
        self.set_pos_conejo(FIRST_PLAYER, gameinfo['pos_first_player'])
        self.set_pos_conejo(SECOND_PLAYER, gameinfo['pos_second_player'])
        self.set_pos_conejo(THIRD_PLAYER, gameinfo['pos_third_player'])
        info_auto=gameinfo['pos_coches']
        for i in range(3):
            Auto_i=info_auto[i]
            self.set_pos_coche(i,Auto_i)
        self.running=gameinfo['is_running']

    def is_running(self):
        return self.running

    def finish(self):
        self.running=False

    def __str__(self):
        for i in range(3):
            return f"G<{self.conejos[SECOND_PLAYER]}:{self.conejos[FIRST_PLAYER]}:{self.coche[i]}>"

class Conejo_Draw(pygame.sprite.Sprite):
    
    def __init__(self,mon,ind):
        super().__init__()
        self.conejo=mon
        self.index=ind
        self.image=pygame.image.load(f'conejo{self.index}.png')
        self.image=pygame.transform.scale(self.image,(35,50))
        self.image.set_colorkey(WHITE)
        self.rect=self.image.get_rect()
        self.update()
        
    def update(self):        
        pos = self.conejo.get_pos()
        self.rect.centerx, self.rect.centery=pos  
        
    def draw(self, screen):
        screen.window.blit(self.image, self.rect)
   
    def __str__(self):
        return f"S<{self.mon}>"


class Coche_Draw(pygame.sprite.Sprite):
    
    def __init__(self,auto):
        super().__init__()
        self.coche=auto
        y = self.coche.get_index()
        self.image=pygame.image.load(f'coche{y+1}.png')
        self.image=pygame.transform.scale(self.image,(70,50))
        self.image.set_colorkey(WHITE)
        self.rect=self.image.get_rect()
        self.update()

    def update(self):
        pos=self.coche.get_pos()
        print(pos)
        self.rect.centerx,self.rect.centery=pos
        
    def draw(self,screen):
        screen.window.blit(self.image,(self.ball.pos))
       
    def __str__(self):
        return f"P<{self.auto.pos}>"
   
class Display():
    
    def __init__(self,game):        
        self.game=game
        self.conejos=[self.game.get_conejo(i) for i in range(3)]
        self.conejosD=[Conejo_Draw(self.game.get_conejo(i),i+1) for i in range(3)]
        self.cocheD=[Coche_Draw(self.game.get_coche(i)) for i in range(3)]
        self.all_sprites=pygame.sprite.Group()
        self.conejo_group=pygame.sprite.Group()
        self.coche_group=pygame.sprite.Group()
        for conejo in self.conejosD:
            self.all_sprites.add(conejo)
            self.conejo_group.add(conejo)
        for coche in self.cocheD:
            self.all_sprites.add(coche)
            self.coche_group.add(coche)
        self.screen=pygame.display.set_mode(SIZE)
        self.clock=pygame.time.Clock()  #FPS
        self.background=pygame.image.load('road.png')
        self.background=pygame.transform.scale(self.background,SIZE)
        pygame.init()
     
    def analyze_events(self,side):        
        events=[]        
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    events.append("quit")
                elif event.key==pygame.K_DOWN:
                    events.append("down")
                elif event.key==pygame.K_UP:
                    events.append("up")
            elif event.type==pygame.QUIT:
                events.append("quit")        
        #if pygame.sprite.groupcollide(self.conejosD,self.cocheD,False,False):            
        if pygame.sprite.spritecollideany(self.conejosD[0],self.cocheD):
            events.append("firstcollide")
            
        if pygame.sprite.spritecollideany(self.conejosD[1],self.cocheD):
           events.append("secondcollide") 
                         
        if pygame.sprite.spritecollideany(self.conejosD[2],self.cocheD):
           events.append("thirdcollide")  
                 
        return events

    def refresh(self):
        
        self.all_sprites.update()
        self.screen.blit(self.background,(0,0))
        font=pygame.font.Font(None,74)
        aux=False
        
        if self.conejos[0].pos[1]<=0:
            font2=pygame.font.Font(None,50) 
            text1=font2.render(f"PLAYER 1 WINS!",1,BLUE)
            self.screen.blit(text1,((5*W/16)-150,150))
            aux=True
        if self.conejos[1].pos[1]<=0:
            font2=pygame.font.Font(None,50) 
            text1=font2.render(f"PLAYER 2 WINS!",1,RED)
            self.screen.blit(text1,((W/2)-150,150))
            aux=True
        if self.conejos[2].pos[1]<=0:
            font2=pygame.font.Font(None,50) 
            text1=font2.render(f"PLAYER 3 WINS!",1,GREEN)
            self.screen.blit(text1,((11*W/16)-150,150))
            aux=True
        self.all_sprites.draw(self.screen)
        pygame.display.flip()
        if aux:
            time.sleep(6)

    def tick(self):
        self.clock.tick(FPS)

    @staticmethod
    def quit():
        pygame.quit()

def main(ip_address,port):    
    try:
        with Client((ip_address,port),authkey=b'secret password') as conn:
            game=Game()
            side,gameinfo=conn.recv()
            print(f"I am playing {SIDESSTR[side]}")
            game.update(gameinfo)
            display=Display(game)
            while game.is_running():
                events=display.analyze_events(side)
                for ev in events:
                    conn.send(ev)
                    if ev=='quit':
                        game.finish()
                conn.send("next")
                gameinfo=conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__=='__main__':
    ip_address="127.0.0.1"
    if len(sys.argv)>2:
        ip_address=sys.argv[1]
        port=int(sys.argv[2])    
    main(ip_address,port)
