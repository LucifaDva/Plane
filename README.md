Natp项目
===
###环境要求：
    Ubuntu 12.04
    Python2.7   GNURadio/RTL-SDR dependencies
    probe package (local configure files,command line tools-modes_probe)
    Restful Web Service:Nginx+uWsgi+Django
    MySQL
    Google Earth
###环境实现：
#####Python 2.7 用 Ubuntu 自带即可
#####安装 GNURadio库：
        方法1: 下载最新源码http://gnuradio.org/redmine/projects/gnuradio/wiki 
              编译安装
        方法2: wget http://www.sbrac.org/files/build-gnuradio
              chmod +x build-gnuradio
              ./build-gnuradio –verbose
        GNURadio库编译安装时间较⻓长,需80-100分钟
#####安装 rlt-sdr / gr-osmosdr库：
        git clone git://git.osmocom.org/rtl-sdr.git •cd rtl-sdr/
        mkdir build
        cd build
        cmake ../ -DINSTALL_UDEV_RULES=ON 
        make
        sudo make install
        sudo ldconfig
        
        git clone git://git.osmocom.org/gr-osmosdr •cd gr-osmosdr/
        mkdir build
        cd build/
        cmake ../
        make
        sudo make install •sudo ldconfig
#####验证 rlt-sdr / gr-osmosdr库 (电视棒接PC)：
        rtl_eeprom •查看rtl-sdr设备信息
        rtl_test •采样测试
        rtl_sdr 
        rtl_fm 
        rtl_tcp
#####安装 gr-air-modes 工具：
        git clone https://github.com/bistromath/gr-air-modes.git •cd gr-air-modes
        mkdir build
        cd build
        cmake ../
        make
        sudo make install •sudo ldconfig
        测试安装结果：modes_rx –help      modes_gui
#####安装 Ngnix：
        参考：http://wiki.ubuntu.org.cn/Nginx
#####安装 Google Earth：
        参考：http://wiki.ubuntu.com.cn/Google_Earth 
###NATP_SERVER:
    信息汇聚检索服务，modes信息导出到KML文件中，DB Schema
    接口report接收natp_probe汇报的请求；
    解析请求中的SQL记录后，写入MySQL数据库中；
    页面展示信息；
    接口定时更新kml输出；
    部署时采用https;
    查询时采用memcached缓存；
###客户端（natp-modes）
前端负责收集飞机信号，并且解码，将结果传送给服务器端。基本上基于gr-air-modes。但是添加了向服务器汇报的功能。包括：数据汇报格式的定义，定时汇报机制，数据加密等。

#####数据汇报格式
数据汇报格式采用xml1.0，添加了自定义元素sql，probe，content，下面是一个例子：

	<?xml version='1.0' encoding='UTF-8'?>
	<sql>
	<probe>first_probe</probe>
	<content>{'values': {'icao': '7867259', 'seen': '2013-11-26 13:29:55', 'speed': '444', 'heading': '7', 'vertical': '-128'}, 'table_name': 'vectors'}
	</content>
	<content>{'values': {'icao': '7867259', 'seen': '2013-11-26 13:29:55', 'alt': '35125', 'lat': '40.257568', 'lon': '116.759277'}, 'table_name': 'positions'}
	</content>
	<content>{'values': {'icao': '7857259', 'ident': 'CSN3615'}, 'table_name': 'ident'}</content>
	</sql>

probe对应服务器端中的probe数据来源，每一行数据都由content包含，数据含义如下(根据数据含义分成3类)

	table_name对应服务器端的3个数据库表，也代表3中消息类别
	
	Ident
	icao 标识飞机
	ident 飞机航班号
	
	Vector
	icao 同上
	seen，该条消息被解析的时间（可以粗略认为是飞机在该时刻的信息）
	speed 飞机水平速度
	heading 以北东南西顺时针方向的角度，北为0度
	vertical 竖直速度
	
	Position
	icao 同上
	seen 同上
	alt  高度（altitude）
	lat  纬度（latitude）
	lon  经度（longtitude）
	
#####定时汇报机制
每个客户端都有一个配置文件，文件内容如下

	[general]

	log_file = XXXX/natp_modes.log
	probe_name = first_probe

	[net_reporter]
	endpoint = http://XXXX/report/
	timeout = 180s
	max_rep_num = 200
	client_cert = XXXXXX/client.crt
	ca_cert = XXXXX/ca.crt
	
其中timeout为每隔多少时间汇报一次(如果消息个数未0则不汇报)，而max_rep_num是每次汇报的大小（以免数据过大，传送失败，以及考虑服务器端处理事件）

#####数据加密
客户端传送数据到服务器端采用https协议，保证数据的安全。

###服务器端
服务器端集中处理客户端发送过来的数据，并进行展示(展示包括数据展示以及google KML文件导出展示)。主要技术包括：使用nginx服务器，django框架，https的支持，系统后台任务调度，查询缓存等。

#####系统后台任务调度
由于多个客户端同时发送数据到服务器端，以及数据动态导出展示需要，增加系统后台任务调度功能。利用celery（开源项目，自称是分布式任务调度队列）来实现服务器不处理请求，而将任务交给系统的celery守护进程处理。

#####查询缓存
由于每次请求查询数据都需要很多时间，利用memcache缓存系统，通过将相同请求中的第一次请求结果存储，来实现快速查询。

#####google kml文件导出算法
导出支持动态和静态导出，静态导出则根据给定的时间范围导出一个kml文件，并下载给用户，用户通过google earth等工具查看飞机。动态导出则是给定一个kml的url给用户，用户也是通过google earth查看，但是这个kml文件内容会动态变化，根据用户给定的时间间隔，生成给定时间内的飞机信息。  
生成kml算法

	Input: start：开始时间
		   end：结束时间
		   freq：查询飞机时间范围长度
		   window_size: 查询飞机信息的历史时间
	Output: 包含飞机信息kml格式的文件
	
	cursor: initially equals start
	front: initially equals start + freq
	back: initially equals start - window_size
	
		while True:
			back = cursor - window_size
			cursor = front
			front = front + freq
			
			if front < end:
				kml = search(back, front)
			elif front > end:
				front = end
				kml = search(back, front)
			else:
				kml = search(back, front)
				break
				

    
    
    
