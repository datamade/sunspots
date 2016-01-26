import googleanalytics as ga
import collections
import numpy
import datetime

SMOOTHER = 20
WINDOW = 8
GROWTH_THRESHOLD = 0.03

def trend(counts) :
    X, Y = zip(*counts)

    X = numpy.array([x.toordinal() for x in X])
    X -= datetime.date.today().toordinal()
    A = numpy.array([numpy.ones(len(X)), X])

    Y = numpy.log(numpy.array(Y))

    w = numpy.linalg.lstsq(A.T,Y)[0]

    return w

profile = ga.authenticate(identity='sunspot', 
                          account='Illinois Campaign for Political Reform',
                          webproperty='Illinois Sunshine', 
                          profile='Illinois Sunshine')

totals = profile.core.query.metrics('pageviews').\
                            daily(days=-WINDOW)

totals = {date : count for date, count in totals.rows}

pages = profile.core.query.metrics('pageviews').\
                           dimensions('pagepath').\
                           daily(days=-WINDOW)

page_counts = collections.defaultdict(dict) 
normalized_page_counts = collections.defaultdict(dict) 

for date, page, count in pages.rows :
    page_counts[page][date] = count
    normalized_page_counts[page][date] = (count + SMOOTHER)/totals[date]

for counts in normalized_page_counts.values() :
    for date in totals.keys() - counts.keys() :
        counts[date] = SMOOTHER/totals[date]

for page, counts in normalized_page_counts.items() :
    b0, b1 = trend(counts.items())
    if b1 > GROWTH_THRESHOLD and page.startswith('/committees/')  :
        print(page, b0, b1)
        for count in sorted(page_counts[page].items()) :
            print(count)



