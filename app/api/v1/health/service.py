def mask_dsn(dsn: str) -> str:
    if not dsn:
        return "<not-configured>"

    try:
        # Extract just the scheme (protocol) to show
        # what type of database it is
        scheme = dsn.split(":")[0] if ":" in dsn else "unknown"
        return f"<{scheme}-database-connection-redacted>"
    except Exception:
        return "<database-connection-redacted>"
