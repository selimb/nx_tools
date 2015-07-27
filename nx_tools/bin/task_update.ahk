#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

logfile = %1%
Time1 := A_Now
FormatTime, new1, %time1% ,yyyy-MM-ddTHH:mmZ

title=NX11 Update
FileAppend, `n%new1%`n, %logfile%
If ErrorLevel
    logfile = %logfile%bak
RunWait %comspec% /c nx_tools_utils check nx11,, Hide UseErrorLevel
err = %ErrorLevel%
Sleep 10
IfEqual, err, 200
{
    MsgBox, 0, %title%, Nothing new for NX11, 3
    FileAppend, Nothing New`n, %logfile%
    return
}
IfEqual, err, 203
{
    option =
    msg = update
    goto, Update
}
IfEqual, err, 201
{
    msg = build
    option = --%msg%
    goto, Update
}
IfEqual, err, 202
{
    msg = patch
    option = --%msg%
    goto, Update
}
MsgBox Task failed to run.`nContact author.`n%err%
return

Update:
FileAppend, Update Available->, %logfile%
wait=10
MsgBox, 4100, %title%, New NX11 %msg% found. Do you want to update now?`nThis message will timeout in %wait% seconds, %wait%
IfMsgBox, No
{
    FileAppend, No`n, %logfile%
    return
}
FileAppend, Yes`n, %logfile%
cmd = nx_tools --no-upgrade update nx11 %option%
FileAppend, Run: %cmd%`n, %logfile%
RunWait, %comspec% /c %cmd% >> %logfile%,, Hide
MsgBox Update Complete.
