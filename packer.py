#!/usr/bin/python
# coding=utf-8
import zipfile
import shutil
import os
import sys
import struct
import subprocess
import argparse

__version__ = '1.0.0'
MARKET_PATH = 'market.txt'
OUTPUT_PATH = 'apks_out/'

#ADD FOR sign
STORE_PASS = 'android'
KEYSTORE_PATH = './keystroe/debug.jks'
KEY_AlIAS = 'androidkey'


def jarsigner(apk_file,apk_file_unsigner,keystore_path, keyAlias,store_pass):
    '''
    jarsigner apk
    '''

    command = 'zipalign -v 4 %s %s' %  (apk_file_unsigner, apk_file_unsigner)
    print('---------apk文件优化-------------')
    cwd = os.path.realpath(os.getcwd())
    pipe = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    oc = str(pipe.communicate()[0])
    print(oc)

    command = 'jarsigner -verbose  -keystore %s -signedjar %s %s %s -storepass %s' %  (keystore_path,apk_file,apk_file_unsigner,keyAlias,store_pass)
    print('---------重新生成签名-------------')
    print(command)
    cwd = os.path.realpath(os.getcwd())
    pipe = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    oc = str(pipe.communicate()[0])
    print(oc)

    del_single_file(apk_file_unsigner)

    command = 'jarsigner -verify -verbose %s' %  (apk_file)
    print('---------apk签名验证-------------')
    cwd = os.path.realpath(os.getcwd())
    pipe = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    oc = str(pipe.communicate()[0])
    print(oc)
    print('渠道包：%s' % (os.path.realpath(apk_file)))


def get_unsigner_apk(signer_file,out_put):
    '''
    del signer_file :CERT.SF and CERT.RSA
    '''
    fz = zipfile.ZipFile(signer_file, 'r')
    for file in fz.namelist():
        fz.extract(file,out_put)
    for root, dirs, files in os.walk('.'):
        for name in files:
            if('CERT.RSA' in name or 'CERT.SF' in name):
                del_single_file(os.path.join(root, name))
    out_file = os.path.abspath(out_put)
    # 删除已签名的apk
    del_single_file(signer_file)
    
    unsginer_file = out_put+'_unsign.apk'
    # 重新生成未签名的apk
    azip = zipfile.ZipFile(unsginer_file, 'w')
    for dirpath, dirnames, filenames in os.walk(out_file):
        # 这一句很重要，不replace的话，就从根目录开始复制
        fpath = dirpath.replace(out_file,'') 
        # 实现当前文件夹以及包含的所有文件的压缩
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            azip.write(os.path.join(dirpath, filename),fpath+filename,zipfile.ZIP_DEFLATED)
    # 关闭资源
    azip.close()
    # 删除解压后的文件
    shutil.rmtree(out_file)
    
    return unsginer_file




def del_single_file(file):
    if os.path.exists(file):
        #删除文件
        os.remove(file)
    else:
        print 'no such file:%s'%file
    
def process_apk(path, market, output, keystore_path, keyAlias,store_pass):
    # 空文件 便于写入此空文件到apk包中作为channel文件
    src_empty_file = 'channel.txt'
    # 创建一个空文件（不存在则创建）
    f = open(src_empty_file, 'w')
    f.close()

    # file name (with extension)
    src_apk_file_name = os.path.basename(path)
    # 分割文件名与后缀
    temp_list = os.path.splitext(src_apk_file_name)
    # name without extension
    src_apk_name = temp_list[0]
    # 后缀名，包含.   例如: ".apk "
    src_apk_extension = temp_list[1]

    # 创建生成目录,与文件名相关
    output_dir = output
    # 目录不存在则创建
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # 遍历渠道号并创建对应渠道号的apk文件
    for key in market:
        # 获取当前渠道号
        target_channel = key
        # 获取当前的渠道号名
        target_channel_name = market[key]
        # 拼接对应渠道号的apk文件名
        target_apk_name = output_dir + src_apk_name + "-" + target_channel_name
        # 拼接对应渠道号的apk
        target_apk = target_apk_name + src_apk_extension
        # 拷贝建立新apk
        shutil.copy(path,  target_apk)
        # zip获取新建立的apk文件
        zipped = zipfile.ZipFile(target_apk, 'a', zipfile.ZIP_DEFLATED)
        # 初始化渠道信息
        empty_channel_file = "META-INF/tcfchannel_{channel}".format(channel = target_channel)
        # 写入渠道信息
        zipped.write(src_empty_file, empty_channel_file)
        print('-----------写入渠道信息成功---------------')
        # 关闭zip流
        zipped.close()

        #删除签名文件
        unsginer_file = get_unsigner_apk(target_apk,target_apk_name)
        print('-----------删除签名信息成功---------------')
        # 获取当前目录
        root_name = os.getcwd()
        # 重新签名,优化包
        jarsigner(root_name+'/'+target_apk,root_name+'/'+unsginer_file,keystore_path,keyAlias,store_pass)
        
    del_single_file(src_empty_file)
        



def get_keystore_md5(keystore_path , store_pass):
    '''
    get keystore md info
    '''
    command = 'keytool -list -keystore %s -storepass %s -v' %  (keystore_path, store_pass)
    cwd = os.path.realpath(os.getcwd())
    print(cwd)
    pipe = subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    oc = str(pipe.communicate()[0])
    print('-----------签名信息---------------')
    start_index = oc.index("MD5:")
    end_index = oc.index("SHA1:")
    md5_str = oc[start_index:end_index]
    sign_md5 = ("".join(md5_str.split(':')[1:])).strip()
    print(sign_md5)
    return sign_md5

def read_market(channel_file):
    f = open(channel_file)
    lines = f.readlines()
    f.close()
    dict = {}
    print('-----------渠道信息---------------')
    for line in lines:
        # 获取当前渠道号，因为从渠道文件中获得带有\n,所有strip一下
        target_channel = line.strip().split('#')[0]
        # 获取当前的渠道号名
        target_channel_name = line.strip().split('#')[1]
        # 打印渠道信息
        print('channel= %s , channel_name = %s' % (target_channel,target_channel_name))
        # 添加到字典中
        dict.setdefault(target_channel, target_channel_name)
    return dict



def _check(path, market=MARKET_PATH ,output=OUTPUT_PATH, keystore_path=KEYSTORE_PATH,keyAlias=KEY_AlIAS, store_pass=STORE_PASS,  show=False):
    '''
    check apk file exists, check apk valid, check arguments, check market file exists
    '''
    if not os.path.exists(path):
        print('apk file',path,'not exists or not readable')
        return
    if show:
        read_market(market)
        return
    if not os.path.exists(market):
        print('market file',market,'not exists or not readable')
        return
    old_market = read_market(market)
    if not old_market:
        print('apk file',path,'already had market:',str(old_market),
            'please using original release apk file')
        return
    if not keyAlias:
        print('the apk file of key alias not found!')
        return
    sign_md5 = get_keystore_md5(keystore_path, store_pass)
    if not sign_md5:
        print('please using correct sign ')
        return
    if show:
        print('packer.py --version:%s' % (__version__))
    # 重新打签名包
    process_apk(path,old_market, output,keystore_path,keyAlias,store_pass)


def _parse_args():
    '''
    parse command line arguments
    '''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='PackerNg v{0} created by tuchaofu@126.com. \n Generation Android Market Packaging Tool'.format(__version__),
        epilog='''Project Home: ''')
    parser.add_argument('path', nargs='?',
                        help='original release apk file path (required)')
    parser.add_argument('market', nargs='?',default = MARKET_PATH,
                        help='markets file path [default: ./markets.txt]')
    parser.add_argument('output', nargs='?',default = OUTPUT_PATH,
                        help='archives output path [default: apks_out/]')

    ## add for sign
    #keystore_path, keyAlias,store_pass
    parser.add_argument('keystore_path', nargs='?',default = KEYSTORE_PATH,
                        help='you apk keystore file path,[default:./keystroe/debug.keystore]')
    parser.add_argument('keyAlias', nargs='?',default = KEY_AlIAS,
                        help='you apk keystore  keyAlias,[default:androiddebugkey]')
    parser.add_argument('store_pass', nargs='?',default = STORE_PASS,
                        help='you apk keystore store password,[default:android]')
    ## end for sign
    parser.add_argument('-s', '--show', action='store_const', const=True,
                        help='show apk file info (pkg/market/version)')
    args = parser.parse_args()
    if len(sys.argv) == 1:
        print('use ./%s -h/--help to show help messages' % sys.argv[0])
        return None
    return args

if __name__ == '__main__':
    args = _parse_args()
    if args:
        _check(**vars(args))

