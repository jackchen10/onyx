# KM 项目一键启动命令

## 🚀 快速启动

```powershell
# 进入部署目录
cd f:\code\onyx\deployment\docker_compose

# 启动所有服务
docker compose -f docker-compose.km.yml -p km up -d --pull always --force-recreate

# 查看启动进度
docker compose -f docker-compose.km.yml -p km logs -f
```

---

## ✅ 验证部署

```powershell
docker ps --filter "name=km"
```

应该看到 10 个容器: km-nginx-1, km-web_server-1, km-api_server-1, 等等。

---

## 🌐 访问地址

- **Web 前端**: http://localhost:3000
- **API 文档**: http://localhost:8080/docs  
- **MinIO 控制台**: http://localhost:9005 (minioadmin/minioadmin)
- **PostgreSQL 15**: localhost:5432 (kmuser/Evergreen@2025!)
- **Redis 6.2**: localhost:6379 (无密码)

---

## 🛠️ 常用命令

```powershell
# 查看状态
docker compose -f docker-compose.km.yml -p km ps

# 查看日志
docker compose -f docker-compose.km.yml -p km logs -f

# 停止服务
docker compose -f docker-compose.km.yml -p km stop

# 重启服务
docker compose -f docker-compose.km.yml -p km restart

# 完全清理
docker compose -f docker-compose.km.yml -p km down -v
```

---

## 📊 关键配置

- **LLM**: DeepSeek API (sk-566706aa2350423b8751a5380444b227)
- **项目名称**: km
- **PostgreSQL**: 版本 15, kmuser / Evergreen@2025!
- **Redis**: 版本 6.2, 无密码
- **MinIO**: 2023-09-04 版本
- **前端**: Next.js 15 + React 18

---

详细文档: `docs/KM部署步骤.md`
