
import sys

mass = int(sys.argv[1])

batches = {}

if mass<1001:
    batches[1] = [60, 70, 75, 80]
    batches[2] = [85, 90, 95, 100]
    batches[3] = [110, 120, 130, 150]
    batches[4] = [170, 190, 250, 300]
    batches[5] = [350, 400, 450, 500]
    batches[6] = [550, 600, 650, 700]
    batches[7] = [750, 800, 850]
else:
    batches[1] = [60, 70, 80, 90, 100]
    batches[2] = [120, 150, 170, 190, 250, 300]
    batches[3] = [350, 400, 450, 500, 550, 600, 650, 700]
    batches[4] = [800, 900, 1000, 1100, 1200]
    batches[5] = [1300, 1400, 1600, 1800]
    batches[6] = [2000, 2200, 2400, 2600, 2800]

    print "1 2 3 4 5 6"
    exit(0)
nMax = len(batches.keys())
output = ""
for i in range(1,nMax+1):
    if ((batches[i][0]+125) < mass):
        output+= str(i)+" "
print output
