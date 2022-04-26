import time, math, colour
import multiprocessing as mp

def draw_set(dimensionX, dimensionY, max_iter, zoom, offsetX, offsetY, fileName):
    numBytes = ((3*dimensionX)+(dimensionX%4))*dimensionY
    print("\nImage of {}x{} to be created at an iteration depth of {}.".format(dimensionX, dimensionY, max_iter))
    input("File size of {} will be ~{} Mb. Enter to continue:\n".format(fileName, numBytes/1e6))
    
    startTime = time.time()
    
    numThreads = mp.cpu_count()
    chunkSize = 5
    P = mp.Pool(numThreads)

    padding = dimensionX%4

    interval = (2*zoom)/min(dimensionX, dimensionY)
    startPos = ((-interval*dimensionX/2)+offsetX, (-interval*dimensionY/2)+offsetY)

    with open(fileName, 'wb') as f:
        create_header(dimensionX, dimensionY, numBytes, f)

        updateInterval = 2
        start = time.time()
        for y in range(dimensionY):
            for x in range(0, dimensionX, numThreads*chunkSize):

                valuesToCalc = min(numThreads*chunkSize, dimensionX-x)
                valList = get_val_list(x, y, valuesToCalc, interval, max_iter, startPos)
                itr_values = P.map(calculate_point, valList, chunkSize)

                for itr in itr_values:
                    if itr == max_iter:
                        f.write(bytes.fromhex('000000'))
                    else:
                        cData = colour.Color(hue = itr/max_iter, saturation = 0.6, luminance = 0.5)
                        f.write(int(colour.rgb2hex(cData.rgb, force_long=True)[1:], 16).to_bytes(3,'little'))

                    if time.time()-start >= updateInterval:
                        #start = display_info_pANDt(start, x, y, dimensionX, dimensionY)
                        start = display_info_pONLY(x, y, dimensionX, dimensionY)
                    
            f.write(bytes.fromhex('00')*padding)

    P.terminate()
    stopTime = time.time()
    
    timeElapsed = stopTime-startTime
    timeElapsed = (timeElapsed//60, timeElapsed%60)
    print("\nDone in {:.0f}m {:.3f}s.".format(timeElapsed[0], timeElapsed[1]))

def create_header(dx, dy, b, file):
    header = '424D46000000000000003600000028000000'
    file.write(bytes.fromhex(header))
    file.write(dx.to_bytes(4, 'little'))
    file.write(dy.to_bytes(4, 'little'))
    file.write(bytes.fromhex('0100180000000000'))
    file.write(b.to_bytes(4, 'little'))
    file.write(bytes.fromhex('130B0000')*2)
    file.write(bytes.fromhex('00')*8)

def calculate_point(data):
    x,y,m = data[0], data[1], data[2]
    iterations = 0
    ca, cb = x, y
    x2, y2 = x**2, y**2
    while (iterations < m and abs(x2+y2) < 50):
        z1 = x2-y2
        z2 = 2*x*y
        x = z1+ca
        y = z2+cb
        x2 = x**2
        y2 = y**2
        iterations+=1

    if iterations == m:
        return m
    else:
        return iterations + 1 - math.log(math.log2(abs(math.sqrt(x2+y2)))) / math.log(50)

def get_val_list(xp,yp,ni,it,mx,st):
    vL= []
    for num in range(ni):
        a = ((xp+num)*it)+st[0]
        b = (yp*it)+st[1]
        vL.append((a,b,mx))
    return vL

def display_info_pONLY(xp,yp,dx,dy):
    percent = ((yp*dx+xp)/(dy*dx))*100
    print("\r{0:.2f}% Complete.".format(percent), end = "")
    return time.time()

def display_info_pANDt(s,xp,yp,dx,dy):
    percent = ((yp*dx+xp)/(dy*dx))*100
    timeEstimate = ((time.time() - s)/max(yp,1)) * (dy-yp)
    print("{0:.2f}% Complete, Remaining: {1:.0f}m {2:.0f}s".format(percent, timeEstimate//60, timeEstimate%60))
    return time.time()
    

if __name__ == '__main__':
    print("-----MANDELBROT SET IMAGE GENERATOR-----")
    
    with open("PREFS.txt") as prefs:
        contents = prefs.readlines()
    
    resolution = list(map(int, contents[0][13:].strip().split(",")))
    maxiterations = int(contents[1][16:].strip())
    magnification = float(contents[2][6:].strip())
    offset = (float(contents[3][9:].strip()), float(contents[4][9:].strip()))
    output = contents[5][8:].strip()
    
    draw_set(resolution[0], resolution[1], maxiterations, magnification, offset[0], offset[1], output)
