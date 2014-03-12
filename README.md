<h1>Natp项目<h1>
<h2>环境要求：<h2>
  <ul>
    <li>Ubuntu 12.04</li>
    <li>Python2.7   GNURadio/RTL-SDR dependencies<li>
    <li>probe package (local configure files,command line tools-modes_probe）</li>
    <li>Restful Web Service:Nginx+uWsgi+Django</li>
    <li>MySQL</li>
    <li>Google Earth</li>
  </ul>
  <h3>环境实现：</h3>
    Python 2.7 用 Ubuntu 自带即可
    安装 GNURadio库：
        方法1: 下载最新源码http://gnuradio.org/redmine/projects/gnuradio/wiki 
               编译安装
        方法2: wget http://www.sbrac.org/files/build-gnuradio 
              chmod +x build-gnuradio
              ./build-gnuradio –verbose
        GNURadio库编译安装时间较⻓长,需80-100分钟
    安装 rlt-sdr / gr-osmosdr库：
        git clone git://git.osmocom.org/rtl-sdr.git •cd rtl-sdr/
        mkdir build
        cd build
        cmake ../ -DINSTALL_UDEV_RULES=ON •make
        sudo make install
        sudo ldconfig
        
        git clone git://git.osmocom.org/gr-osmosdr •cd gr-osmosdr/
        mkdir build
        cd build/
        cmake ../
        make
        sudo make install •sudo ldconfig
    验证 rlt-sdr / gr-osmosdr库 (电视棒接PC)：
        rtl_eeprom •查看rtl-sdr设备信息
        rtl_test •采样测试
        rtl_sdr 
        rtl_fm 
        rtl_tcp
    安装 gr-air-modes 工具：
        git clone https://github.com/bistromath/gr-air-modes.git •cd gr-air-modes
        mkdir build
        cd build
        cmake ../
        make
        sudo make install •sudo ldconfig
        测试安装结果：modes_rx –help      modes_gui
    安装 Ngnix：
        参考：http://wiki.ubuntu.org.cn/Nginx
    安装 Google Earth：
        参考：http://wiki.ubuntu.com.cn/Google_Earth 
NATP_SERVER:
    信息汇聚检索服务，modes信息导出到KML文件中，DB Schema设计（）
    接口report接收natp_probe汇报的请求；
    解析请求中的SQL记录后，写入MySQL数据库中；
    页面展示信息；
    接口定时更新kml输出；
    部署时采用https;
    查询时采用memcached缓存；
    
    
    
