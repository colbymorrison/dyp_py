import asyncio

async def foo():
    return "what is"

async def bar():
    gos = [foo(), foo(), foo(), foo()]
    done, pending = await asyncio.wait(gos)

    files = list(map(lambda task: f"pdfs/{task.result()}", done))

    print(files)

asyncio.run(bar())
