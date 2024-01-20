#!/usr/bin/env python

# ----------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
# On MacOSX csh, tcsh:
#   setenv PYTHONPATH /Developer/Library/PrivateFrameworks/LLDB.framework/Resources/Python
# On MacOSX sh, bash:
#   export PYTHONPATH=/Developer/Library/PrivateFrameworks/LLDB.framework/Resources/Python
# ----------------------------------------------------------------------

import lldb
import os
import sys


def breakpoint_cb(frame, bpno, err):
    print('breakpoint callback')
    return False

def disassemble_instructions(insts):
    for i in insts:
        print(i)


def usage():
    print("Usage: disasm.py [-n name] executable-image")
    print("       By default, it breaks at and disassembles the 'main' function.")
    sys.exit(0)


if len(sys.argv) == 2:
    fname = "main"
    exe = sys.argv[1]
elif len(sys.argv) == 4:
    if sys.argv[1] != "-n":
        usage()
    else:
        fname = sys.argv[2]
        exe = sys.argv[3]
else:
    usage()

# Create a new debugger instance
debugger = lldb.SBDebugger.Create()

# When we step or continue, don't return from the function until the process
# stops. We do this by setting the async mode to false.
debugger.SetAsync(False)

print(f'debugger: {debugger}')
# Create a target from a file and arch
print("Creating a target for '%s'" % exe)

target = debugger.CreateTargetWithFileAndArch(exe, None) # lldb.LLDB_ARCH_DEFAULT)

if target:
    print("Has target")
    # If the target is valid set a breakpoint at main
    main_bp = target.BreakpointCreateByName(fname, target.GetExecutable().GetFilename())
    main_bp.SetScriptCallbackFunction('breakpoint_cb')
    print(main_bp)
    
#   breakpoint = target.BreakpointCreateByAddress(0x100003f60) # 0x100003c90)
#   breakpoint.SetEnabled(True)
#   breakpoint.SetScriptCallbackFunction('breakpoint_cb')
#   print(breakpoint)
        
    # Launch the process. Since we specified synchronous mode, we won't return
    # from this function until we hit the breakpoint at main
    process = target.LaunchSimple(None, None, os.getcwd())
    print(process)
    # This causes an error and the callback is never called.
#   opt = lldb.SBExpressionOptions()
#   opt.SetIgnoreBreakpoints(False)
#   v = target.EvaluateExpression('main()', opt)
#   err = v.GetError()
#   if err.fail:
#       print(err.GetCString())
#   else:
#       print(v.value)
#   error = lldb.SBError()
#   
#   sb_launch_info = lldb.SBLaunchInfo(None)
#   # sb_launch_info.SetExecutableFile(exe, True)
#   
#   process = target.Launch(sb_launch_info, error) #debugger.GetListener(), None, None, None, '/tmp/stdout.txt', None, None, 0, True, error)
                            
    # Make sure the launch went ok
    if process:
        print("Process launched OK")
        # Print some simple process info
        state = process.GetState()
        print(process)
        if state == lldb.eStateStopped:
            print("state == lldb.eStateStopped")
            # Get the first thread
            thread = process.GetThreadAtIndex(0)
            if thread:
                # Print some simple thread info
                print(thread)
                # Get the first frame
                frame = thread.GetFrameAtIndex(0)
                if frame:
                    # Print some simple frame info
                    print(frame)
                    function = frame.GetFunction()
                    # See if we have debug info (a function)
                    if function:
                        # We do have a function, print some info for the
                        # function
                        print(function)
                        # Now get all instructions for this function and print
                        # them
                        insts = function.GetInstructions(target)
                        disassemble_instructions(insts)
                    else:
                        # See if we have a symbol in the symbol table for where
                        # we stopped
                        symbol = frame.GetSymbol()
                        if symbol:
                            # We do have a symbol, print some info for the
                            # symbol
                            print(symbol)
                            # Now get all instructions for this symbol and
                            # print them
                            insts = symbol.GetInstructions(target)
                            disassemble_instructions(insts)

                    registerList = frame.GetRegisters()
                    print(
                        "Frame registers (size of register set = %d):"
                        % registerList.GetSize()
                    )
                    for value in registerList:
                        # print value
                        print(
                            "%s (number of children = %d):"
                            % (value.GetName(), value.GetNumChildren())
                        )
                        for child in value:
                            print(
                                "Name: ", child.GetName(), " Value: ", child.GetValue()
                            )

            print(
                "Hit the breakpoint at main, enter to continue and wait for program to exit or 'Ctrl-D'/'quit' to terminate the program"
            )
            next = sys.stdin.readline()
            if not next or next.rstrip("\n") == "quit":
                print("Terminating the inferior process...")
                process.Kill()
            else:
                # Now continue to the program exit
                process.Continue()
                # When we return from the above function we will hopefully be at the
                # program exit. Print out some process info
                print(process)
        elif state == lldb.eStateExited:
            print("Didn't hit the breakpoint at main, program has exited...")
        else:
            print(
                "Unexpected process state: %s, killing process..."
                % debugger.StateAsCString(state)
            )
            process.Kill()
    else:
        print("Process NOT launched!!!")
else:
    print("Has NO target")

lldb.SBDebugger.Terminate()
