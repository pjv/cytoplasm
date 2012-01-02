'''
These are some utilites used when writing and handling interpreters.
'''

import shutil
from cytoplasm import configuration
from cytoplasm.errors import InterpreterError

def interpreted_filename(file):
    "Intelligently return the interpreted filename of a file."
    # get the last suffix:
    suffix = file.split(".")[-1]
    # if the suffix is in interpreters.keys() the destination is everything but that last suffix
    if suffix in configuration.get_config().interpreters.keys():
        return ".".join(file.split(".")[:-1])
    # otherwise, it's the whole thing.
    else:
        return file

def SaveReturned(fn):
    '''Some potential interpreters, like Mako, don't give you an easy way to save to a destination.
    In these cases, simply use this function as a decorater.'''
    def InterpreterWithSave(source, destination, **kwargs):
        # destination should _always_ be a file or file-like object.
        # pass **kwargs to this function.
        destination.write(fn(source, **kwargs))
    return InterpreterWithSave

def default_interpreter(source, destination, **kwargs):
    "Copy from source to destination. Use this if no other interpreters match the file."
    # destination is always a file object, so you can copyfileobj.
    with open(source) as source_file:
        shutil.copyfileobj(source_file, destination)

def interpret(source, destination, **kwargs):
    "Interpret a file to a destination with an interpreter according to its suffix."
    # open the destination and write to it.
    with open(destination, "w") as destination_file:
        # and, since we now have a file-like object, use interpret_to_filelike
        interpret_to_filelike(source, destination_file, **kwargs)

def interpret_to_filelike(source, destination, **kwargs):
    "Interpret a file to a file-like object with an interpreter according to its suffix."
    # get the list of interpreters from the configuration
    interpreters = configuration.get_config().interpreters
    # figure out the last suffix of the file, to use to determine which interpreter to use
    ending = source.split(".")[-1]
    # and then interpret, based on the ending of the file!
    interpreters.get(ending, default_interpreter)(source, destination, **kwargs)

