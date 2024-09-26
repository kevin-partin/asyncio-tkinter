#! /usr/bin/env python3

'''
This program demonstrates the mixing of asyncio and tkinter.
'''

import tkinter as tk
from tkinter import messagebox
import asyncio
import threading
import random

    
async def one_url(url: int):
    """ One task. """
    sec = random.randint(1, 8)
    await asyncio.sleep(sec)
    return 'url: {}\tsec: {}'.format(url, sec)


async def do_urls():
    """ Creating and starting 10 tasks. """
    tasks = [asyncio.create_task(one_url(url)) for url in range(10)]
    completed, pending = await asyncio.wait(tasks)
    results = [task.result() for task in completed]
    print('\n'.join(results))


def _asyncio_thread(async_loop: asyncio.AbstractEventLoop):
    async_loop.run_until_complete(do_urls())


def do_asyncio_tasks(async_loop):
    """ Button-Event-Handler starting the asyncio part. """
    threading.Thread(target=_asyncio_thread, args=(async_loop,)).start()


def do_other_tasks():
    messagebox.showinfo(message='Tkinter is reacting.')


def main(async_loop):

    root = tk.Tk()
    root.title('asyncio-tkinter')
    root.resizable(False, False)

    body = tk.Frame(master=root)
    body.pack(anchor=tk.CENTER, fill=tk.BOTH, padx=10, pady=10)

    tk.Button(master=body, text='Asyncio Tasks', command=lambda:do_asyncio_tasks(async_loop)).pack(anchor=tk.N, fill=tk.X)
    tk.Button(master=body, text='Other Tasks', command=do_other_tasks).pack(anchor=tk.N, fill=tk.X)

    root.mainloop()


if __name__ == '__main__':
    async_loop = asyncio.new_event_loop()
    main(async_loop)

