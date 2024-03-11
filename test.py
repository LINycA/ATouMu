from os import getcwd,path,listdir

from mutagen import mp3,flac,id3

file_list = [path.join(getcwd(),i) for i in listdir(getcwd())]

for i in file_list:
    if path.isdir(i):
        for n in listdir(i):
            file_list.append(path.join(i,n))
    else:
        if "flac" in i:
            print(i)
            info = flac.FLAC(i)
            print(info["lrc"])