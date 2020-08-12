import random


# capitalizes the second character in the string, for sure, no matter what
def cap_second(value):
    return '%s%s' % (str(value)[0] if random.random() > 0.5 else str(value)[0].lower(),str(value)[1:].capitalize() if random.random() < 0.5 else str(value)[1:].title()) if len(str(value)) > 1 else cap_second('%s%s' % (value,value))
