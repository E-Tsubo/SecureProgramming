# -*- coding: utf-8 -*-
# こちらのコードをもとに修正を加えた
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
# https://github.com/oreilly-japan/black-hat-python-jp-support/blob/master/chapter-10/file_monitor.py
import tempfile
import threading
import win32file
import win32con
import os

# 監視対象ディレクトリ
dirs_to_monitor = ["C:\\WINDOWS\\Temp",tempfile.gettempdir()]

# ファイルへの変更に関する定数
FILE_CREATED      = 1
FILE_DELETED      = 2
FILE_MODIFIED     = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO   = 5

def startMonitor(path_to_watch):

    # フォルダを監視するスレッド本体
    FILE_LIST_DIRECTORY = 0x0001

    # 監視対象ディレクトリへのハンドルを入手
    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    while True:
        try:
            # 対象の変更に対しての通知を取得
            results = win32file.ReadDirectoryChangesW(
                h_directory,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None
            )

            # 変更対象のパス取得及び、対象へのアクションを取得
            for action, file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)

                if action == FILE_CREATED:
                    print "[ + ] Created %s" % full_filename
                elif action == FILE_DELETED:
                    print "[ - ] Deleted %s" % full_filename
                elif action == FILE_MODIFIED:
                    print "[ * ] Modified %s" % full_filename

                    # ファイル変更時には、ファイル内容のダンプ出力
                    print "[vvv] Dumping contents..."

                    try:
                        fd = open(full_filename,"rb")
                        contents = fd.read()
                        fd.close()
                        print contents
                        print "[^^^] Dump complete."
                    except:
                        print "[!!!] Failed."

                elif action == FILE_RENAMED_FROM:
                    print "[ > ] Renamed from: %s" % full_filename
                elif action == FILE_RENAMED_TO:
                    print "[ < ] Renamed to: %s" % full_filename
                else:
                    print "[???] Unknown: %s" % full_filename
        except:
            pass


for path in dirs_to_monitor:
    monitor_thread = threading.Thread(target=startMonitor,args=(path,))
    print "Spawning monitoring thread for path: %s" % path
    monitor_thread.start()
