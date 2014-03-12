<h1>Natp项目<h1>
<h2>环境要求：<h2>
    <p>Ubuntu 12.04</p>
    <p>Python2.7   GNURadio/RTL-SDR dependencies</p>
    <p>probe package (local configure files,command line tools-modes_probe）</p>
    <p>Restful Web Service:Nginx+uWsgi+Django</p>
    <p>MySQL</p>
    <p>Google Earth</p>
  <h3>环境实现：</h3>
    <p>Python 2.7 用 Ubuntu 自带即可</p>
    <p>安装 GNURadio库：</p>
        <p>方法1: 下载最新源码http://gnuradio.org/redmine/projects/gnuradio/wiki </p>
         <p>      编译安装</p>
        <p>方法2: wget http://www.sbrac.org/files/build-gnuradio </p>
          <p>    chmod +x build-gnuradio</p>
          <p>    ./build-gnuradio –verbose</p>
        <p>GNURadio库编译安装时间较⻓长,需80-100分钟</p>
    <p>安装 rlt-sdr / gr-osmosdr库：</p>
        <p>git clone git://git.osmocom.org/rtl-sdr.git •cd rtl-sdr/</p>
        <p>mkdir build</p>
        <p>cd build</p>
        <p>cmake ../ -DINSTALL_UDEV_RULES=ON •make</p>
        <p>sudo make install</p>
        <p>sudo ldconfig</p>
        
        <p>git clone git://git.osmocom.org/gr-osmosdr •cd gr-osmosdr/</p>
        <p>mkdir build</p>
        <p>cd build/</p>
        <p>cmake ../</p>
        <p>make</p>
        <p>sudo make install •sudo ldconfig</p>
    <p>验证 rlt-sdr / gr-osmosdr库 (电视棒接PC)：</p>
        <p>rtl_eeprom •查看rtl-sdr设备信息</p>
        <p>rtl_test •采样测试</p>
        <p>rtl_sdr </p>
        <p>rtl_fm </p>
        <p>rtl_tcp</p>
    <p>安装 gr-air-modes 工具：</p>
        <p>git clone https://github.com/bistromath/gr-air-modes.git •cd gr-air-modes</p>
        <p>mkdir build</p>
        <p>cd build</p>
        <p>cmake ../</p>
        <p>make</p>
        <p>sudo make install •sudo ldconfig</p>
        <p>测试安装结果：modes_rx –help      modes_gui</p>
    <p>安装 Ngnix：</p>
        <p>参考：http://wiki.ubuntu.org.cn/Nginx</p>
    <p>安装 Google Earth：</p>
        <p>参考：http://wiki.ubuntu.com.cn/Google_Earth </p>
<h2>NATP_SERVER:</h2>
    <p>信息汇聚检索服务，modes信息导出到KML文件中，DB Schema设计（）</p>
    <p>接口report接收natp_probe汇报的请求；</p>
    <p>解析请求中的SQL记录后，写入MySQL数据库中；</p>
    <p>页面展示信息；</p>
    <p>接口定时更新kml输出；</p>
    <p>部署时采用https;</p>
    <p>查询时采用memcached缓存；</p>
    
    
    
