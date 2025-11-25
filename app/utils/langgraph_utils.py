def read_markdown_file(file_path):
    """
    Reads a markdown file and returns its content as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise
    except Exception as e:
        raise