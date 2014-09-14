# -*- encoding: utf-8 -*-

def bar(data):
    tick = u'▇'
    width = 50

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
