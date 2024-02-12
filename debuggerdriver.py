##===-- debuggerdriver.py ------------------------------------*- Python -*-===##
##
# Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
##
##===----------------------------------------------------------------------===##


import lldb
import lldbutil
from lldbutil import *
import sys
from threading import Thread

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6 import uic, QtWidgets, QtCore
#global process
#process = None

def breakpointHandlerDriver(dummy, frame, bpno, err):
    print("breakpointHandlerDriver ...")
    print("YESSSSSSS GETTTTTTTIIIIINNNNNNNGGGGG THERE!!!!!!")

class DebuggerDriverSignals(QObject):
    event_queued = QtCore.pyqtSignal(object)
  
class DebuggerDriver(Thread):
    """ Drives the debugger and responds to events. """
    
    
    signals = None
    
    def __init__(self, debugger, event_queue):
        Thread.__init__(self)
        self.signals = DebuggerDriverSignals()
        self.event_queue = event_queue
        # This is probably not great because it does not give liblldb a chance
        # to clean up
        self.daemon = True
        self.initialize(debugger)

    def initialize(self, debugger):
        print("INITIALISING DRIVER!!!")
        self.done = False
        self.debugger = debugger
        self.listener = debugger.GetListener()
        if not self.listener.IsValid():
            raise "Invalid listener"

        self.listener.StartListeningForEventClass(self.debugger,
                                                  lldb.SBTarget.GetBroadcasterClassName(),
                                                  lldb.SBTarget.eBroadcastBitBreakpointChanged
                                                  #| lldb.SBTarget.eBroadcastBitModuleLoaded
                                                  #| lldb.SBTarget.eBroadcastBitModuleUnloaded
                                                  | lldb.SBTarget.eBroadcastBitWatchpointChanged
                                                  #| lldb.SBTarget.eBroadcastBitSymbolLoaded
                                                  )

        self.listener.StartListeningForEventClass(self.debugger,
                                                  lldb.SBThread.GetBroadcasterClassName(),
                                                  lldb.SBThread.eBroadcastBitStackChanged
                                                  #  lldb.SBThread.eBroadcastBitBreakpointChanged
                                                  | lldb.SBThread.eBroadcastBitThreadSuspended
                                                  | lldb.SBThread.eBroadcastBitThreadResumed
                                                  | lldb.SBThread.eBroadcastBitSelectedFrameChanged
                                                  | lldb.SBThread.eBroadcastBitThreadSelected
                                                  )

        self.listener.StartListeningForEventClass(self.debugger,
                                                  lldb.SBProcess.GetBroadcasterClassName(),
                                                  lldb.SBProcess.eBroadcastBitStateChanged
                                                  | lldb.SBProcess.eBroadcastBitInterrupt
                                                  | lldb.SBProcess.eBroadcastBitSTDOUT
                                                  | lldb.SBProcess.eBroadcastBitSTDERR
                                                  | lldb.SBProcess.eBroadcastBitProfileData
                                                  )
        self.listener.StartListeningForEventClass(self.debugger,
                                                  lldb.SBCommandInterpreter.GetBroadcasterClass(),
                                                  lldb.SBCommandInterpreter.eBroadcastBitThreadShouldExit
                                                  | lldb.SBCommandInterpreter.eBroadcastBitResetPrompt
                                                  | lldb.SBCommandInterpreter.eBroadcastBitQuitCommandReceived
                                                  | lldb.SBCommandInterpreter.eBroadcastBitAsynchronousOutputData
                                                  | lldb.SBCommandInterpreter.eBroadcastBitAsynchronousErrorData
                                                  )

    def createTarget(self, target_image, args=None):
        self.handleCommand("target create %s" % target_image)
        if args is not None:
            self.handleCommand("settings set target.run-args %s" % args)

    def attachProcess(self, pid):
        self.handleCommand("process attach -p %d" % pid)
        pass

    def loadCore(self, corefile):
        self.handleCommand("target create -c %s" % corefile)
        pass

    def setDone(self):
        self.done = True

    def isDone(self):
        return self.done

    def getPrompt(self):
        return self.debugger.GetPrompt()

    def getCommandInterpreter(self):
        return self.debugger.GetCommandInterpreter()

    def getSourceManager(self):
        return self.debugger.GetSourceManager()

    def setSize(self, width, height):
        # FIXME: respect height
        self.debugger.SetTerminalWidth(width)

    def getTarget(self):
        return self.debugger.GetTargetAtIndex(0)

    def handleCommand(self, cmd):
        ret = lldb.SBCommandReturnObject()
        self.getCommandInterpreter().HandleCommand(cmd, ret)
        return ret

    def eventLoop(self):
#       global process
        while not self.isDone():
            event = lldb.SBEvent()
            got_event = self.listener.WaitForEvent(lldb.UINT32_MAX, event)
            print(f'GOT-EVENT: {event} / {event.GetType()}')
            desc = lldbutil.get_description(event)
            print('Event description:', desc)
            print('Event data flavor:', event.GetDataFlavor())
#           if event.GetDataFlavor() == "Breakpoint::BreakpointEventData":
#             print("GOT BREAKPOINT CHANGE!!!")
#           global process
#           print('Process state:', lldbutil.state_type_to_str(process.GetState()))
            print()
            
            # eBroadcastBitSTDOUT
#           if event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
#             stdout = process.GetSTDOUT(256)
#             if stdout is not None and len(stdout) > 0:
#               message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
            if got_event and not event.IsValid():
                self.winAddStr("Warning: Invalid or no event...")
                continue
            elif not event.GetBroadcaster().IsValid():
                continue
            
            self.event_queue.put(event)
            self.signals.event_queued.emit(event)
            
    def run(self):
        self.eventLoop()

    def terminate(self):
        lldb.SBDebugger.Terminate()
        sys.exit(0)


def createDriver(debugger, event_queue):
    driver = DebuggerDriver(debugger, event_queue)
    # driver.start()
    # if pid specified:
    # - attach to pid
    # else if core file specified
    # - create target from corefile
    # else
    # - create target from file
    # - settings append target.run-args <args-from-cmdline>
    # source .lldbinit file

    return driver