'''
神圣堡垒文本解析程序
版本v1.0:创建
版本v1.1:根据开关以决定是否对每个字符进行加空格处理，以完成游戏中的自动换行。
版本v1.2:导入时对标题做去掉编号的处理
**************************
(适用于PC、PS3)
文本为UTF-8格式纯文本，带BOM头
每一行开始为此条文本标题，然后由\t\t作为分隔符，""中为文本内容，以换行符\r\n结束
每一行就是一条文本，文本内容中无手动换行，本游戏自动换行，如果想强制换行，可采用加入半角空格的方式
'''
import struct,os,sys,fnmatch

#递归遍历一个目录下所有文件（含子目录），返回包含目录中所有文件的文件名的列表，对于空目录及空子目录不返回任何值。
#增加按模式匹配功能，默认返回所有文件(*)，也可以只返回匹配的文件列表
#参数1:目录名称
#参数2:匹配模式，默认*
def walk(dirname,pattern='*'):
    filelist=[]
    for root,dirs,files in os.walk(dirname):
        for filename in files:
            fullname=os.path.join(root,filename)
            filelist.append(fullname)
    return fnmatch.filter(filelist,pattern)

#将普通agemo格式的文本转化为列表，合并多行，去掉末尾换行符但不处理中间的换行符。并去掉可能有的句子结尾控制符
#参数1:一个包含文件所有行的列表
#参数2:模式，简单模式S(simple)只返回合并后的文本列表，复杂模式F(Full)返回一个包含[agemo标题，文本]的列表，默认简单模式
#参数3:句子结尾控制符，默认{END}，不一定所有文本都有，而且文本中有的话也会被替换掉
#参数4:换行符，默认\n
def agemo2list(lines,mode='S',lastctl='{END}',newline='\n'):
    textlist=[]
    llen=len(lines)
    for index,line in enumerate(lines):
        if ('#### ' in line) and (' ####' in line):
            j=1
            strs=''
            while True:
                if index+j>=llen:
                    break
                if ('#### ' in lines[index+j]) and (' ####' in lines[index+j]):
                    break
                else:
                    strs+=lines[index+j]
                    j+=1
            textlist.append([line.split(' ')[1],strs.rstrip(newline).replace(lastctl,'')])
    if mode=='S':
        return [y for x,y in textlist]
    if mode=='F':
        return textlist

def addspace(strs):
    newstrs=''
    for c in strs:
        newstrs+=c+' '
    return newstrs
        
#变量定义
rawdir='raw_files'
txtdir='txt_files'
AddSpaceFlag=True
#主程序
filelist=walk(rawdir)
for rfilepath in filelist:
    #拼出tfilepath
    tfilepath=txtdir+os.sep+rfilepath.split(os.sep,1)[-1]+'.txt'
    #检查对应txt文件是否存在
    if not os.path.exists(tfilepath):
        print('%s对应的文本文件不存在，跳过该文件的导入'%(rfilepath))
        continue
    #读取文本文件内容至列表
    with open(tfilepath,'r',encoding='utf-16') as txtfile:
        textlist=agemo2list(txtfile.readlines(),mode='F')
        #sys.exit()
    with open(rfilepath,'r+',encoding='utf_8_sig') as rawfile:
        print('正在导入%s的文本'%(rfilepath))
        #更新文本
        rawfile.truncate(0)
        for title,text in textlist:
            if AddSpaceFlag:
                text=addspace(text)
            rawfile.write(title.split(',')[-1]+'\t\t'+'"'+text+'"\n')
os.system('pause')
