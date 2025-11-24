# km Docker 鏈湴閮ㄧ讲瀹屾暣姝ラ鎸囧崡

## 馃搵 瀹氬埗鍖栭厤缃鏄?

鏈枃妗ｅ熀浜庝互涓嬪畾鍒跺寲瑕佹眰:
- 鉁?浣跨敤 DeepSeek API (API Key: sk-566706aa2350423b8751a5380444b227)
- 鉁?椤圭洰鍚嶇О: `km` (鏇夸唬 onyx-stack)
- 鉁?PostgreSQL 鐗堟湰: 15
- 鉁?Redis 鐗堟湰: 6.2 (鏃犲瘑鐮?
- 鉁?MinIO: 浣跨敤鏃х増鏈?(RELEASE.2023-09-04,甯︽帶鍒跺彴)
- 鉁?鍓嶇: Next.js 15 + React 18,鑷瀹夎渚濊禆骞舵瀯寤?

---

## 馃殌 瀹屾暣閮ㄧ讲姝ラ

### 绗竴姝?妫€鏌?Docker Desktop

```powershell
# 1. 纭 Docker Desktop 宸插畨瑁呭苟杩愯
docker --version
docker compose version

# 2. 閰嶇疆 Docker Desktop 璧勬簮
# 鎵撳紑 Docker Desktop 鈫?Settings 鈫?Resources
# 鎺ㄨ崘閰嶇疆:
# - CPUs: 6-8
# - Memory: 12-16 GB
# - Swap: 2 GB
# - Disk: 100 GB
```

### 绗簩姝?鍑嗗椤圭洰鐩綍

```powershell
# 杩涘叆閮ㄧ讲鐩綍
cd f:\code\onyx\deployment\docker_compose

# 纭瀹氬埗鍖栭厤缃枃浠跺瓨鍦?
dir docker-compose.km.yml
```

### 绗笁姝?閰嶇疆鐜鍙橀噺 (鍙€?

鍒涘缓 `.env.km` 鏂囦欢:

```powershell
@"
# DeepSeek API 閰嶇疆
GEN_AI_API_KEY=sk-566706aa2350423b8751a5380444b227

# 鏁版嵁搴撻厤缃?
POSTGRES_USER=kmuser
POSTGRES_PASSWORD=Evergreen@2025!
POSTGRES_DB=onyx

# MinIO 閰嶇疆
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# 璁よ瘉閰嶇疆 (鏈湴寮€鍙戠鐢?
AUTH_TYPE=disabled

# 鏃ュ織绾у埆
LOG_LEVEL=info

# 绂佺敤閬ユ祴
DISABLE_TELEMETRY=true
"@ | Out-File -FilePath .env.km -Encoding UTF8
```

### 绗洓姝?鍚姩鏈嶅姟

#### 鏂瑰紡涓€:浣跨敤棰勬瀯寤洪暅鍍?(鎺ㄨ崘,蹇€?

```powershell
docker compose -f docker-compose.km.yml -p km up -d --pull always --force-recreate
```

#### 鏂瑰紡浜?浠庢簮鐮佹瀯寤?(瀹屾暣鏋勫缓,鍖呮嫭鍓嶇渚濊禆)

```powershell
docker compose -f docker-compose.km.yml -p km up -d --build --force-recreate
```

**璇存槑**:
- `-f docker-compose.km.yml`: 浣跨敤瀹氬埗鍖栭厤缃?
- `-p km`: 椤圭洰鍚嶇О涓?km
- `--build`: 浠庢簮鐮佹瀯寤?(浼氳嚜鍔ㄥ畨瑁?Next.js 15 鍜?React 18 渚濊禆)
- `--pull always`: 鎷夊彇鏈€鏂板熀纭€闀滃儚

**棰勮鏃堕棿**:
- 鏂瑰紡涓€ (棰勬瀯寤?: 10-15 鍒嗛挓
- 鏂瑰紡浜?(婧愮爜鏋勫缓): 20-30 鍒嗛挓 (棣栨)

### 绗簲姝?鐩戞帶鍚姩杩涘害

```powershell
# 鏌ョ湅鎵€鏈夊鍣ㄧ姸鎬?
docker compose -f docker-compose.km.yml -p km ps

# 鏌ョ湅瀹炴椂鏃ュ織
docker compose -f docker-compose.km.yml -p km logs -f

# 鏌ョ湅鐗瑰畾鏈嶅姟鏃ュ織
docker compose -f docker-compose.km.yml -p km logs -f api_server
docker compose -f docker-compose.km.yml -p km logs -f web_server
```

**绛夊緟鎵€鏈夋湇鍔″惎鍔?*,鎸?`Ctrl+C` 閫€鍑烘棩蹇楁煡鐪嬨€?

### 绗叚姝?楠岃瘉鏈嶅姟

```powershell
# 妫€鏌ユ墍鏈夊鍣ㄦ槸鍚﹁繍琛?
docker ps --filter "name=km"
```

**搴旇鐪嬪埌 10 涓鍣?*:
- km-nginx-1
- km-web_server-1
- km-api_server-1
- km-background-1
- km-inference_model_server-1
- km-indexing_model_server-1
- km-relational_db-1 (PostgreSQL 15)
- km-index-1 (Vespa)
- km-cache-1 (Redis 6.2)
- km-minio-1 (MinIO 2023-09-04)

### 绗竷姝?璁块棶鏈嶅姟

鎵撳紑娴忚鍣?璁块棶浠ヤ笅鍦板潃:

| 鏈嶅姟 | URL | 璇存槑 |
|------|-----|------|
| **Web 鍓嶇** | http://localhost:3000 | 涓荤晫闈?(Next.js 15 + React 18) |
| **API 鏂囨。** | http://localhost:8080/docs | FastAPI Swagger UI |
| **PostgreSQL** | localhost:5432 | 鏁版嵁搴?(鐢ㄦ埛: kmuser, 瀵嗙爜: Evergreen@2025!) |
| **Redis** | localhost:6379 | 缂撳瓨 (鏃犲瘑鐮? |
| **MinIO Console** | http://localhost:9005 | 瀵硅薄瀛樺偍绠＄悊鐣岄潰 (minioadmin/minioadmin) |
| **Vespa** | http://localhost:8081 | 鍚戦噺鎼滅储寮曟搸 |

### 绗叓姝?娴嬭瘯 DeepSeek AI 鍔熻兘

1. 璁块棶: http://localhost:3000

2. 杩涘叆鑱婂ぉ鐣岄潰 (鏃犻渶鐧诲綍,鍥犱负 AUTH_TYPE=disabled)

3. 鍙戦€佹祴璇曟秷鎭?
   ```
   浣犲ソ,璇风敤涓枃浠嬬粛涓€涓嬩綘鑷繁
   ```

4. 搴旇鑳界湅鍒?DeepSeek AI 鐨勫洖澶?

---

## 馃敡 甯哥敤鎿嶄綔鍛戒护

### 鍋滄鏈嶅姟

```powershell
# 鍋滄鎵€鏈夊鍣?(淇濈暀鏁版嵁)
docker compose -f docker-compose.km.yml -p km stop
```

### 閲嶅惎鏈嶅姟

```powershell
# 閲嶅惎鎵€鏈夋湇鍔?
docker compose -f docker-compose.km.yml -p km restart

# 閲嶅惎鍗曚釜鏈嶅姟
docker compose -f docker-compose.km.yml -p km restart api_server
docker compose -f docker-compose.km.yml -p km restart web_server
```

### 鏌ョ湅鏃ュ織

```powershell
# 鏌ョ湅鎵€鏈夋湇鍔℃棩蹇?
docker compose -f docker-compose.km.yml -p km logs -f

# 鏌ョ湅鐗瑰畾鏈嶅姟鏃ュ織
docker compose -f docker-compose.km.yml -p km logs -f api_server
docker compose -f docker-compose.km.yml -p km logs -f web_server
docker compose -f docker-compose.km.yml -p km logs -f relational_db

# 鏌ョ湅鏈€杩?100 琛屾棩蹇?
docker compose -f docker-compose.km.yml -p km logs --tail=100
```

### 杩涘叆瀹瑰櫒璋冭瘯

```powershell
# 杩涘叆 API 鏈嶅姟鍣?
docker exec -it km-api_server-1 /bin/bash

# 杩涘叆 PostgreSQL 15
docker exec -it km-relational_db-1 psql -U kmuser -d onyx

# 杩涘叆 Redis 6.2 (鏃犲瘑鐮?
docker exec -it km-cache-1 redis-cli

# 杩涘叆鍓嶇瀹瑰櫒
docker exec -it km-web_server-1 /bin/sh
```

### 瀹屽叏娓呯悊 (鈿狅笍 鍒犻櫎鎵€鏈夋暟鎹?

```powershell
# 鍋滄骞跺垹闄ゅ鍣ㄥ拰鏁版嵁鍗?
docker compose -f docker-compose.km.yml -p km down -v
```

---

## 馃攳 鐗堟湰楠岃瘉

### 楠岃瘉 PostgreSQL 鐗堟湰

```powershell
docker exec km-relational_db-1 psql -U kmuser -d onyx -c "SELECT version();"
```

搴旇鏄剧ず: `PostgreSQL 15.x`

### 楠岃瘉 Redis 鐗堟湰

```powershell
docker exec km-cache-1 redis-cli INFO server | findstr redis_version
```

搴旇鏄剧ず: `redis_version:6.2.x`

### 楠岃瘉 MinIO 鐗堟湰

璁块棶 http://localhost:9005,鐧诲綍鍚庡簲璇ヨ兘鐪嬪埌瀹屾暣鐨勬帶鍒跺彴鐣岄潰 (涓嶆槸鏂扮増鐨勭畝鍖栫晫闈?銆?

### 楠岃瘉鍓嶇渚濊禆

```powershell
# 鏌ョ湅 Next.js 鐗堟湰
docker exec km-web_server-1 cat package.json | findstr "next"

# 鏌ョ湅 React 鐗堟湰
docker exec km-web_server-1 cat package.json | findstr "react"
```

搴旇鏄剧ず:
- `"next": "^15.2.4"`
- `"react": "^18.3.1"`

---

## 馃洜锔?鏁呴殰鎺掓煡

### 闂 1: PostgreSQL 15 杩炴帴澶辫触

```powershell
# 妫€鏌?PostgreSQL 瀹瑰櫒鐘舵€?
docker ps --filter "name=km-relational_db"

# 鏌ョ湅 PostgreSQL 鏃ュ織
docker compose -f docker-compose.km.yml -p km logs relational_db

# 娴嬭瘯杩炴帴
docker exec km-relational_db-1 psql -U kmuser -d onyx -c "SELECT 1;"
```

### 闂 2: Redis 6.2 杩炴帴闂

```powershell
# 妫€鏌?Redis 瀹瑰櫒
docker ps --filter "name=km-cache"

# 娴嬭瘯 Redis 杩炴帴 (鏃犲瘑鐮?
docker exec km-cache-1 redis-cli ping
# 搴旇杩斿洖: PONG
```

### 闂 3: MinIO 鎺у埗鍙版棤娉曡闂?

```powershell
# 妫€鏌?MinIO 鐗堟湰
docker exec km-minio-1 minio --version

# 搴旇鏄剧ず: minio version RELEASE.2023-09-04T19-57-37Z

# 鏌ョ湅 MinIO 鏃ュ織
docker compose -f docker-compose.km.yml -p km logs minio
```

纭繚璁块棶 http://localhost:9005 鑰屼笉鏄?http://localhost:9004

### 闂 4: DeepSeek API 璋冪敤澶辫触

```powershell
# 鏌ョ湅 API 鏈嶅姟鍣ㄦ棩蹇?
docker compose -f docker-compose.km.yml -p km logs api_server | findstr "GEN_AI"

# 妫€鏌ョ幆澧冨彉閲?
docker exec km-api_server-1 env | findstr "GEN_AI_API_KEY"
```

纭 API Key 姝ｇ‘: `sk-566706aa2350423b8751a5380444b227`

### 闂 5: 鍓嶇鏋勫缓澶辫触

```powershell
# 鏌ョ湅鍓嶇鏋勫缓鏃ュ織
docker compose -f docker-compose.km.yml -p km logs web_server

# 閲嶆柊鏋勫缓鍓嶇
docker compose -f docker-compose.km.yml -p km up -d --build web_server
```

---

## 馃搳 鏁版嵁鎸佷箙鍖?

### 鏁版嵁鍗峰垪琛?

```powershell
# 鏌ョ湅鎵€鏈夋暟鎹嵎
docker volume ls | findstr km
```

**閲嶈鏁版嵁鍗?*:
- `km_db_volume` - PostgreSQL 15 鏁版嵁
- `km_vespa_volume` - Vespa 绱㈠紩鏁版嵁
- `km_minio_data` - MinIO 瀵硅薄瀛樺偍
- `km_model_cache_huggingface` - AI 妯″瀷缂撳瓨
- `km_indexing_huggingface_model_cache` - 绱㈠紩妯″瀷缂撳瓨

### 澶囦唤鏁版嵁

```powershell
# 澶囦唤 PostgreSQL 15 鏁版嵁搴?
docker exec km-relational_db-1 pg_dump -U kmuser onyx > km_backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# 澶囦唤 MinIO 鏁版嵁
docker run --rm -v km_minio_data:/data -v ${PWD}:/backup alpine tar czf /backup/minio_backup.tar.gz /data
```

---

## 鉁?鎴愬姛鏍囧織

閮ㄧ讲鎴愬姛鍚?鎮ㄥ簲璇ヨ兘澶?

鉁?璁块棶 http://localhost:3000 鐪嬪埌 Web 鐣岄潰
鉁?鍦ㄨ亰澶╃晫闈㈠彂閫佹秷鎭苟鏀跺埌 DeepSeek AI 鐨勫洖澶?
鉁?璁块棶 http://localhost:9005 鐪嬪埌 MinIO 瀹屾暣鎺у埗鍙?
鉁?浣跨敤 `psql` 杩炴帴鍒?PostgreSQL 15
鉁?浣跨敤 `redis-cli` 杩炴帴鍒?Redis 6.2 (鏃犲瘑鐮?
鉁?鎵€鏈?10 涓鍣ㄩ兘鍦ㄨ繍琛?

---

## 馃幆 涓嬩竴姝ユ搷浣?

1. **閰嶇疆鏁版嵁婧愯繛鎺ュ櫒**:
   - 璁块棶: http://localhost:3000/admin/connectors
   - 娣诲姞 Google Drive, Slack, Confluence 绛夎繛鎺ュ櫒

2. **鍒涘缓鑷畾涔?Persona**:
   - 璁块棶: http://localhost:3000/admin/personas
   - 鍒涘缓涓撳睘鐨?AI 鍔╂墜

3. **娴嬭瘯 DeepSeek AI**:
   - 鍦ㄨ亰澶╃晫闈㈡祴璇曞悇绉嶉棶棰?
   - 楠岃瘉涓枃鍥炲璐ㄩ噺

4. **鐩戞帶璧勬簮浣跨敤**:
   ```powershell
   # 鏌ョ湅瀹瑰櫒璧勬簮浣跨敤
   docker stats --filter "name=km"
   ```

---

## 馃摑 蹇€熷懡浠ゅ弬鑰?

```powershell
# 鍚姩
docker compose -f docker-compose.km.yml -p km up -d

# 鏌ョ湅鐘舵€?
docker compose -f docker-compose.km.yml -p km ps

# 鏌ョ湅鏃ュ織
docker compose -f docker-compose.km.yml -p km logs -f

# 鍋滄
docker compose -f docker-compose.km.yml -p km stop

# 閲嶅惎
docker compose -f docker-compose.km.yml -p km restart

# 瀹屽叏娓呯悊
docker compose -f docker-compose.km.yml -p km down -v
```

---

## 馃敆 閲嶈閾炬帴

- Web 鍓嶇: http://localhost:3000
- API 鏂囨。: http://localhost:8080/docs
- MinIO 鎺у埗鍙? http://localhost:9005 (minioadmin/minioadmin)
- PostgreSQL: localhost:5432 (kmuser/Evergreen@2025!)
- Redis: localhost:6379 (鏃犲瘑鐮?

---

**鏂囨。鐗堟湰**: v1.0  
**鏈€鍚庢洿鏂?*: 2025-01-24  
**椤圭洰鍚嶇О**: km  
**閫傜敤浜?*: Docker Desktop 鏈湴閮ㄧ讲

