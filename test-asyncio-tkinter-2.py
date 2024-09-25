#! /usr/bin/env python3

'''
This program demonstrates mixing asyncio and tkinter.
'''

import asyncio
import random
import sys
import threading

import tkinter as tk
from tkinter import messagebox

    
async def asyncioTask(url: int):
    '''
    An Async I/O Task.
    '''
    sec = random.randint(1, 8)
    await asyncio.sleep(sec)
    return 'url: {}\tsec: {}'.format(url, sec)


async def asyncioTasks():
    '''
    Create and start 10 Async I/O Tasks.
    '''
    tasks = [asyncio.create_task(asyncioTask(n)) for n in range(10)]
    completed, pending = await asyncio.wait(tasks)
    results = [task.result() for task in completed]
    print('\n'.join(results))


def asyncioMain():
    '''
    Starts the Ansyc I/O event loop.
    '''
    asyncio.run(asyncioTasks())


def guiTasks(n: int):
    messagebox.showinfo(message=f'Performing Task {n}')


def guiMain():
    root = tk.Tk()
    body = tk.Frame(master=root)
    body.pack(anchor=tk.CENTER, fill=tk.BOTH, padx=10, pady=10)
    tk.Button(master=body, text='Task 1', command=lambda: guiTasks(1)).pack(anchor=tk.N, fill=tk.X, pady=(0, 5))
    tk.Button(master=body, text='Task 2', command=lambda: guiTasks(2)).pack(anchor=tk.N, fill=tk.X, pady=(0, 5))
    tk.Button(master=body, text='Task 3', command=lambda: guiTasks(3)).pack(anchor=tk.N, fill=tk.X, pady=(0, 5))
    tk.Button(master=body, text='Exit', command=root.destroy).pack(anchor=tk.N, fill=tk.X, pady=(5, 0))
    root.mainloop()


if __name__ == '__main__':

    guit = threading.Thread(
        target = guiMain,
        name = 'GUI',
    )

    aiot = threading.Thread(
        target= asyncioMain,
        name = 'Async I/O',
    )

    guit.start()

    aiot.start()

    aiot.join()
    print('Async I/O complete')

    guit.join()
    print('Done')

    sys.exit(0)
