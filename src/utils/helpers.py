import datetime
import json
import traceback

def chunk_text(text, max_chars=4000):
    """
    Split text into chunks for processing limits.
    """
    if not text:
        return []
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

def format_output(data, as_json=False, indent=2):
    """
    Format output for display. Supports JSON and pretty string.
    """
    if as_json:
        try:
            return json.dumps(data, indent=indent, ensure_ascii=False)
        except Exception:
            return str(data)
    if isinstance(data, dict):
        return "\n".join(f"{k}: {v}" for k, v in data.items())
    if isinstance(data, list):
        return "\n".join(str(item) for item in data)
    return str(data)

def log_error(error_message, exc=None):
    """
    Log errors with timestamp and optional exception traceback.
    """
    with open("error_log.txt", "a") as log_file:
        timestamp = datetime.datetime.now().isoformat()
        log_file.write(f"[{timestamp}] ERROR: {error_message}\n")
        if exc:
            log_file.write(traceback.format_exc() + "\n")

def log_info(message):
    """
    Log informational messages with timestamp.
    """
    with open("info_log.txt", "a") as log_file:
        timestamp = datetime.datetime.now().isoformat()
        log_file.write(f"[{timestamp}] INFO: {message}\n")

def safe_get(dct, keys, default=None):
    """
    Safely get a nested value from a dict.
    keys: list of keys to traverse.
    """
    val = dct
    try:
        for k in keys:
            val = val[k]
        return val
    except Exception:
        return default

def flatten_dict(d, parent_key='', sep='.'):
    """
    Flatten a nested dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def pretty_print_table(rows, headers=None):
    """
    Print a list of dicts or lists as a table.
    """
    if not rows:
        return ""
    if isinstance(rows[0], dict):
        headers = headers or list(rows[0].keys())
        lines = ["\t".join(headers)]
        for row in rows:
            lines.append("\t".join(str(row.get(h, "")) for h in headers))
        return "\n".join(lines)
    elif isinstance(rows[0], (list, tuple)):
        if headers:
            lines = ["\t".join(headers)]
        else:
            lines = []
        for row in rows:
            lines.append("\t".join(str(x) for x in row))
        return "\n".join(lines)
    return str(rows)

def get_current_timestamp(fmt="%Y-%m-%d %H:%M:%S"):
    """
    Returns the current timestamp as a formatted string.
    """
    return datetime.datetime.now().strftime(fmt)

def safe_int(val, default=0):
    """
    Safely convert a value to int, return default if conversion fails.
    """
    try:
        return int(val)
    except Exception:
        return default

def safe_float(val, default=0.0):
    """
    Safely convert a value to float, return default if conversion fails.
    """
    try:
        return float(val)
    except Exception:
        return default

def normalize_text(text):
    """
    Lowercase and strip whitespace from text.
    """
    return text.lower().strip() if isinstance(text, str) else text

def remove_duplicates(seq):
    """
    Remove duplicates from a list while preserving order.
    """
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

def merge_dicts(a, b):
    """
    Merge two dictionaries. Values from b overwrite those from a.
    """
    result = a.copy()
    result.update(b)
    return result

def safe_call(func, *args, **kwargs):
    """
    Call a function safely, return None if exception occurs.
    """
    try:
        return func(*args, **kwargs)
    except Exception:
        return None

def get_file_extension(filename):
    """
    Returns the file extension for a filename.
    """
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

def is_supported_filetype(filename):
    """
    Returns True if the file extension is supported for document comparison.
    """
    supported = {'txt', 'md', 'docx', 'pdf', 'csv', 'xlsx'}
    return get_file_extension(filename) in supported