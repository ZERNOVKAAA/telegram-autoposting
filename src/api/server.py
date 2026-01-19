from fastapi import FastAPI
import os

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'Telegram AutoPosting API', 'status': 'online'}

@app.get('/health')
async def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 10000))
    uvicorn.run(app, host='0.0.0.0', port=port)
