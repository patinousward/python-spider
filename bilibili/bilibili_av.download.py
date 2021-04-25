def change(x):
   tr = {}
   table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
   s = [11, 10, 3, 8, 4, 6]
   xor = 177451812
   add = 8728348608
   r = 0
   for i in range(58):
       tr[table[i]] = i
   for i in range(6):
       r+=tr[x[s[i]]]*58**i
   return (r-add)^xor

def choose(url):
   import re
   try:
       modle_video = r'BV\w{10}'
       match = re.findall(modle_video, url, re.I)
       new=match[0]
       new_url='https://www.bilibili.com/video/av'+str(change(new))
   except:
       modle_video = r'ss\d{5}'
       match = re.findall(modle_video, url, re.I)
       new = match[0]
       new_url='https://www.bilibili.com/bangumi/play/'+new
   return new_url

def download(url):
   import sys
   import getpass
   import you_get
   user = getpass.getuser()
   directory = r'/home/patinousward/下载/bilibili' 
   print(url)
   print(directory)
   sys.argv = ['you-get', '--playlist', '-o', directory, url]
   you_get.main()
   print('finish download :',url)

while 1:
   download(choose(input('url')))
