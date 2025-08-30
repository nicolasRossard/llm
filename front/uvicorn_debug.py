"""
Useful to debug in local & PyCharm
"""

import uvicorn

if "__main__" == __name__:
    uvicorn.run("streamlit_app:app", host="0.0.0.0", port=8501, reload=True)

