from fastapi import FastAPI
import os

app = FastAPI(title='Telegram AutoPosting API')

@app.get('/')
async def root():
    return {'message': 'Telegram AutoPosting API', 'status': 'online'}

@app.get('/health')
async def health():
    return {'status': 'healthy'}

@app.get('/test')
async def test():
    return {'test': 'ok', 'timestamp': '2024-01-01'}

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 10000))
    uvicorn.run(app, host='0.0.0.0', port=port)
