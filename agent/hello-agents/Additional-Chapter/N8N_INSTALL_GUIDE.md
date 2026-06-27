这里我们介绍项目中使用的本地安装方式中的Docker，因为这种方式最稳定，并且最利于持续探索n8n的使用。

我们先进入docker官网：[Docker: Accelerated Container Application Development](https://www.docker.com/)

选择你的终端设备进行下载，这里以Windows作为演示。

![image-20250912025341155](./N8N_INSTALL_GUIDE/image-20250912025341272.png)

下载好以后可以切换磁盘存放路径，因为镜像一般很大，尽量不要存在C盘。

![image-20250912032540657](./N8N_INSTALL_GUIDE/image-20250912032540657.png)

后打开你的命令行，输入以下指令拉取n8n

```
docker volume create n8n_data
docker run -d --restart unless-stopped --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```

现在我们就能在docker里面看到n8n运行啦

![image-20250912033251997](./N8N_INSTALL_GUIDE/image-20250912033251997.png)

点击5678:5678可以进入n8n的启动界面。

![image-20250912033341666](./N8N_INSTALL_GUIDE/image-20250912033341666.png)

进入页面后，可以看到打开新项目的按钮

![image-20250912034040656](./N8N_INSTALL_GUIDE/image-20250912034040656.png)

主要用到的功能有三个
![image-20250912234709064](./N8N_INSTALL_GUIDE/image-20250912234709064.png)

添加新节点按钮打开之后可以搜索节点或选择自己有需要的节点添加即可~

![image-20250912234748845](./N8N_INSTALL_GUIDE/image-20250912234748845.png)
