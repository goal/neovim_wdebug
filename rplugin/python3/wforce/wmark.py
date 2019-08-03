import string
import pynvim as nvim

from wforce.common import write_msg, write_err_msg

@nvim.plugin
class WMark(object):

    def __init__(self, vim):
        self.vim = vim
        try:
            self.marks = self.vim.eval("g:wmark_syms")
        except nvim.api.nvim.NvimError as e:
            self.marks = string.ascii_lowercase

    @nvim.command("AutoMark", range="", nargs="*", sync=True)
    def auto_mark(self, args, range):
        try:
            mark_count = self.vim.eval("g:mark_count")
        except nvim.api.nvim.NvimError as e:
            mark_count = 0
        idx = mark_count % len(self.marks)
        sym = self.marks[idx]
        self.vim.command(f"k {sym}")
        self.vim.command(f"let g:mark_count={mark_count+1}")
        write_msg(self.vim, f"Set mark [{sym}]")
