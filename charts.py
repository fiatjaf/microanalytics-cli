# -*- encoding: utf-8 -*-

tick = u'▇'

# get terminal width
import os
try:
    _, width = os.popen('stty size', 'r').read().split()
    width = int(width) - 5
except:
    width = 50

def bar(data):
    global width
    global tick

    labels = []
    values = []

    for label, value in data:
        labels.append(label)
        values.append(int(value))

    # massage data
    labels_width = max(map(len, labels))
    width = width - labels_width - 1 - 4
    step = max(values) / float(width)
    blocks = [int(d / step) for d in values]

    # output command line chart
    output = ''
    for i, label in enumerate(labels):
        lbl = u'%s ' % (label.rjust(labels_width, ' '))
        output += u'%s ' % lbl
        if blocks[i] < step:
            pass
        else:
            output += tick * blocks[i]
        output += u'  %d' % values[i]
        output += u'\n'

    return output
