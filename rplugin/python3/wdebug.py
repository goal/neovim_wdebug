import os
from pathlib import Path
import time
import pynvim as nvim


@nvim.plugin
class Work(object):

    def __init__(self, vim):
        self.vim = vim
        self.vim.command('nnoremap <C-x>j :Rd<cr>')
        self.vim.command('nnoremap <C-x>k :Rdv<cr>')

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

    @nvim.command('Ru', range='', nargs='*', sync=True)
    def ru_cmd(self, args, range):
        filename = self.vim.current.buffer.name
        cur_dir = Path(".").absolute()
        files = cur_dir.glob("**/online.log")

        for f in files:
            st = f.stat()
            if now - st.st_mtime < 6:
                self.vim.out_write("running gamed %s" % f.parent.parent)
                break
        else:
            self.vim.out_write("no running gamed found!")
            return

    def _debug_values(self, values):
        line = "debug_message(\"" + ", ".join(
            "%s=%%O" % v for v in values) + "\", " + ", ".join(values) + ");"
        cw = self.vim.current.window
        r, c = cw.cursor
        spaces = " " * self.vim.call("cindent", r)
        self.vim.current.line = spaces + line
