from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random


N = 5
NPROD = 10

def delay(factor = 3):
    sleep(0.05)

def add_data(buffer, pid, data, mutex):
    mutex.acquire() #Para impedir que otros procesos accedan al buffer a la vez
    try:
        buffer[pid] += data
        print (f" El productor {current_process().name} produce {buffer[pid]}")
        delay(6)
    finally:
        mutex.release()

def get_data(buffer, resultado, empty, mutex):
    mutex.acquire() #Para impedir que otros procesos accedan al buffer a la vez
    try:
        minimo=min(filter(lambda x:x>=0,buffer))
        print(f'Consumidor consume {minimo}')
        posicionmin =list(buffer).index(minimo)
        resultado.append(buffer[posicionmin])
        if filter(lambda x:x!=-1,buffer)==[]:
            print(resultado)
        empty[posicionmin].release()
        delay(6)
    finally:
        mutex.release()

def terminado(buffer, mutex)->bool:
    mutex.acquire() #Para impedir que otros procesos accedan al buffer a la vez
    for i in buffer:
        if i!=-1:
            mutex.release()
            return False
    mutex.release()
    return True


def producer(buffer, empty, non_empty, mutex):
    '''Cada productor produce N productos en orden creciente aleatoriamente'''
    for v in range(N):
        delay(6)
        empty.acquire()
        data=random.randint(1,100)
        add_data(buffer, int(current_process().name.split('_')[1]), data, mutex)
        non_empty.release()
    empty.acquire()
    mutex.acquire() #Para impedir que otros procesos accedan al buffer a la vez
    buffer[int(current_process().name.split('_')[1])]=-1 
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
        print(list(buffer))
        non_empty.acquire()
    print('La lista ordenada de todos los productos es {}'.format(resultado))
    
def main():
    buffer = Array('i',[-2 for _ in range(NPROD)])
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
        
        
        
   