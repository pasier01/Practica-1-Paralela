from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from time import sleep
import random


N = 5
NPROD = 3

def delay(factor = 3):
    sleep(0.05)

def get_data(buffer, resultado, empty, mutex):
    mutex.acquire() #Para impedir que otros procesos accedan al buffer a la vez
    try:
        buffer_usable=[]
        for listaprods in buffer:
            if listaprods!=[-1]:
                buffer_usable.append(filter(lambda x: x>=0,listaprods))
            else:
                buffer_usable.append([-1])
        minimo=min(filter(lambda x: x!=-1,map(lambda x:x[0],buffer_usable)))
        print(f'Consumidor consume {minimo}')
        posicionmin =list(map(lambda x:x[0],buffer_usable)).index(minimo)
        empty[posicionmin].release()
        delay(6)
    finally:
        mutex.release()

def terminado(buffer, mutex)->bool:
    mutex.acquire() #Para impedir que otros procesos accedan al buffer a la vez
    for i in buffer:
        if i!=[-1]:
            mutex.release()
            return False
    mutex.release()
    return True


def producer(buffer, empty, non_empty, mutex):
    '''Cada productor produce N productos en orden creciente aleatoriamente'''
    i=int(current_process().name.split('_')[1])
    bufferproductor=buffer[i]
    for v in range(N):
        delay(6)
        empty.acquire()
        data=random.randint(1,100)
        if v==0:
            bufferproductor[v]=data
        else:
            bufferproductor[v]=bufferproductor[v-1]+data
        buffer[i]=bufferproductor
        print (f" El productor {current_process().name} produce {bufferproductor[v]}")
        print(buffer)
        delay(6)
        non_empty.release()
    empty.acquire()
    mutex.acquire() #Para impedir que otros procesos accedan al buffer a la vez
    buffer[v]=-1 
    mutex.release()
    non_empty.release()
    
def consumer(buffer, resultado, empty, non_empty, mutex):
    '''Cada productor produce un producto. El consumidor coger el mínimo de 
    esos productos y lo consume. Así hasta que consumen todos los productos de 
    todos los consumidores'''
    for w in range(NPROD):
        non_empty.acquire()
    while terminado(buffer,mutex)==False:
        delay(6)
        get_data(buffer, resultado, empty, mutex)
        print(buffer)
        non_empty.acquire()
    print('La lista ordenada es {}'.format(resultado))
    
def main():
    buffer = [[-2 for _ in range(N)] for _ in range(NPROD)]
    print(f'almacén inicial: {list(buffer)}')
    resultado = []
    non_empty = Semaphore(0)
    empty = [BoundedSemaphore(1) for i in range(NPROD)]
    mutex = Lock()
    prodlst = [Process(target=producer,
                        name=f'prod_{i}',
                        args=(buffer, empty[i], non_empty, mutex))
                for i in range(NPROD)]
    onlyconsumer = Process(target=consumer,args=(buffer, resultado,
                                              empty, non_empty, mutex))
    
    for p in prodlst+[onlyconsumer]:
       p.start()
       
    for p in prodlst+[onlyconsumer]:
        p.join()

if __name__ == '__main__':
    main()
  
        
        