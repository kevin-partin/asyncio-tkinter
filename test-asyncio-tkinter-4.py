#! /usr/bin/env python3

'''
This program demonstrates mixing asyncio and tkinter.
'''

import asyncio
from collections.abc import Callable
import random
import sys
import threading
import time

import tkinter as tk
from tkinter import messagebox


event = threading.Event()

# -------------------------------------------------------------------------

class EventMonitor():

    def __init__(self, event: threading.Event, callback: Callable, timeout: float = 0.1) -> None:
        '''
        Event Montor

            event - The event to monitor.

            callback - The callback to evaluate when the event is true.
        '''

        self.event = event
        self.event.clear()

        self.callback = callback
        self.timeout  = timeout

        self.enabled = False

        self.thread: threading.Thread = None

    # -------------------------------------------------------------------------

    def __del__(self) -> None:
        '''
        Delete the event monitor.
        '''
        self.disable()

    # -------------------------------------------------------------------------

    def disable(self) -> None:
        '''
        Disable the event monitor.
        '''
        self.enabled = False

        # Wait for the thread to terminate.
        if self.thread and self.thread.is_alive():
            self.thread.join()

        self.thread = None

    # -------------------------------------------------------------------------

    def enable(self) -> None:
        '''
        Enable the event monitor.
        '''
        if not self.enabled:
            self.enabled = True
            self.thread = threading.Thread(target=self._monitor, name='Event Monitor')
            self.thread.start()

    # -------------------------------------------------------------------------

    def reset(self, delay: float = 5.0) -> None:
        '''
        Reset the event monitor.
        '''
        self.disable()
        time.sleep(delay)
        self.enable()

    # -------------------------------------------------------------------------

    def restart(self, delay: float = 5.0) -> None:
        '''
        Restart the event monitor.
        '''
        self.reset(delay)

    # -------------------------------------------------------------------------

    def start(self) -> None:
        '''
        Start the event monitor.
        '''
        self.enable()

    # -------------------------------------------------------------------------

    def stop(self) -> None:
        '''
        Stop the event monitor.
        '''
        self.disable()

    # -------------------------------------------------------------------------

    def _monitor(self) -> None:
        '''
        Monitor the event.
        '''
        while self.enabled:
            if self.event.wait(timeout=self.timeout):
                self.callback()
                self.event.clear()

# -------------------------------------------------------------------------

async def asyncioTask(url: int):
    '''
    An Async I/O Task.
    '''
    sec = random.randint(1, 8)
    await asyncio.sleep(sec)
    return 'url: {}\tsec: {}'.format(url, sec)

# -------------------------------------------------------------------------

async def asyncioTasks():
    '''
    Create and start 10 Async I/O Tasks.
    '''
    event.clear()
    tasks = [asyncio.create_task(asyncioTask(n)) for n in range(10)]
    completed, pending = await asyncio.wait(tasks)
    results = [task.result() for task in completed]
    print('\n'.join(results))
    event.set()

# -------------------------------------------------------------------------

def asyncioMain():
    '''
    Starts the Ansyc I/O event loop.
    '''
    asyncio.run(asyncioTasks())

# -------------------------------------------------------------------------

def guiTasks(n: int):
    messagebox.showinfo(message=f'Performing Task {n}')

# -------------------------------------------------------------------------

def guiMain(exitCallback: Callable):

    def _exit(master: tk.Tk, exitCallback: Callable) -> None:
        exitCallback()
        master.destroy()

    root = tk.Tk()

    body = tk.Frame(master=root)
    body.pack(anchor=tk.CENTER, fill=tk.BOTH, padx=10, pady=10)

    tk.Button(master=body, text='Task 1', command=lambda: guiTasks(1)).pack(anchor=tk.N, fill=tk.X, pady=(0, 5))
    tk.Button(master=body, text='Task 2', command=lambda: guiTasks(2)).pack(anchor=tk.N, fill=tk.X, pady=(0, 5))
    tk.Button(master=body, text='Task 3', command=lambda: guiTasks(3)).pack(anchor=tk.N, fill=tk.X, pady=(0, 5))

    tk.Button(master=body, text='Exit', command=lambda: _exit(root, exitCallback)).pack(anchor=tk.N, fill=tk.X, pady=(5, 0))

    root.mainloop()

# -------------------------------------------------------------------------

if __name__ == '__main__':

    em = EventMonitor(
        event    = event,
        callback = lambda: messagebox.showinfo(message='Async I/O Tasks complete.'),
    )

    guit = threading.Thread(
        target = guiMain,
        name   = 'GUI',
        args   = [em.stop,],
    )

    aiot = threading.Thread(
        target = asyncioMain,
        name   = 'Async I/O',
    )

    em.start()
    guit.start()
    aiot.start()

    aiot.join()
    print('Async I/O complete')

    guit.join()
    print('Done')

    # em.stop()

    sys.exit(0)
