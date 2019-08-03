import pynvim as nvim


@nvim.plugin
class WMark(object):

    def __init__(self, vim):
        self.vim = vim

    @nvim.command("AutoMark", range="", nargs="*", sync=True)
    def auto_mark(self, args, range):
        try:
            mark_count = self.vim.eval("g:mark_count")
        except nvim.api.nvim.NvimError as e:
            mark_count = 0
        cur = mark_count % 26
        sym = chr(cur + 97)
        self.vim.command(f"k {sym}")
        self.vim.command(f"let g:mark_count={mark_count+1}")
