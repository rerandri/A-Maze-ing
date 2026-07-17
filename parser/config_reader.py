from typing import TextIO


def _parse_line(line: str) -> tuple[str, object] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    if "=" not in line:
        raise ValueError(
            "Config line missing '=' separator:"
            f" '{line[:40]}{'...' if len(line) > 40 else ''}'"
        )

    key, value = line.split("=", 1)
    key = key.strip().upper()
    value = value.strip()
    value_lower = value.lower()

    if key in ("WIDTH", "HEIGHT"):
        return key, int(value)
    if key in ("ENTRY", "EXIT"):
        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError(
                f"Invalid coordinate format for"
                f" '{key}': expected 'x,y' but got '{value}'"
            )
        return key, (int(parts[0]), int(parts[1]))
    if key == "PERFECT":
        if value_lower not in ("true", "false"):
            raise ValueError(
                f"Invalid boolean value for"
                f" '{key}': expected 'true' or 'false', got '{value}'"
            )
        return key, value_lower == "true"
    if key == "SEED":
        return key, int(value) if value_lower != "none" else None

    return key, value


def read_config_file(file_obj: TextIO) -> dict[str, object]:
    config: dict[str, object] = {}
    for line in file_obj:
        parsed = _parse_line(line)
        if parsed:
            key, value = parsed
            config[key] = value
    return config
