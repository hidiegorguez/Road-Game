"""JUEGO CARRETERA"""

from multiprocessing.connection import Listener
from multiprocessing import Process, Manager, Value, Lock
import traceback
import sys
import random

#Definimos la resolución
W=800
H=450
SIZE=(W,H)

#Definimos nuestros jugadores
N=3
FIRST_PLAYER=0
SECOND_PLAYER=1
THIRD_PLAYER=2
SIDESSTR=["left","centre","right"]

#Coordenadas de posición
X=0
Y=1

#Movimiento de los conejos
STEP=25

class Conejo():
#Clase de los conejos, para indicar su tamaño, su posición y sus movimientos.    
    def __init__(self, side):
        self.side=side
        if side==FIRST_PLAYER:
            self.pos=[5*W/16,H-30]           
        if side==SECOND_PLAYER:
            self.pos=[W/2,H-30]
        if side==THIRD_PLAYER:
            self.pos=[11*W/16,H-30] 

    def get_pos(self):
        return self.pos

    def get_side(self):
        return self.side

    def moveDown(self):
        self.pos[Y]+=STEP
        if self.pos[Y]>H-30:
            self.pos[Y]=H-30
                   
    def moveUp(self):
        self.pos[Y]-=STEP
   
    def reiniciar_M(self):
        self.pos[Y]=H-30   
   
    def __str__(self):
        return f"C<{SIDESSTR[self.side]},{self.pos}>"
    

class Coche():
#Clase de los coches. Habrá tres tipos y tendrán posiciones distintas y velocidades aleatorias.    
    def __init__(self,n):
        l=[H/6,H/2,5*H/6-30]
        self.index=n         
        self.y=l[self.index]
        if self.index==0:
            self.x=random.randint(-1000,-1)             
            self.pos=[self.x,self.y]
            self.vel_x=random.randint(4,8)
            self.velocity=[self.vel_x, 0]
        if self.index==2:
            self.x=random.randint(-1000,-1)             
            self.pos=[self.x,self.y]
            self.vel_x=random.randint(4,8)
            self.velocity=[self.vel_x, 0] 
        if self.index==1:
            self.x=random.randint(-1000,-1)            
            self.pos=[self.x,self.y]
            self.vel_x=random.randint(4,8)
            self.velocity=[self.vel_x, 0] 
    
    def get_pos(self):
        return self.pos         
        
    def update(self):              
        self.pos[Y]=self.pos[Y] 
        self.pos[X]+=self.velocity[X]   
     
    def __str__(self):
        return f"C<{self.pos}>"


class Game():
    
    def __init__(self,manager):
        self.conejos=manager.list([Conejo(FIRST_PLAYER),Conejo(SECOND_PLAYER),Conejo(THIRD_PLAYER)])
        self.coches=manager.list([Coche(i) for i in range(N)])
        self.score=manager.list([0,0])
        self.running=Value('i',1)
        self.lock=Lock()

    def get_conejo(self,side):
        return self.conejos[side]

    def get_coche(self):
        for i in range(N): 
            return self.coches[i]

    def is_running(self):
        return self.running.value==1

    def stop(self):
        pos1=self.conejos[0].pos[1]
        pos2=self.conejos[1].pos[1]
        pos3=self.conejos[2].pos[1]
        if pos1<=0:
            self.winner=1
            self.running.value=0
        if pos2<=0:
            self.winner=2
            self.running.value=0
        if pos3<=0:
            self.winner=3
            self.running.value=0
                    
    def finish(self):
        self.running.value=0
        
    def moveDown(self,mon):
        self.lock.acquire()
        m=self.conejos[mon]        
        m.moveDown()
        self.conejos[mon]=m
        self.lock.release()
        
    def moveUp(self,mon):    
        self.lock.acquire()
        m=self.conejos[mon]        
        m.moveUp()
        self.conejos[mon]=m
        self.lock.release()
    
    def first_collide(self,mon):
    #Para cuando el primer conejo se choque con un coche
        self.lock.acquire()
        m = self.conejos[FIRST_PLAYER]
        m.reiniciar_M()
        self.conejos[FIRST_PLAYER]=m
        self.lock.release()
        
    def second_collide(self,mon):
    #Para cuando el segundo conejo se choque con un coche
        self.lock.acquire()
        m=self.conejos[SECOND_PLAYER]
        m.reiniciar_M()
        self.conejos[SECOND_PLAYER]=m
        self.lock.release()
        
    def third_collide(self,mon):
    #Para cuando el tercer conejo se choque con un coche
        self.lock.acquire()
        m = self.conejos[THIRD_PLAYER]
        m.reiniciar_M()
        self.conejos[THIRD_PLAYER]=m
        self.lock.release()
        
    def get_info(self):
    #Diccionario que nos de las posiciones de todos los elementos en pantalla
        pos_auto=[]
        for i in range(N):
            pos_auto.append(self.coches[i].get_pos())
        info={
            'pos_first_player': self.conejos[FIRST_PLAYER].get_pos(),
            'pos_second_player': self.conejos[SECOND_PLAYER].get_pos(),
            'pos_third_player': self.conejos[THIRD_PLAYER].get_pos(),
            'pos_coches': pos_auto,
            'score': list(self.score),
            'is_running': self.running.value==1
        }
        return info
   
    def move_coche(self):
        self.lock.acquire()
        for i in range(N):
            auto=self.coches[i]
            auto.update()
            pos=auto.get_pos()           
            if pos[X]>=SIZE[X]:
                auto=Coche(i)          
            self.coches[i]=auto
        self.lock.release()
        
    def __str__(self):     
        return f"G<{self.conejos[THIRD_PLAYER]}:{self.conejos[SECOND_PLAYER]}:{self.conejos[FIRST_PLAYER]}:{self.running.value}:Score:{self.score}>"

def player(side,conn,game):    
    try:
        print(f"starting player {SIDESSTR[side]}:{game.get_info()}")
        conn.send( (side,game.get_info()) )
        while game.is_running():
            command=""
            while command!="next":
                command=conn.recv()                
                if command=="down":
                    game.moveDown(side)
                elif command=="up":
                    game.moveUp(side)
                elif command=="quit":
                    game.finish()          
                elif command=="firstcollide" and side==0:
                    game.first_collide(side)
                elif command=="secondcollide" and side==1:
                    game.second_collide(side)
                elif command=="thirdcollide" and side==2:
                    game.third_collide(side)                     
                               
            if side==1 or side==2:
                game.move_coche()
                if game.stop():
                    return f"GAME OVER"
            conn.send(game.get_info())
            
    except:
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Game ended {game}")

def main(ip_address, port):
    manager=Manager()
    try:
        with Listener((ip_address,port),authkey=b'secret password') as listener:
            n_player=0
            players=[None,None,None]
            game=Game(manager)
            while True:
                print(f"accepting connection {n_player}")
                conn=listener.accept()
                players[n_player]=Process(target=player,args=(n_player,conn,game))
                n_player+=1
                if n_player==3:
                    players[0].start()
                    players[1].start()
                    players[2].start()
                    n_player=0
                    players=[None, None, None]
                    game=Game(manager)

    except Exception as e:
        traceback.print_exc()

if __name__=='__main__':
    ip_address="127.0.0.1"
    if len(sys.argv)>2:
        ip_address=sys.argv[1]
        port=int(sys.argv[2])    
    main(ip_address,port)
    
