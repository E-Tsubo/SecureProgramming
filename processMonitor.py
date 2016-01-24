# -*- coding: utf-8 -*-

# WMIを利用したプロセス監視ツール
# プロセス監視の際に、実行プロセスの権限を取得する
# なお、UAC利用の環境だと、[SeChangeNotifyPrivilege]しかキャッチできない
# これは、UAC環境では起動時にフィルターされたトークンでプロセスが起動されるためである。
# その後、ユーザが許諾すれば、完全なトークンで子プロセスが起動される。
# 参考URL:http://www.atmarkit.co.jp/fwin2k/vista_feature/08uac02/08uac02_01.html

import win32con
import win32api
import win32security

# The Python WMI module is a lightweight wrapper on top of the pywin32 extensions,
# and hides some of the messy plumbing needed to get Python to talk to the WMI API.
# It’s pure Python and should work with any version of Python
# from 2.1 onwards (list comprehensions) and any recent version of pywin32.
#
# https://pypi.python.org/pypi/WMI/
import wmi

import sys
import os

def getProcessPrivileges(pid):
    try:
        # 対象のプロセスへのハンドルを取得
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION,False,pid)

        # プロセストークンを開く
        htok = win32security.OpenProcessToken(hproc,win32con.TOKEN_QUERY)

        # 有効化されている権限のリストを取得
        privs = win32security.GetTokenInformation(htok, win32security.TokenPrivileges)

        priv_list = []
        for priv_id, priv_flag in privs:
            if priv_flag == 3:
                priv_list.append(win32security.LookupPrivilegeName(None,priv_id))

    except:
        priv_list.append("N/A")

    return "|".join(priv_list)

def logToFile(message):
    fd = open("process_monitor_log.csv", "ab")
    fd.write("%s\r\n" % message)
    fd.close()

    return

# ログファイルのヘッダー作成
logToFile("Time, User, Executable, CommandLine, PID, Parent PID, Privileges")

# WMIインターフェイスのインスタンスを生成
c = wmi.WMI()

# プロセス監視を開始(プロセス生成のイベントを監視)
# 他にもイベントを監視することは可能
# “creation”, “deletion”, “modification” or “operation”
process_watcher = c.Win32_Process.watch_for("Creation")

while True:
    try:

        new_process = process_watcher()

        proc_owner  = new_process.GetOwner()
        proc_owner  = "%s\\%s" % (proc_owner[0],proc_owner[2])
        create_date = new_process.CreationDate
        executable  = new_process.ExecutablePath
        cmdline     = new_process.CommandLine
        pid         = new_process.ProcessId
        parent_pid  = new_process.ParentProcessId

        privileges = getProcessPrivileges(pid)

        process_log_message = "%s, %s, %s, %s, %s, %s, %s\r\n" % \
        (create_date, proc_owner, executable, cmdline, pid, parent_pid, privileges )

        print process_log_message

        logToFile( process_log_message )

    except:
        pass
