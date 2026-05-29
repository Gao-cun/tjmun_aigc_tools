# Delegate Writing Consistency Analyzer

一个模联代表写作一致性分析器。它分析“新文本与该代表历史写作风格的偏离程度”，不做 AI 检测，也不输出 AI probability。

## 功能

- Delegate profile 创建与历史文档管理
- 支持上传 `txt` / `docx` / `pdf`
- Stylometry 特征：句长、长句比例、功能词、标点、被动语态、连接词、POS 分布、lexical diversity
- Embedding baseline：默认 `sentence-transformers/all-MiniLM-L6-v2`，可切 OpenAI Embeddings
- 风险输出：`Low / Medium / High Consistency Risk`
- 可视化：dashboard、timeline、radar chart、feature drift、embedding cluster
- Revision history 分析接口：粘贴、大段输入、停顿、删除重写比例
- FastAPI Swagger：`http://localhost:8000/docs`

## 本地启动

后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

打开：

- Frontend: `http://localhost:3000`
- FastAPI Swagger: `http://localhost:8000/docs`

## Docker 启动

```bash
docker compose up --build
```

## 环境变量

复制 `.env.example` 为 `.env` 后按需调整：

```bash
DATABASE_URL=sqlite:///./data/app.db
UPLOAD_DIR=./data/uploads
EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

切换 OpenAI embedding：

```bash
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your_key_from_env
```

不要把密钥写入代码或提交到 Git。

macOS 一键脚本默认使用 `EMBEDDING_PROVIDER=hash` 启动 demo，避免首次运行下载 HuggingFace 模型导致界面卡住。需要真实本地 MiniLM embedding 时，用下面命令启动：

```bash
EMBEDDING_PROVIDER=local ./start-mac.command
```

## Demo 数据

首次打开前端时会自动调用 `/demo/seed`。也可以手动执行：

```bash
curl -X POST http://localhost:8000/demo/seed
```

## 示例 API

创建代表：

```bash
curl -X POST http://localhost:8000/delegates \
  -H "Content-Type: application/json" \
  -d '{"name":"Maya Chen","country":"Canada","committee":"UNHRC"}'
```

上传历史文档：

```bash
curl -X POST http://localhost:8000/upload_history \
  -F delegate_id="<delegate_id>" \
  -F document_type="Position Paper" \
  -F meeting="TJMUN Spring" \
  -F document_date="2026-05-21" \
  -F file=@sample.txt
```

分析新文档：

```bash
curl -X POST http://localhost:8000/analyze \
  -F delegate_id="<delegate_id>" \
  -F file=@new_text.txt
```

Revision session 分析：

```bash
curl -X POST http://localhost:8000/revision_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "delegate_id": "<delegate_id>",
    "source_type": "typing_session",
    "events": [
      {"timestamp": 0, "type": "insert", "text": "Opening sentence."},
      {"timestamp": 240, "type": "paste", "text": "A long inserted paragraph..."},
      {"timestamp": 260, "type": "delete", "chars": 40}
    ]
  }'
```

## 风险评分解释

系统先从历史文档提取 stylometry 特征和 embedding centroid，再对新文本计算：

- semantic drift：新文本 embedding 到历史 centroid 的 cosine distance
- stylometric shift：显著变化特征的 z-score 均值
- embedding distance：cosine 与 Mahalanobis distance
- significant features：偏离最明显的写作特征

输出只表示“与历史风格画像的一致性偏离程度”，不代表作者身份判断，也不代表 AI 生成概率。

## 测试

```bash
cd backend
pytest
```

```bash
cd frontend
npm run lint
```
