def make_path(*args: str, is_file: bool) -> str:
    args = [i.rstrip("/") for i in args if i]
    slash = "" if is_file else "/"
    path = ("/".join(args) + slash) if len(args) > 1 else (args[0] + slash) if len(args) == 1 else ""
    return path
