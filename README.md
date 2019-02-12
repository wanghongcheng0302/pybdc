# Pybdc
## 安装
### pip install pybdc
## 配置文件
### USER_AGENT
模拟浏览器代理，默认为**Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36**
### DELAY
访问延时，默认3秒
### DEBUG
日志打印等级
### LOG_FILE
日志文件路径，默认为**./out.log**
## 客户端
Client为网盘操作客户端，创建对象时传入**百度cookie**和**百度token**（打开浏览器调试模式，执行一般的网盘操作都能获取这两个参数）

对于文件上传\文件夹上传操作，需要在接口中传入**bd_uss**参数，该参数可通过浏览器调试模式手动获取
## 接口
### 增
#### InsertUtils
- create_dir：创建目录
	- 参数
		- bd_dir：待创建的网盘目录
- upload_file：上传文件
	- 参数
		- local_file_path：本地文件路径
		- bd_path：网盘路径，不包括文件名
		- bd_uss：文件上传附加参数
- upload_dir：上传目录
	- 参数
		- local_dir：本地目录
		- bd_dir：网盘目录
		- bd_uss：文件上传附加参数
### 删
#### DeleteUtils
- delete_dir：删除目录
	- 参数
		- bd_dir：目录路径
- delete_file：删除文件
	- 参数
		- bd_file_path：网盘文件路径
### 改
#### UpdateUtils
- modify_dir_name：修改目录名
	- 参数
		- bd_dir_old_path：原目录名，包括路径
		- bd_dir_new_name：新目录名，不包括路径
- modify_file_name：修改文件名
	- 参数
		- bd_file_old_path：原文件名，包括路径
		- bd_file_new_name：新文件名，不包括
### 查
#### SelectUtils
- select_all_from_dir：查询指定目录下的文件\目录
	- 参数
		- bd_dir：目录
		- num：一次性查询数量，默认为100
	- 返回
		- 查询结果，类型为json
### 存
#### SaveUtils
- save_to_bd_dir：保存网盘资源到指定路径
	- 参数
		- pan_url：网盘链接
		- pan_code：网盘密码
		- bd_dir：网盘路径，默认为根路径
- set_code_cookie：对于需要网盘密码的操作，输入密码后记录相应资源的cookie
	- 参数
		- pan_url：网盘链接
		- pan_code：网盘密码
- transfer_source：保存资源的实际操作
	- 参数（网盘web必要参数）
		- fsidlist
		- bd_dir
		- shareid
		- from_
		- referer
		- cookie
## 问题
1. 目前仅测试了普通百度网盘账号相关操作
2. 仅在linux下完成测试
3. 对于个别参数代码中硬编码为某一固定值，虽不影响使用，但不了解参数的真正意义
