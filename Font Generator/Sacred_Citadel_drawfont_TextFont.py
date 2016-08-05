'''
生成神圣堡垒游戏的字库图片及字库索引文件(PC,PS3)
版本v1.0:创建
*************************************************
LE
4 字符缩放级别 值越大字越大
4 垃圾 修改后无任何影响
4 字符个数
以下为索引结构，每结构22字节
typedef FontIndexStru
{
    4 x坐标起始位置(坐标值=实际像素值*32，下同)
    4 y坐标起始位置
    4 x坐标结束位置
    4 y坐标结束位置
    2 值越大字符越宽，值越小字符越窄，但总会完整显示一个字符，通常设置为字体宽度
    2 字间距调整，值越小(最小为0，负值报错)字符与其左边的字符间距越大，
      值越大，间距越小，值太大有可能重叠，建议设为0x06
    2 UTF-16LE的字符编码
};
'''
import struct,sys,os,codecs
from PIL import Image,ImageDraw,ImageFont

#建立FontFileStru类
class FontFileStru:
    def __init__(self,zoom,dump,charnums,indexoffset):
        self.zoom=zoom
        self.dump=dump
        self.charnums=charnums
        self.indexoffset=indexoffset

#解析index文件
def indexfileparse(indexfile):
    #读取字体缩放级别
    zoom=struct.unpack(endian+'I',indexfile.read(4))[0]
    #读取垃圾部分
    dump=struct.unpack(endian+'I',indexfile.read(4))[0]
    #读取字符个数
    charnums=struct.unpack(endian+'I',indexfile.read(4))[0]
    #读取字库正式索引偏移位置
    indexoffset=indexfile.tell()
    #写入结构
    result=FontFileStru(zoom,dump,charnums,indexoffset)
    return result

#变量设置
endian='<'
charfile='chars.txt'
fontindexfile='55DCE06E'
fontpicfile='234E7BE5'
fontname='minijiankatong.ttf'
fontsize=40
pwidth=2048
pheight=2048-288
#pheight=2048
kerning=0x06
#索引偏移
ioff=5522
#ioff=0

#主程序
#将字符文件中的字符读入内存
if os.path.exists(charfile):
    lines=codecs.open(charfile,'r',encoding='utf-16').readlines()
    #处理去掉换行符，将字符串拼在一起
    charset=''
    for line in lines:
        charset+=line.rstrip('\n')
    #统计字符个数
    charnums=len(charset)
else:
    print('未找到字符文件%s，该文件为带BOM头utf-16编码的文件'%(charfile))
    os.system('pause')
    sys.exit()
#解析index文件
with open(fontindexfile,'rb') as indexfile:
    result=indexfileparse(indexfile)
#读取字体
font=ImageFont.truetype(fontname,fontsize)
#变量设置
x=0
y=288
xpad=4
ypad=4
fontindexdata=b''
#建立图片对象
#生成黑色背景图测试用
#im=Image.new(mode='RGBA',size=(pwidth,pheight),color=(0,0,0,255))
im=Image.new(mode='RGBA',size=(pwidth,pheight),color=(255,255,255,0))
drawobj=ImageDraw.Draw(im)
for char in charset:
    #获取每个字符宽高
    cwidth,cheight=font.getsize(char)
    #print(char,cwidth,cheight)
    #sys.exit()
    #特殊处理，仅是特殊字体需要进行此处理，否则注释掉
    #cheight=fontsize
    #判断该字符是否可以描绘在本行中，不能的话描绘在下一行
    if x+cwidth>pwidth:#不能描绘在本行
        #转到下一行进行描绘
        #调整xy偏移地址到下一行开头
        x=0
        y+=cheight+ypad
        #即时描绘字符
        drawobj.text((x,y-288),char,font=font)
        #写字符索引
        xstart=struct.pack(endian+'I',x*32)
        ystart=struct.pack(endian+'I',y*32)
        xend=struct.pack(endian+'I',(x+cwidth)*32)
        yend=struct.pack(endian+'I',(y+cheight)*32)
        xwidth=struct.pack(endian+'H',cwidth)
        xoffset=struct.pack(endian+'H',kerning)
        unicode=struct.pack(endian+'H',ord(char))
        fontindexdata+=xstart+ystart+xend+yend+xwidth+xoffset+unicode
        #调整x偏移地址
        x+=cwidth+xpad
    else:#可以描绘在本行
        #即时描绘字符
        drawobj.text((x,y-288),char,font=font)
        #写字符索引
        xstart=struct.pack(endian+'I',x*32)
        ystart=struct.pack(endian+'I',y*32)
        xend=struct.pack(endian+'I',(x+cwidth)*32)
        yend=struct.pack(endian+'I',(y+cheight)*32)
        xwidth=struct.pack(endian+'H',cwidth)
        xoffset=struct.pack(endian+'H',kerning)
        unicode=struct.pack(endian+'H',ord(char))
        fontindexdata+=xstart+ystart+xend+yend+xwidth+xoffset+unicode
        #调整x偏移地址
        x+=cwidth+xpad
#保存最终页
im.save('%s.png'%fontpicfile)
#修改字库索引文件
#对字库索引进行相应修改
with open(fontindexfile,'rb+') as indexfile:
    result.zoom=0x30
    indexfile.write(struct.pack(endian+'III',result.zoom,result.dump,charnums+(ioff//22)))
    indexfile.seek(result.indexoffset+ioff)
    indexfile.truncate()
    indexfile.write(fontindexdata)
os.system('pause')
