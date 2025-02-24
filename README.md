# stream-diffusion-webapp

## 動作環境

* uv 0.6.0
* python 3.10
* nvm 0.40.1
* node v22.13.1

* macOS 15.3.1
* M4 Max 128 GB

## 動かし方

### 1. pythonのライブラリをインストールする

uvを使う場合
```
uv sync
```

uvを使わない場合
```
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. nodeのライブラリをインストールする

```
cd frontend
nvm install
nvm use
npm install
```

### 3. フロントエンドをビルドする

```
cd frontend
npm run build
```

### 4. 動かす

uvを使う場合
```
cd stream-diffusion-webapp
uv run fastapi dev ./backend/app.py
```

uvを使わない場合
```
cd stream-diffusion-webapp
python3 -m uvicorn backend.app:app --reload
```
