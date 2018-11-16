import pip

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

if __name__ == 'main':
    install('pandas')
    install('xlrd')