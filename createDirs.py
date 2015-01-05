__author__ = 'taoluo'

import os

def mkDir(path):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
    if os.path.isdir(path):
        return
    os.makedirs(path)

if __name__ == "__main__":
    mkDir('static')
    mkDir('log/dev')
    mkDir('media/dev/catchimg')
    mkDir('media/dev/code')
    mkDir('media/dev/font')
    mkDir('media/dev/newsImage')
    mkDir('media/dev/upload/file')
    mkDir('media/dev/upload/image')
    mkDir('media/dev/upload/img')
    mkDir('media/dev/upload/imglib')
    mkDir('media/dev/upload/scrawl')
    mkDir('media/dev/upload/thumbnail')

    mkDir('log/prod')
    mkDir('media/prod/catchimg')
    mkDir('media/prod/code')
    mkDir('media/prod/font')
    mkDir('media/prod/newsImage')
    mkDir('media/prod/upload/file')
    mkDir('media/prod/upload/image')
    mkDir('media/prod/upload/img')
    mkDir('media/prod/upload/imglib')
    mkDir('media/prod/upload/scrawl')
    mkDir('media/prod/upload/thumbnail')