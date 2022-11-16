# 简书贝信息交流中心

简书贝交易意向平台。

## 功能

- 意向单发布、修改价格和已交易数量、删除
- 用户注册与登录，绑定简书账号，修改昵称和密码
- 查看已有的意向单，支持意向单自动过期
- 查看交易均价等统计数据

## 部署

以下部署方式均需要在 `27017` 端口启动一个 MongoDB 服务器。

在项目根目录下运行以下命令，生成默认配置文件：

```
python utils/config.py
```

### Docker

将启动的 MongoDB 服务器添加到名为 `mongodb` 的 Docker 网络中。

在配置文件中将 `db.host` 改为 `mongodb`。

运行以下命令：

```
docker compose up -d
```

### 手动部署

运行以下命令安装依赖：

```
poetry install
```

如果没有安装 `Poetry`，可运行以下命令：

```
pip install -r requirements.txt
```

启动服务：

```
python main.py
```