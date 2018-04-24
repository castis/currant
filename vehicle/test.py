import asyncio

async def my_task(seconds):
    print("start sleeping for {} seconds".format(seconds))
    await asyncio.sleep(seconds)
    print("end sleeping for {} seconds".format(seconds))

all_tasks = asyncio.gather(my_task(1))
asyncio.ensure_future(my_task())
loop = asyncio.get_event_loop()
# loop.run_until_complete(all_tasks)
loop.run_forever()
loop.close()
