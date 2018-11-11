import asyncio
import random
import time
import aiohttp
import json
import os.path

from vkscript_code import gen_vkcall, resp_to_id_type_members
from storage import Storage_groups
from config import access_token

REQUESTS_PER_SECOND = 20
WORKERS_COUNT = 70

FST_ID = 1
LST_ID = 172741352

FILE_PROCESSED = "groups_processed.bin"

st = Storage_groups(FST_ID, LST_ID)
if os.path.exists(FILE_PROCESSED):
    st.load(FILE_PROCESSED)
else:
    st.create_empty()

async def fetch(session, url, data):
    async with session.post(url, data=data) as response:
        return await response.text()

async def fetch_api(batches, code):
    url_exec = "https://api.vk.com/method/execute"
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        data_dict = {
            "access_token": access_token,
            "v": "5.87",
            "code": code,
        }
        resp_str = await fetch(session, url_exec, data_dict)
        resp_data = json.loads(resp_str)
        if "error" in resp_data:
            resp_data['request_params'] = ""
            print (resp_data)
        else:
            calls_resp = resp_data["response"]
            for group_data in resp_to_id_type_members(batches, calls_resp):
                st.update_group_info(*group_data)

async def worker(name, queue):
    while True:
        try:
            code = await queue.get()
            print(name)
            if code is not None:
                await fetch_api(*code)
            else:
                break
        except Exception as e:
            print("ERROR:", e)
        finally:
            queue.task_done()

async def req_putter(req_queue):
    started_at = time.time()

    groups_it = st.get_undone()
    vkcalls = gen_vkcall(groups_it)
    try:
        vkcall = next(vkcalls)
        while True:
            t_start = time.time()
            for i in range(REQUESTS_PER_SECOND):
                try:
                    req_queue.put_nowait(vkcall)
                except asyncio.QueueFull as e:
                    break
                else:
                    vkcall = next(vkcalls)

            await asyncio.sleep(1 - time.time() + t_start)

    except StopIteration:
        pass

    for _ in range(WORKERS_COUNT):
        await req_queue.put(None)

    await req_queue.join()

    execute_time = time.time() - started_at
    print("execution time", execute_time)

    st.dump(FILE_PROCESSED)

async def main():
    queue = asyncio.Queue(REQUESTS_PER_SECOND)

    tasks = [asyncio.create_task(req_putter(queue))]

    for i in range(WORKERS_COUNT):
        task = asyncio.create_task(worker(f'worker-{i}', queue))
        tasks.append(task)

    await asyncio.gather(*tasks, return_exceptions=True)


asyncio.run(main())
