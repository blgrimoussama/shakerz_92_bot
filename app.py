from quart import Quart, render_template, redirect, send_from_directory
from func import apology
import os

DIRNAME = '\\'.join(os.path.dirname(__file__).split("/"))

app = Quart(__name__)

@app.route("/data/<channel>/<path:path>")
async def get_txt(channel, path):
    try:
        if not path.endswith('.txt'):
            raise FileNotFoundError
        with open(os.path.join(f"{DIRNAME}/static/{channel}", path), "r") as f:
            content = f.read()
        return {"participants": content.strip().split('\n')}
    except FileNotFoundError:
        # raise ValueError('No such file')
        return await apology('FileNotFoundError', 500)


@app.route('/')
async def index():
    return 'What do you want here ?! 🙄'


@app.route("/static/<channel>/<path:path>")
async def static_dir(channel, path):
    return await send_from_directory(f"static/{channel}", path)


@app.route("/spin/<channel>/<path:path>")
async def spin(channel, path):
    data = await get_txt(channel, path)
    # print(data['participants'].strip().split('\n'))
    if not isinstance(data, tuple):
        return await render_template('last.html',
                                     title=path.replace('.txt', ''),
                                     data=data['participants'],
                                     channel=channel)
    else:
        return await apology('FileNotFoundError', 500)


@app.route("/spins/<channel>/<path:path>")
async def spins(channel, path):
    data = await get_txt(channel, path)
    # print(data['participants'].strip().split('\n'))
    if not isinstance(data, tuple):
        return await render_template('spin.html',
                                     title=path.replace('.txt', ''),
                                     data=data['participants'])
    else:
        return redirect(f"/{path}", code=302)


@app.route("/test/<channel>/<path:path>")
async def test(channel, path):
    data = await get_txt(channel, path)
    # print(data['participants'].strip().split('\n'))
    if not isinstance(data, tuple):
        return await render_template('last_2.html',
                                     title=path.replace('.txt', ''),
                                     data=data['participants'])
    else:
        return redirect(f"/{path}", code=302)