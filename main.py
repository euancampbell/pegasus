from configs.config import Config

from modules.jsonformat import jsonformat
from modules.sqlformat import sqlformat
from modules.f import f
from modules.listformat import listformat
from modules.sql import sql

import os
import sys
from os import listdir
from os.path import isfile, join
from importlib import reload 

while True:
    print('')
    # input
    text_input = input('command: ')
    command=text_input.split(' ')[0]
    try:
        param=text_input.split(' ')[1]
    except:
        param=None

    # load everything
    config = Config()

    if command=='help':
        current_path=os.path.dirname(os.path.abspath(__file__)) + '/modules'
        files = [f[:-3] for f in listdir(current_path) if isfile(join(current_path, f)) and '__init__' not in f]
        for fil in files:
            print(fil)
            try:
                instance = globals()[fil]()
                description = instance.__doc__
                
            except KeyError:
                description = f'Unavailable: Not imported in main'
            print(f' - {description}')
            
    elif command=='exit':
        sys.exit()
    elif command=='reload':
        continue
    else:
        try:
            module = globals()[command](command)
            module.__run__(param)
        except KeyError:
            print('Unavailable: Not imported in main')
        
        
    


    
