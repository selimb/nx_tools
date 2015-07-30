#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#SingleInstance force

hk = %1%
MsgBox Starting NX Tools Identifier with Hotkey: %hk%
Hotkey, %hk%, identify, on
Return

;======================================================
identify:
total=1
WinGet, active_name, ProcessName, A  ; Active window's process name
; If active process is not ugraf.exe, may proceed if there's only one NX running.
IfNotEqual, active_name, ugraf.exe
{
    ;SetTitleMatchMode, RegEx  ; Filter out Windows Explorer false positive.
    ;WinGet, nx_list, List, NX (\d){2}
    WinGet, nx_list, List, NX, History  ; NX Window should always contain History in the text.
    IfEqual, nx_list, 0
    {
        MsgBox Can't find NX process.
        Return  ; Must have at least one NX open.
    }
    IfGreater, nx_list, 1
    {
        total := nx_list
        Loop, %total%
        {
            the_ahk_id := nx_list%A_Index%
            WinGet, the_PID, PID, ahk_id %the_ahk_id%
            PID_Array%A_Index% := the_PID
        }
    }
    WinGet, PID_Array1, PID, NX
}
Else
{
    WinGet, PID_Array1, PID, A
}
title = NX Identifier
EnvGet, dir, USERPROFILE
filename=%dir%\.nx_identifier.temp
stop:=False
Loop, %total%
{
    the_PID := PID_Array%A_Index%
    the_msg = %A_Index%/%total%
    Display(the_PID, A_Index)
    WinWaitClose, %title%
    if stop
        break
}
FileDelete, %filename%
Display(NX_PID, index)
{
    global stop
    global title
    global hk
    global filename
    global total
    RunWait %comspec% /c nx_tools_utils find_entry %NX_PID% > %filename%,, UseErrorLevel Hide
    If ErrorLevel
    {
        MsgBox Oops. Something's wrong.
        ExitApp
    }
    FileRead, output, %filename%
    StringTrimRight, output, output, 2  ; Get rid of last empty line

    needle=NAME: (.*)\R
    FoundName := RegExMatch(output, needle, name)
    If FoundName
    {
        title=%name1%
        output := RegExReplace(output, needle)
    }
    Else
        title=NX Identifier
;-----------------------------------------------------
; GUI BLOCK
    Gui, Add, Edit, ReadOnly, %output%
    Gui, Add, Text,, %index%/%total%
    Gui, Show,, %title%
    Hotkey, IfWinActive, %title% ahk_class AutoHotkeyGUI
    Hotkey, Tab, GuiClose
    Hotkey, %hk%, GuiClose
    Return
    GuiEscape:
    stop:=True
    Gui, Destroy
    GuiClose:
    Gui, Destroy
; END GUI BLOCK
;------------------------------------------------------
    Return
}


