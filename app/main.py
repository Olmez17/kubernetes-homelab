from .database import lifespan
from fastapi import HTTPException
from fastapi import FastAPI
from .models import Item

app = FastAPI(lifespan=lifespan)
@app.get("/")
def read_root():
	return{"message": "hello_berkay"}
@app.get("/ready")
async def ready():
    try:
        await app.state.pool.fetchval("SELECT 1")
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="database not ready")


@app.post("/items")
async def create_item(item: Item):
    new_id = await app.state.pool.fetchval(
        "INSERT INTO items (text, completed) VALUES ($1, $2) RETURNING id",
        item.text, item.completed
    )
    return {"id": new_id, "text": item.text, "completed": item.completed}

@app.get("/items")
async def get_items():
    rows = await app.state.pool.fetch("SELECT id, text, completed FROM items")
    return [dict(row) for row in rows]

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    result = await app.state.pool.execute("DELETE FROM items WHERE id = $1", item_id)
    number = int(result.split()[-1])
    if number == 0:
        raise HTTPException(status_code=404, detail="item not found")
    else:
        return {"deleted": item_id}
