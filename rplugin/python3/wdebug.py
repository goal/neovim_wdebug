import os
from pathlib import Path
import time
import pynvim as nvim

def write_msg(vim, msg):
    vim.command("echomsg '%s'" % msg)

def write_err_msg(vim, msg):
    vim.command("echohl Error | echomsg '%s' | echohl None" % msg)

def wait_file_content(file_path, old_size, total_wait_secs, check_internal, check_content):
    wait_secs = 0
    while wait_secs < total_wait_secs:
        time.sleep(check_internal)
        wait_secs += check_internal

        size = file_path.stat().st_size
        if size > old_size:
            with open(file_path) as f:
                f.seek(old_size)
                c = f.read()
                if check_content in c:
                    return True
    return False


@nvim.plugin
class Work(object):

    def __init__(self, vim):
        self.vim = vim
        self.vim.command('nnoremap <C-x>j :Rd<cr>')
        self.vim.command('nnoremap <C-x>k :Rdv<cr>')
        self.vim.command('nnoremap <C-x>u :Ru<cr>')

    @nvim.command('Rdv', range='', nargs='*', sync=True)
    def rdv_cmd(self, args, range):
        line = self.vim.current.line
        words = line.split()
        self._debug_values(words)

    @nvim.command('Rd', range='', nargs='*', sync=True)
    def rd_cmd(self, args, range):
        line = self.vim.current.line
        s = line.replace("...", "").replace("*", "")
        s = s[s.index("("):s.index(")")]
        vs = []
        for x in s.split(","):
            t, v = x.strip().split()
            vs.append(v)
        self._debug_values(vs)

    @nvim.command('Ru', range='', nargs='*', sync=False)
    def ru_cmd(self, args, range):
        filename = self.vim.current.buffer.name
        cur_dir = Path(".").absolute()
        files = cur_dir.glob("**/online.log")

        now = time.time()

        for f in files:
            st = f.stat()
            if now - st.st_mtime < 6:
                write_msg(self.vim, "find running gamed: %s" % f.parent.name)
                break
        else:
            write_err_msg(self.vim, "no running gamed found!")
            return

        gamed_log = f.parent / "gamed.log"
        st = gamed_log.stat()
        old_size = st.st_size

        rel_filename = os.path.relpath(filename, f.cwd())
        with open(f.parent.parent.parent / "etc/autoupdate.ini", "w") as uf:
            uf.write("[gamed]\n%s" % rel_filename)

        update_msg = "update succ=" + rel_filename[:-2]
        if wait_file_content(gamed_log, old_size, 5, 1, update_msg):
            write_msg(self.vim, "update succ")
        else:
            write_err_msg(self.vim, "update fail")


    def _debug_values(self, values):
        line = "debug_message(\"" + ", ".join(
            "%s=%%O" % v for v in values) + "\", " + ", ".join(values) + ");"
        cw = self.vim.current.window
        r, c = cw.cursor
        spaces = " " * self.vim.call("cindent", r)
        self.vim.current.line = spaces + line
