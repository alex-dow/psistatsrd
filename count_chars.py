from collections import Counter

def count_chars (s, mode = 0):
    """Counts the number of occurrences of every byte-value (0..255) in string
    and returns it in various ways.
    
    0 - an array with the byte-value as key and the frequency of every byte as value.
    1 - same as 0 but only byte-values with a frequency greater than zero are listed.
    2 - same as 0 but only byte-values with a frequency equal to zero are listed.
    3 - a string containing all unique characters is returned.
    4 - a string containing all not used characters is returned.
    """
    temp = {chr (_x) : 0 for _x in xrange (256)} # All ASCII Characters


    if mode == 0:
        temp.update (Counter (s))
        return temp
    elif mode == 1:
        temp.update (Counter (s))
        res = temp.copy ()
        for i, j in temp.iteritems ():
            if not j:
                res.pop (i)
        return res
    elif mode == 2:
        temp.update (Counter (s))
        res = temp.copy ()
        for i, j in temp.iteritems ():
            if j:
                res.pop (i)
        return res
    elif mode == 3:
        res = ""
        temp.update (Counter (s))
        for i, j in temp.iteritems ():
            if j:
                res +=  i
        return res
    elif mode == 4:
        res = ""
        temp.update (Counter (s))
        for i, j in temp.iteritems ():
            if not j:
                res +=  i
        return res
    else:
        raise ValueError ("Incorrect value of mode (%d)" % (mode,))
