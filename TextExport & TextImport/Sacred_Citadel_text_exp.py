'''
神圣堡垒文本解析程序
版本v1.0:创建
版本v1.1:只处理包含\t\t的行，改变去掉字符串两边双引号的方式
版本v1.2:根据开关决定是否去掉导出字符串中的空格
版本v1.3:导出的文本标题加上条数编号
**************************
(适用于PC、PS3)
文本为UTF-8格式纯文本，带BOM头
每一行开始为此条文本标题，然后由\t\t作为分隔符，""中为文本内容，以换行符\r\n结束
每一行就是一条文本，文本内容中无手动换行，本游戏自动换行，如果想强制换行，可采用加入半角空格的方式
'''
import struct,os,sys,fnmatch,re

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

#解析rawfile，返回数据
def rawfileparse(rawfile):
    result=[]
    for line in rawfile.readlines():
        #print(line)
        if '\t\t' in line:
            #print(line)
            line_split=line.rstrip('\n').split('\t\t')
            line_split[-1]=re.findall('"(.*)"',line_split[-1])[0]
            if DelSpaceFlag:
                line_split[-1]=line_split[-1].replace(' ','')
            result.append(line_split)
        #print(result)
        #sys.exit()
    return result

#变量定义
rawdir='raw_files'
txtdir='txt_files'
DelSpaceFlag=False
#主程序
filelist=walk(rawdir)
for rfilepath in filelist:
    print('正在导出%s中的文本'%(rfilepath))
    with open(rfilepath,'r',encoding='utf-8-sig') as rawfile:
        #调用函数解析rawfile
        result=rawfileparse(rawfile)
    #拼出tfilepath
    tfilepath=txtdir+os.sep+rfilepath.split(os.sep,1)[-1]+'.txt'
    #建立目录
    os.makedirs(os.path.dirname(tfilepath),exist_ok=True)
    #打开文件，写入文本
    with open(tfilepath,'w',encoding='utf-16') as txtfile:
        for no,(title,text) in enumerate(result):
            txtfile.write('#### %d,%s ####\n'%(no+1,title))
            txtfile.write('%s\n'%text)
            txtfile.write('\n')
os.system('pause')
