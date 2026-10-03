import os
import re

MapFile = 'Map.txt'

def GetMap(path):
    dirs = []
    files = []
    folder = dict()
    content = []
    for i in range(len(os.listdir(path))):
        if os.listdir(path)[i].find('.') == -1:
            dirs.append(os.listdir(path)[i])
        else:
            files.append(os.listdir(path)[i])
    files = sorted(files)
    dirs = sorted(dirs)
    
    for i in range(len(dirs)):
        folder[dirs[i]] = GetMap(path+'//'+dirs[i])
    content.append(files)
    content.append(folder)
    return content

def DrawFiles(content,path,add_str,dirs):
    files = PreDraw(content)[0]
    res = ''
    if os.path.split(path)[0] != '':
        fold = os.path.split(path)[0]
    else:
        fold = path
    if path != '..' and len(fold)//2 <= 4:
        add_str += ' '*(len(fold)//2)
    else:
        if path != '..':
            add_str += ' '*4
        else:
            add_str += ' '*(len(os.path.split(path)[1])//2)
    if len(dirs) != 0 or len(files) != 0:
        res += add_str + '│\n'
        
    for i in range(len(files)):
        out = add_str + '├'
        if i+1 == len(files) and len(dirs) == 0:
            out = add_str + '└'
        res += out + '──'+files[i] + '\n'
        if i+1 != len(files) or len(dirs) != 0:
            res += add_str + '│\n'
    if len(dirs) != 0 and len(files) != 0:
        res += add_str + '│\n'
    return [res,add_str]

def DrawMap(content,path,add_str,used):
    res = ''
    dirs = PreDraw(content)[1]
    if used:
        files_map = DrawFiles(content,os.path.split(path)[1],add_str,dirs)
    else:
        files_map = DrawFiles(content,path,add_str,dirs)
    res += files_map[0]
    add_str = files_map[1]
    for i in range(len(dirs)):
        out = add_str + '├'
        if i+1 == len(dirs):
            out = add_str + '└'
        res += out + '──'+dirs[i] + '\n'
        if i+1 != len(dirs):
            add_str += '│  '
        else:
            add_str += '   '
        files = []
        if len(content[1]) != 0:
            for j in content[1].values():
                files.append(j)
        inner_fold = []
        for j in range(len(files)):
            inner_fold.append([files[j]])
        if len(inner_fold) != 0:
            res += DrawMap(inner_fold[i][0],path+'/'+dirs[i], add_str,True)
        if i+1 != len(dirs):
            res += add_str + '\n'
            add_str = add_str[:len(add_str)-3]
    return res

def PreDraw(content):
    dirs = []
    for i in range(len(content)-1):
        for j in content[i+1].keys():
            dirs.append(j)
        for j in content[i+1].values():
            PreDraw(j)
    if len(content) > 0:
        files = content[0]
    else:
        files = []
    res = []
    res.append(files)
    res.append(dirs)
    return res

def CallDrawMap(f_name,content,head):
    if f_name != '':
        res = head + '\n'
        res += DrawMap(content,head,'',False)
        return res
    else:
        return ''

if __name__ == "__main__":
    print('Processing...')
    f_out = open(MapFile,'w',encoding='utf8')
    path = os.path.split(os.getcwd())[1]
    f_out.write(path + '\n')
    f_out.write(DrawMap(GetMap(path + '/..'),path + '/..','',False))
    f_out.close()

    path += '/Map.txt'
    input('It\'s treed! Open "' + path + '"')
