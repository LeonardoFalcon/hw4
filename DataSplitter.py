def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

testDataAcceX = [0] * 100 #this will be the testData within the start and end event.

dataInChunks = list(chunks(testData, 7))) #this will be the data chunks
