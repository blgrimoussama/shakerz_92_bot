from hypercorn.config import Config
from hypercorn.asyncio import serve
from app import app
from bot import Bot, client, main
import asyncio


# client.loop.create_task(main())

loop = asyncio.get_event_loop()
config = Config()
# config.bind = ['0.0.0.0:3000']
loop.create_task(serve(app, config))
bot = Bot(['shakerz_92'])
# dbot.pubsub_client = client
bot.run()

