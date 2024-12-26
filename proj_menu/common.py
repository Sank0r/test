import hashlib
def get_md5_of_string(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()
