import logging
import json, pickle

from datetime import datetime as dt
    
def configure_loggers( loggers, logging_level, log_here= True, log_to= None):
    """
    Streamline configuring loggers for a script / notebook, so that a single
    function call takes care of the boilerplate below.
    
    :param loggers: list of loggers (allow multiple for extendability - e.g. multiple repos)
    :param logging_level: logging module type `level` e.g. logging.DEBUG
    :param log_here: bool whether to display in console / notebook
    :param log_to: str name of file to log to
    :return: list of loggers, now configured and ready to use
    """    
    spc=' '
    formatter = logging.Formatter(
        f'%(asctime)s | %(levelname)s @ %(name)s\n{spc*20}| %(message)s', '%Y-%m-%d %H:%M:%S'
    )
    
    if log_here:
        chandler = logging.StreamHandler()
        chandler.setLevel( logging_level)
        chandler.setFormatter( formatter)
        _ = [x.addHandler( chandler) for x in loggers]
    
    if log_to is not None:
        phoebe = logging.FileHandler( log_to)
        phoebe.setLevel( logging_level)
        phoebe.setFormatter( formatter)
        _ = [x.addHandler( phoebe) for x in loggers]
        
    elif not log_here:
        fname = inspect.stack()[0].function
        print(f'{fname} did not add any handlers!')
    
    _ = [x.setLevel( logging_level) for x in loggers]
    
    return loggers

def now_string( short= False):
    """
    Provide a string version of datetime for tagging files / folders.
    
    :param short: whether to only provide YYMMDD string, defaults to no
    :return: string in the format YYYY-DD-MM_HH-mm-ss
    """
    if short:
        return dt.strftime( dt.now(), '%y%m%d')
    else:
        return dt.strftime( dt.now(), '%Y-%m-%d_%H-%M-%S')
    
def none():
    """
    Utility for always returning 0, for use with defaultdict as a missing key
    default value.
    """
    return 0

def from_json( file_path, encoding= 'utf-8'):
    with open( file_path, 'r', encoding= encoding) as inn:
        dictionary = json.load( inn)
    return dictionary   

def to_json( dictionary, file_path, encoding= 'utf-8'):
    with open( file_path, 'w', encoding= encoding) as oot:
        json.dump(dictionary, oot, indent= 5)

def to_pickle( object_, file_path):
    with open( file_path, 'wb') as oot:
        pickle.dump( object_, oot)

def from_pickle( file_path):
    with open( file_path, 'rb') as inn:
        return pickle.load( inn)

def update_dictionary_values( dict_, fun):
    """
    We'll be using a dictionary for answers to queries, may be useful to
    e.g. do stats over results or apply a parsing function..
    """
    for key, val in dict_.items():
        dict_[ key] = fun( val)

def update_nested_dictionary_values( dict_, fun):
    """
    We'll be using a nested dictionary for subjects and their constituent parts, 
    and for storing answers, may be useful utility to e.g. apply a parsing 
    function etc.
    """
    for k1 in dict_.keys():
        for k2, val in dict_[k1].items():
            dict_[ k1][ k2] = fun( val)    
    
def from_text( file_path, encoding= 'utf-8', how= 'lines'):
    """
    Just a copied utility from other project, to load tokens to acces OpenAI / HF.
    """
    if how == 'lines':
        lines= []
        exceptions = []
        line_num = 0
        with open( file_path, 'r', encoding= encoding) as inn:
            while True:
                try:
                    line = inn.readline()
                    lines.append( line)
                    line_num += 1
                except Exception:
                    # usually an encoding error..
                    exceptions.append( line_num)
                    line_num += 1
                if not line:
                    break
        return lines, exceptions
    else:
        with open( file_path, 'r', encoding= encoding) as inn:
            text = inn.read()
        return [text], []