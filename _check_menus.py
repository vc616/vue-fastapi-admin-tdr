import asyncio, aiosqlite

async def check():
    db = await aiosqlite.connect("db.sqlite3")
    db.row_factory = aiosqlite.Row
    cur = await db.execute(
        "SELECT id, name, path, parent_id, menu_type, component, redirect, icon "
        "FROM menu ORDER BY parent_id, id"
    )
    rows = await cur.fetchall()
    for r in rows:
        d = dict(r)
        print(
            f"  id={d['id']:2d}  name={d['name']:8s}  type={d['menu_type']:8s}  "
            f"path={d['path']:35s}  parent={d['parent_id']:2d}  "
            f"component={str(d['component']):30s}  redirect={d['redirect']}"
        )
    await db.close()

asyncio.run(check())
