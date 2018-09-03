from gitsrht.app import app
from srht.config import cfg, cfgi

import os

app.static_folder = os.path.join(os.getcwd(), "static")

if __name__ == '__main__':
    app.run(host=cfg("git.sr.ht", "debug-host"),
            port=cfgi("git.sr.ht", "debug-port"),
            debug=True)
