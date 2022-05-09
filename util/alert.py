def red_error(account):
    return ('[bold red]' + account + '[/]')
def log_red_error(log, account):
    return log.error(red_error(account), extra={"markup": True})