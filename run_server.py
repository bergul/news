import sys
import asyncio
import uvicorn

# Ensure Windows uses SelectorEventLoop before creating the event loop
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

if __name__ == "__main__":
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000)

