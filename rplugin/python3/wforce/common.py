def write_msg(vim, msg):
    vim.command("echomsg '%s'" % msg)


def write_err_msg(vim, msg):
    vim.command("echohl Error | echomsg '%s' | echohl None" % msg)
