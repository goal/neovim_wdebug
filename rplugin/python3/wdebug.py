import os
from pathlib import Path
import time
import subprocess
import re
import random
import string

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


def try_find_func_definition(vim):
    p_line = re.compile(r"^[^=]+(\s|\*)[^=]+\(.*\)$")
    idx = cur_line = vim.current.line
    buf = vim.current.buffer
    lines = buf.splitlines()
    while idx > 0:
        idx -= 1
        cur_line = lines[idx]
        if p_line.match(cur_line):
            return cur_line
    return ""


@nvim.plugin
class Work(object):

    def __init__(self, vim):
        self.vim = vim
        self.vim.command('nnoremap <C-x>j :Rd<cr>')
        self.vim.command('nnoremap <C-x>k :Rdv<cr>')
        self.vim.command('nnoremap <C-x>u :Ru<cr>')
        self.vim.command('nnoremap <C-x>c :Run<cr>')

    @nvim.command('Rdv', range='', nargs='*', sync=True)
    def rdv_cmd(self, args, range):
        line = self.vim.current.line
        words = line.split()
        self._debug_values(words)

    @nvim.command('Rd', range='', nargs='*', sync=True)
    def rd_cmd(self, args, range):
        line = self.vim.current.line
        if not line.strip():
            line = try_find_func_definition(self.vim)
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
        chars = string.ascii_letters + string.digits
        firstn = random.randrange(0, 6)
        ustr = random.choice(chars) * firstn + random.choice(chars) * (5 - firstn)
        line = 'F_ERROR("%s. %s.", %s);' % (ustr, ','.join('%s=%%O' % v for v in values),
                                            ', '.join(values))
        cw = self.vim.current.window
        r, c = cw.cursor
        spaces = " " * self.vim.call("cindent", r)
        self.vim.current.line = spaces + line

    def _show_quickfix(self):
        # g:loaded_session test for denite-extra
        if self.vim.eval("g:loaded_session") and self.vim.call("exists", ":Denite"):
            self.vim.command("Denite quickfix")
        else:
            self.vim.command("cwindow")

    def _close_quickfix(self):
        self.vim.command("cclose")

    @nvim.command('Run', range='', nargs='*', sync=True)
    def run_cmd(self, args, range):
        filename = self.vim.current.buffer.name
        cur_dir = Path(".").absolute()
        rel_filename = os.path.relpath(filename, cur_dir)

        p = subprocess.Popen(
            ["../engine/engine.nostrip", "-l", "./", "-r", rel_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        outdata, errdata = p.communicate()

        all_lines = errdata.decode("utf8").splitlines()
        error_patterns = {".+ line [\d]+: .*": "%f\ line\ %l:\ %m"}

        # clear quickfix list
        self.vim.call("setqflist", [], "f")

        has_error = False
        for pattern, efm in error_patterns.items():
            result = {"lines": [], "efm": efm}
            p = re.compile(pattern)
            for line in all_lines:
                if p.match(line):
                    result["lines"].append(line)

            if result["lines"]:
                has_error = True
                # add to quickfix list
                self.vim.call("setqflist", [], "a", result)

        if has_error:
            self._show_quickfix()
        else:
            self._close_quickfix()
            write_msg(self.vim, "compile success!")
