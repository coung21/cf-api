from sanic import Sanic
from sanic_cors import CORS
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME
from routes import init_routes

app = Sanic("CoffeeLeafAPI")

# Enable CORS (if needed)
CORS(app)

# MongoDB Connection


@app.listener('before_server_start')
async def setup_db(app, loop):
    app.ctx.mongo_client = AsyncIOMotorClient(MONGO_URI, io_loop=loop)
    app.ctx.db = app.ctx.mongo_client[DB_NAME]


@app.listener('after_server_stop')
async def close_db(app, loop):
    app.ctx.mongo_client.close()

# Initialize routes
init_routes(app)

if __name__ == "__main__":
    app.run(host="localhost", port=8000)
