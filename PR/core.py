
def reverse(string):
    string = string[::-1]
    return string

def square(num):
    try:
        float(num)
        return num**2
    except ValueError:
        return False
