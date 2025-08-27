"""
Useful to debug in local & PyCharm
"""

import uvicorn

if "__main__" == __name__:
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

