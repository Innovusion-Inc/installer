# Virtual Loop 安装包内容说明

1. OD和WEB压缩包以 OM_Virtual_Loop_OD_ 或OM_Virtual_Loop_WEB_ 为前缀，zip为后缀
2. OM_Virtual_Loop_WEB_*.zip 中文件夹和文件不要轻易修改
   目录结构如下：

   ```bash
   ├── docker_install
   │   ├── city-job
   │   │   ├── city-job-admin.jar
   │   │   └── Dockerfile
   │   ├── docker-compose.yml
   │   ├── innovusion_lidar_util
   │   ├── nginx
   │   │   └── nginx.conf
   │   ├── redis
   │   │   └── redis.conf
   │   └── upload.sh
   ├── restart.sh
   └── webAndGL
       ├── apollo
       ├── omnisense
       │   ├── city-admin.jar
       │   ├── Dockerfile
       │   ├── Dockerfile_withoutscene
       │   ├── docker_omnisense.sh
       │   ├── scene
       │   │   ├── Dual_Lidar_Virtual_Loop.zip
       │   │   └── Single_Lidar_Virtual_Loop.zip
       │   └── version
       └── web
           └── virtualLoop.zip

   ```
   1. 安装程序会修改docker_compose.yml文件中的build路径和volumes路径
3. OM_Virtual_Loop_WEB_*.zip中web包(OM_Virtual_Loop_WEB_*/webAndGL/web/web_name.zip)解压后的文件夹名称需要和压缩包名称相同
