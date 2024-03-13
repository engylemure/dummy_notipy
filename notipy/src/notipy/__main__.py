import notipy
import uvicorn
import sys

sys.exit(uvicorn.run("notipy:app", host="0.0.0.0", port=8080, reload=True))
