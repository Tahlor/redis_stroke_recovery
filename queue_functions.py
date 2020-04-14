def save_to_hard_drive(the_files):
    """
    Args:
        the_files: tuple, output_file_name, tempfile_path

    Returns:

    """
    file_name, tempfile = the_files
    with tempfile as f:
        data = f.read()
    with open(file_name, "wb") as f:
        f.write(data)
