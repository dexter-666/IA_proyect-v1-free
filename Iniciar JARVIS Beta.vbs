' J.A.R.V.I.S — Lanzador con permisos de Administrador
' Auto-eleva vía UAC si no tiene privilegios de admin
Option Explicit

' ── Verificar si ya somos Admin ────────────────────────────────────────────────
Function IsAdmin()
    On Error Resume Next
    Dim shell
    Set shell = CreateObject("WScript.Shell")
    ' Intentar escribir en HKLM (solo funciona con admin)
    shell.RegRead "HKEY_USERS\S-1-5-19\Environment\TEMP"
    If Err.Number = 0 Then
        IsAdmin = True
    Else
        IsAdmin = False
    End If
    Err.Clear
    On Error GoTo 0
    Set shell = Nothing
End Function

' ── Si no somos Admin, re-lanzar elevado ──────────────────────────────────────
If Not IsAdmin() Then
    Dim objShell
    Set objShell = CreateObject("Shell.Application")
    objShell.ShellExecute "wscript.exe", Chr(34) & WScript.ScriptFullName & Chr(34), "", "runas", 0
    Set objShell = Nothing
    WScript.Quit 0
End If

' ── Ya somos Admin: lanzar JARVIS ─────────────────────────────────────────────
Dim ws, fso, d, py, cmd
Set ws  = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
d = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))

' Fijar el directorio de trabajo al directorio del script
ws.CurrentDirectory = d

py = d & ".venv\Scripts\pythonw.exe"
If Not fso.FileExists(py) Then
    py = d & ".venv\Scripts\python.exe"
End If
If Not fso.FileExists(py) Then
    MsgBox "JARVIS: ejecuta el archivo Instalar_JARVIS.bat primero para configurar el entorno.", 16, "JARVIS"
    WScript.Quit 1
End If

cmd = Chr(34) & py & Chr(34) & " " & Chr(34) & d & "main.py" & Chr(34)
ws.Run cmd, 1, False
Set ws  = Nothing
Set fso = Nothing

