 # Android 多渠道打包
 
## 前言
 本文的多渠道打包兼容到Android P，解决渠道包在[Android P 系统无法正常安装问题](https://github.com/Meituan-Dianping/walle/issues/264) 。
 在此非常感谢[美团点评的多渠道打包方案](<https://github.com/Meituan-Dianping/walle/issues>)给我了思考的方向，如有问题请提交 issue 。

## 获取渠道名方法

- 在Android 工程中添加：ChannelUtils.java（参考美团的工具类）

```java
String channel_name = ChannelUtil.getChannel(context);
```
 
## 常用命令：
```python
#打包
python packer.py $APK $MARKET $OUPUT $KEYSTORE_PATH $KEY_AlIAS $STORE_PASS
#帮助
python packer.py -h
```

## 参数说明：

| 参数        | 说明    |  备注  |
| --------   | :-----:  | :----: |
|APK|APK母包所在路径|必需|
|MARKET|渠道文件所在路径|market.txt|
|OUTPUT|输出目录-生成apks目录|apks_out|
|KEYSTORE_PATH|母包签名文件路径|./keystroe/debug.keystore|
|KEY_AlIAS|母签名别名|androiddebugkey|
|STORE_PASS| 母包签名密钥|android|

## 原理说明

```flow 
st=>start: 开始 
e=>end: 结束 
cond=>condition: 解压已签名的apk 
cond1=>condition: 删除签名信息
cond2=>condition: 写入渠道信息 
cond3=>condition: 生成未签名的apk 
cond4=>condition: 优化已签名的apk 
cond5=>condition:  重新签名apk
cond6=>condition: 验证是否签名成功 
st->cond 
cond(yes)->cond1
cond(no)->cond 
cond1(yes)->cond2 
cond1(no)->cond 
cond2(yes)->cond3
cond2(no)->cond 
cond3(yes)->cond4
cond3(no)->cond 
cond4(yes)->cond5 
cond4(no)->cond 
cond5(yes)->cond6 
cond5(no)->cond 
cond6(yes)->e
cond6(no)->cond 
```flow
    1.解压已签名的apk；
    2.删除签名信息:META-INF/CERT.RSA,META-INF/CERT.SF
    3.写入渠道信息；
    4.生成未签名的apk;
    5.优化已签名的apk;
    6.重新签名apk;
    7.验证是否签名成功;
