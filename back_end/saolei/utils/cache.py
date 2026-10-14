def maybe_bytes_to_str(value):
    if isinstance(value, bytes):
        return value.decode()
    return value
