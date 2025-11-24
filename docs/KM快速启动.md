# km 蹇€熷惎鍔ㄦ寚鍗?

## 鈿?涓€閿惎鍔ㄥ懡浠?

```powershell
# 1. 杩涘叆閮ㄧ讲鐩綍
cd f:\code\onyx\deployment\docker_compose

# 2. 鍚姩鎵€鏈夋湇鍔?(浣跨敤棰勬瀯寤洪暅鍍?鎺ㄨ崘)
docker compose -f docker-compose.km.yml -p km up -d --pull always --force-recreate

# 3. 鏌ョ湅鍚姩杩涘害
docker compose -f docker-compose.km.yml -p km logs -f
```

鎸?`Ctrl+C` 閫€鍑烘棩蹇楁煡鐪?绛夊緟 5-10 鍒嗛挓璁╂墍鏈夋湇鍔″惎鍔ㄥ畬鎴愩€?

---

## 鉁?楠岃瘉閮ㄧ讲

```powershell
# 妫€鏌ユ墍鏈夊鍣ㄦ槸鍚﹁繍琛?
docker ps --filter "name=km"
```

搴旇鐪嬪埌 **10 涓鍣?*閮藉湪杩愯銆?

---

## 馃寪 璁块棶鏈嶅姟

| 鏈嶅姟 | URL | 璐﹀彿瀵嗙爜 |
|------|-----|----------|
| **Web 鍓嶇** | http://localhost:3000 | 鏃犻渶鐧诲綍 |
| **API 鏂囨。** | http://localhost:8080/docs | - |
| **MinIO 鎺у埗鍙?* | http://localhost:9005 | minioadmin / minioadmin |
| **PostgreSQL 15** | localhost:5432 | kmuser / Evergreen@2025! |
| **Redis 6.2** | localhost:6379 | 鏃犲瘑鐮?|

---

## 馃И 娴嬭瘯 AI 鍔熻兘

1. 璁块棶: http://localhost:3000
2. 杩涘叆鑱婂ぉ鐣岄潰
3. 鍙戦€佹秷鎭? "浣犲ソ,璇风敤涓枃浠嬬粛涓€涓嬩綘鑷繁"
4. 搴旇鑳界湅鍒?DeepSeek AI 鐨勫洖澶?

---

## 馃搳 鍏抽敭閰嶇疆

- **LLM**: DeepSeek API (sk-566706aa2350423b8751a5380444b227)
- **椤圭洰鍚嶇О**: km
- **PostgreSQL**: 鐗堟湰 15,璐﹀彿 kmuser / Evergreen@2025!
- **Redis**: 鐗堟湰 6.2,鏃犲瘑鐮?
- **MinIO**: 2023-09-04 鐗堟湰 (甯﹀畬鏁存帶鍒跺彴)
- **鍓嶇**: Next.js 15 + React 18

---

## 馃洜锔?甯哥敤鍛戒护

```powershell
# 鏌ョ湅鐘舵€?
docker compose -f docker-compose.km.yml -p km ps

# 鏌ョ湅鏃ュ織
docker compose -f docker-compose.km.yml -p km logs -f

# 鍋滄鏈嶅姟
docker compose -f docker-compose.km.yml -p km stop

# 閲嶅惎鏈嶅姟
docker compose -f docker-compose.km.yml -p km restart

# 瀹屽叏娓呯悊 (鈿狅笍 鍒犻櫎鎵€鏈夋暟鎹?
docker compose -f docker-compose.km.yml -p km down -v
```

---

## 馃攳 鏁版嵁搴撹繛鎺?

```powershell
# 杩涘叆 PostgreSQL 15
docker exec -it km-relational_db-1 psql -U kmuser -d onyx

# 楠岃瘉鐗堟湰
docker exec km-relational_db-1 psql -U kmuser -d onyx -c "SELECT version();"

# 鏌ョ湅鏁版嵁搴撳垪琛?
docker exec km-relational_db-1 psql -U kmuser -d onyx -c "\l"
```

---

## 馃摑 鐜鍙橀噺 (.env.km)

```bash
# DeepSeek API
GEN_AI_API_KEY=sk-566706aa2350423b8751a5380444b227

# PostgreSQL 15
POSTGRES_USER=kmuser
POSTGRES_PASSWORD=Evergreen@2025!
POSTGRES_DB=onyx

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# 鍏朵粬
AUTH_TYPE=disabled
LOG_LEVEL=info
DISABLE_TELEMETRY=true
```

---

## 馃毃 鏁呴殰鎺掓煡

### 瀹瑰櫒鍚姩澶辫触

```powershell
# 鏌ョ湅澶辫触瀹瑰櫒鐨勬棩蹇?
docker compose -f docker-compose.km.yml -p km logs <鏈嶅姟鍚?

# 渚嬪:
docker compose -f docker-compose.km.yml -p km logs api_server
docker compose -f docker-compose.km.yml -p km logs relational_db
```

### 鏁版嵁搴撹繛鎺ュけ璐?

```powershell
# 娴嬭瘯鏁版嵁搴撹繛鎺?
docker exec km-relational_db-1 psql -U kmuser -d onyx -c "SELECT 1;"

# 妫€鏌ュ瘑鐮佹槸鍚︽纭?
docker exec km-relational_db-1 env | findstr POSTGRES
```

### AI 鍥炲澶辫触

妫€鏌?DeepSeek API Key 鏄惁姝ｇ‘閰嶇疆:

```powershell
docker exec km-api_server-1 env | findstr GEN_AI_API_KEY
```

---

## 馃摎 璇︾粏鏂囨。

瀹屾暣閮ㄧ讲姝ラ鍜岄厤缃鏄?璇锋煡鐪?
- `docs/km閮ㄧ讲姝ラ.md`
- `docs/Docker鏈湴閮ㄧ讲璺嚎鍥?md`
- `docs/鎶€鏈灦鏋勬枃妗?md`

---

**鏈€鍚庢洿鏂?*: 2025-01-24  
**椤圭洰**: km  
**鐜**: Docker Desktop 鏈湴閮ㄧ讲

