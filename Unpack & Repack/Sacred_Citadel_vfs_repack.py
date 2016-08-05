'''
神圣堡垒VFS包解析
版本v1.0:创建
********************************************************
（适用于PC版、PS3版）
LE
【文件头】
4 幻数 0D 35 11 0F
4 文件个数
x（结构体，每12个字节）
typedef struct
{
  int 文件名HASH值;
  int 文件字节数;
  int 文件偏移地址（绝对）;
};
'''
import fnmatch,os,struct,sys,binascii

#结构体类
class FileInfo:
    def __init__(self,hashname,size,offset):
        self.hashname=hashname
        self.size=size
        self.offset=offset

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

def byte2hex(bstr):
    hexstr=binascii.hexlify(bstr).decode('ascii')
    return hexstr

def packfileparse(packfile):
    #读取包中的文件个数
    packfile.seek(0x04)
    filenums=struct.unpack(endian+'I',packfile.read(4))[0]
    infolist=[]
    for i in range(filenums):
        #读取文件信息
        hashname=byte2hex(packfile.read(4)).upper()
        size=struct.unpack(endian+'I',packfile.read(4))[0]
        offset=struct.unpack(endian+'I',packfile.read(4))[0]
        #加入列表
        infolist.append(FileInfo(hashname,size,offset))
    #计算数据区开始地址
    dataoff=8+filenums*12
    return infolist,dataoff

#变量定义
magicnumber=b'\x0D\x35\x11\x0F'
endian='<'
packdir='pack_files'
unpackdir='unpack_files'
#主程序
filelist=walk(packdir)
for packfilepath in filelist:
    #根据幻数判断文件类型，不符合条件的跳过
    if open(packfilepath,'rb').read(4)!=magicnumber:
        continue
    print('正在封包%s'%(packfilepath))
    fullfiles=True
    with open(packfilepath,'rb+') as packfile:
        #调用函数解析
        infolist,dataoff=packfileparse(packfile)
        #拼出unpackfilepath
        unpackfilepath=unpackdir+os.sep+(os.path.splitext(packfilepath)[0]+os.path.splitext(packfilepath)[-1].replace('.','_')).split(os.sep,1)[-1]
        packfile.seek(dataoff);packfile.truncate()
        for fileinfo in infolist:
            newpath=unpackfilepath+os.sep+fileinfo.hashname
            #判断待封包的文件是否存在，如果不存在，终止封包
            if not os.path.exists(newpath):
                print('因缺少文件%s，封包终止'%(newpath))
                fullfiles=False
                break
            #修改字节数，修改偏移
            fileinfo.size=os.path.getsize(newpath)
            fileinfo.offset=packfile.tell()
            #将文件写入封包
            with open(newpath,'rb') as unpackfile:
                packfile.write(unpackfile.read())
        #只在文件完整时写入索引
        if fullfiles:
            packfile.seek(8)
            for fileinfo in infolist:
                #跳过文件名不写入
                packfile.seek(4,1)
                packfile.write(struct.pack(endian+'I',fileinfo.size))
                packfile.write(struct.pack(endian+'I',fileinfo.offset))
os.system('pause')
