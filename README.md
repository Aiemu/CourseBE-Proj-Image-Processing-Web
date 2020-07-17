# 图片处理网站 项目文档
  * [图片处理网站 项目文档](#图片处理网站-项目文档)
       * [实验分工](#实验分工)
       * [部署方式及效果](#部署方式及效果)
       * [项目开发测试环境](#项目开发测试环境)
       * [基于深度学习的图像处理](#基于深度学习的图像处理)
       * [用户模块](#用户模块)
       * [网页基础操作](#网页基础操作)

### 实验分工
    Aiemu: 基于深度学习的图像处理模块，界面的外观显示，历史记录管理模块
    Bo-B0: 用户模块实现，网页后端接口的实现，前端框架搭建

### 部署方式及效果
    - 部署方式
    $ pip install torch torchvision numpy matplotlib django scikit-image pillow opencv-python 

    $ python manager.py run server 8000
    
    之后可通过http://localhost:8000/login访问登录界⾯

    - 部署效果
1. login/
![pic_login](https://tva1.sinaimg.cn/large/006y8mN6ly1g6x0icwrz3j31ip0u0gow.jpg)

2. logon/
![pic_logon](https://tva1.sinaimg.cn/large/006y8mN6ly1g6x0jnuhqdj31ip0u0dj3.jpg)

3. home/
![pic_home](https://tva1.sinaimg.cn/large/006y8mN6ly1g6x0kczw24j31ip0u0npe.jpg)

4. history/
![pic_history](https://tva1.sinaimg.cn/large/006y8mN6ly1g6x0l7jw8tj31ip0u0gsu.jpg)


### 项目开发测试环境
      后端
    - python 3.7
    - pytorch 
    - django 2.2.4
    - SQLite3
      
      前端 
    - bootstrap v3.3.7
    - bootstrap table 1.15.4
    - nodejs v12.7.0

      运行环境
    - Google Chrome 76.0.3809.87

### 基于深度学习的图像处理
    1. 图像分割（Segmentation）
        模型: torchvision.models.segmentation.fcn_resnet101
        输入: 原始图片 * 1
        输出: 显示分割的图片 * 1
        其他: 检测动漫图片即复杂风景图的能力较差
    
    2. 目标检测（Detection）
        模型: torchvision.models.detection.maskrcnn_resnet50_fpn
        输入: 原始图片 * 1
        输出: 带框、目标名称及可能性的图片 * 1
        其他: 检测动漫图片即复杂风景图的能力较差
    
    3. 风格转换（StyleTransition）
        模型: torchvision.models.vgg19
        输入: 原始图片 * 1
        输出: 风格转换后的图片 * 1
        其他: 该功能将会耗费数分钟时间，不满足作业要求，仅留作参考。此外该功能仅支持正方形图片的转换

### 用户模块
    1. 实现了注册、登录和注销等基本功能，并使用了Cookie维护登录状态。在除了登录（login/）注册（logon/）均实现了用户身份检测，若未登录则自动返回登录页面
    2. 用户选择的图片会储存在Final_Project/media/1下，处理完成的图片会根据操作种类分别储存在Final_Project/media/det|seg|sty下
    3. 在登录进入home/后可通过点击导航栏的history进入该用户的历史记录管理页面，该模块显示的图片由服务器后台发送
    4. 管理员功能可通过创建Django超级用户实现

### 网页基础操作
    1. 打开网页后进入login/界面，密码错误/未输入用户名或密码/用户不存在等均会有提示信息
    2. 用户可通过login/界面进入logon/界面，该界面会有未输入用户名或密码/用户已存在等错误信息提示。注册成功后会自动返回登录界面，也可选择手动返回
    3. 登录成功后用户进入home/界面，点击每个功能简介下的view detail按钮可跳转到对应位置
    4. 每个功能的图片均可通过选择系统图片或http网址的方式传入，图片处理完成后会自动刷新页面并将原始图片或处理后的图片在功能对应位置显示
    5. 用户可通过点击home/导航栏的history进入该用户的历史记录管理页面。该页面实现了删除/批量删除/关键字搜索/分页/选择每页显示数量/按操作时间或id排序
