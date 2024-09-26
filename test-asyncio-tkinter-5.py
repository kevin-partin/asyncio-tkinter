#! /usr/bin/env python3

'''
This program demonstrates the mixing of asyncio and tkinter.
'''

import asyncio
from collections.abc import Callable
from datetime import datetime
import sys
import threading
import time
from typing import NamedTuple

import tkinter as tk
import tkinter.ttk as ttk


class Events(NamedTuple):
    trigger  = threading.Event()
    shutdown = threading.Event()
    stopped  = threading.Event()

timestamp: datetime

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
        Monitor for an event occurance.
        '''
        while self.enabled:
            if self.event.wait(timeout=self.timeout):
                self.callback()
                self.event.clear()

# -------------------------------------------------------------------------

class IOManager:


    def __init__(self, *, events: Events) -> None:
        '''
        I/O Manager.
        '''
        self.events = events
        asyncio.run(self.main())


    async def main(self):
        '''
        I/O Manager Main Function.
        '''
        global timestamp

        self.events.trigger.clear()

        while not self.events.shutdown.is_set():

            # Update the data.
            timestamp = datetime.now()

            # Set the trigger event to indicate the data has been updated.
            self.events.trigger.set()
            await asyncio.sleep(1)
        
        self.events.stopped.set()

# -------------------------------------------------------------------------

class GUI:


    def __init__(self, *, events: Events) -> None:
        '''
        Graphical User Interface.
        '''

        self.events = events

        # Create an event monitor to refresh the GUI when the trigger event is set.
        self.eventMonitor = EventMonitor(self.events.trigger, self.refresh)
        self.eventMonitor.start()

        # Create the GUI.
        self.create()


    def exitButtonCallback(self) -> None:
        '''
        Callback for the Exit button.
        '''

        # Set the shutdown event.
        self.events.shutdown.set()

        # Wait for the stopped event to be set.
        self.events.stopped.wait()

        # Stop the event monitor.
        self.eventMonitor.stop()

        # Destroy the GUI.
        self.root.destroy()


    def create(self) -> None:
        '''
        Create the GUI.
        '''

        self.root = tk.Tk()
        self.root.title('asyncio-tkinter')
        self.root.resizable(False, False)

        body = ttk.Frame(master=self.root)
        body.pack(anchor=tk.CENTER, fill=tk.BOTH, padx=10, pady=10)

        self.timestamp = tk.StringVar()
        ttk.Label(master=body, text='Timestamp:').grid(row=0, column=0)
        ttk.Entry(master=body, textvariable=self.timestamp, width=23).grid(row=0, column=1)

        ttk.Button(master=body, text='Exit', command=self.exitButtonCallback).grid(row=1, column=0, columnspan=2, pady=(10, 0))


    def start(self) -> None:
        '''
        Start the GUI.
        '''
        self.root.mainloop()


    def refresh(self) -> None:
        '''
        Refresh the GUI.
        '''
        self.timestamp.set(timestamp.isoformat(timespec='milliseconds'))
        self.root.update()

# -------------------------------------------------------------------------

if __name__ == '__main__':

    # Create the GUI.
    gui = GUI(events=Events)

    # Create a thread to manage all I/O.
    threading.Thread(
        target = IOManager,
        name   = 'I/O Manager',
        kwargs = {'events': Events},
    ).start()

    # Start the GUI.
    gui.start()

    sys.exit(0)
