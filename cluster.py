import sys
try:
    import Image
except ImportError:
    from PIL import Image 
from collections import namedtuple
from math import sqrt
import random

RUNTIMES = 5
DIV = 5.0
# define point and cluster type by namedtuple
TRUE    = 1
Color   = namedtuple('Color', 'v1 v2 v3')
Rgb     = namedtuple('Rgb', 'r g b')
Xyz     = namedtuple('Xyz', 'x y z')
Lab     = namedtuple('Lab', 'l a b')
Point   = namedtuple('Point', 'color count')
Cluster = namedtuple('Cluster', 'plist ctr')  
    
def getDomColor( imgpath, numClust, min_moved, modtype ):
    image = Image.open( imgpath )
    image.thumbnail((200, 200))
    w, h  = image.size
    plist = getHist( image )
    
    # run k-means 5 times 
    # ctrs = [ [0,0,0] for i in xrange(numClust)]
    #for i in xrange(RUNTIMES):
    #    tryclusters = kmeans( plist, numClust, min_moved, modtype )
    #    tryclusters = sorted( tryclusters, key=mySortFn )
    #    for j in xrange(numClust):
    #        ctrs[j][0] += tryclusters[j].ctr.color[0]
    #        ctrs[j][1] += tryclusters[j].ctr.color[1] 
    #        ctrs[j][2] += tryclusters[j].ctr.color[2] 
            
    #for j in xrange(numClust):
    #    ctrs[j][0] = ctrs[j][0] / DIV
    #    ctrs[j][1] = ctrs[j][1] / DIV
    #    ctrs[j][2] = ctrs[j][2] / DIV
    
    clusters = kmeans( plist, numClust, min_moved, modtype )
    clusters = sorted( clusters, key=mySortFn )    
    colors = []
    for j in xrange( numClust ):
        color = tuple( map( int, clusters[j].ctr.color ) )
        print "Color: ", j, color
        colors.append( color )
    print 
    return colors
    
def getHist( img ):
    w, h = img.size
    return [ Point( Color( color[0], color[1], color[2] ), count ) for count, color in img.getcolors(w * h) ]
   
def distance( p1, p2, type ):
    col1 = p1.color
    col2 = p2.color
    if type != 2:
        return sqrt( ( col1[0] - col2[0] ) ** 2 + ( col1[1] - col2[1] ) ** 2 + ( col1[2] - col2[2] ) ** 2 )
    else :
        lab1 = colorTolab( col1 )
        lab2 = colorTolab( col2 )
        return deltae94( lab1, lab2 )
   
def getCenter( pdisk ):
    total_p = 0
    ctr = [ 0.0 for i in xrange(3) ]
    for point in pdisk:
        total_p += point.count
        for i in xrange(3):
            ctr[i] += point.color[i] * point.count;
    if total_p != 0:
        for i in xrange(3):
            ctr[i] = ctr[i] / total_p
        return Point( Color( ctr[0], ctr[1], ctr[2] ), 1 )
    
def kmeans( plist, k, min_moved, modtype ):
    # take random k points for k clusters
    if k == 1:
        ctr = getCenter( plist )
        return [ Cluster(plist, ctr) ]
    clusters = [Cluster([p], p) for p in random.sample( plist, k )]
    while TRUE:
        # create k disks and attract other points to each disk
        pdisks =[ [] for i in xrange(k) ]
        for point in plist:
            min_dist = float('Inf')
            for i in xrange(k):
                dist = distance( point, clusters[i].ctr, modtype )
                if dist < min_dist:
                    min_dist = dist
                    index = i
            pdisks[index].append( point )
        
        # recalcuate and update center of each cluster
        # if center of each cluster disk not move too much then stop clustering
        ctr_moved = 0
        for i in xrange(k):
            cur = clusters[i]
            new_ctr = getCenter( pdisks[i] )
            new_cluster = Cluster( pdisks[i], new_ctr )
            clusters[i] = new_cluster
            ctr_moved = max( ctr_moved, distance( cur.ctr, new_ctr, modtype ) )
        if ctr_moved < min_moved:
            break      
    return clusters

def mySortFn( s ):
    total_p = 0
    for point in s.plist:
        total_p += point.count
    return total_p*(-1)

def rgbToxyz( rgb ):
    val = [ (rgb[i] / 255.0) for i in xrange(3) ]
    
    for i in xrange(3):
        if val[i] > 0.04045 :
            val[i] = ( ( val[i] + 0.055 ) / 1.055 ) ** 2.4
        else:
            val[i] = val[i] / 12.92
        val[i] = val[i] * 100.0
    
    #Observer = 2deg, Illuminant = D65
    X = val[0] * 0.4124 + val[1] * 0.3576 + val[2] * 0.1805
    Y = val[0] * 0.2126 + val[1] * 0.7152 + val[2] * 0.0722
    Z = val[0] * 0.0193 + val[1] * 0.1192 + val[2] * 0.9505
    
    return Xyz( X, Y, Z)

def xyzTolab( xyz ):
    ref = [ 95.047, 100.000, 108.883 ] # Observer = 2deg, Illuminant = D65
    val = [ (xyz[i] / ref[i] ) for i in xrange(3) ]
    for i in xrange(3):
        if val[i] > 0.008856 :
            val[i] = val[i] ** (1.0/3.0)
        else:
            val[i] = 7.787 * val[i] + 16.0/116.0
            
    CIEL = 116.0 * val[1] - 16.0
    CIEa = 500.0 * ( val[0] - val[1] )
    CIEb = 200.0 * ( val[1] - val[2] )
    return Lab( CIEL, CIEa, CIEb )

def labToxyz( lab ):
    ref = [ 95.047, 100.000, 108.883 ] # Observer = 2deg, Illuminant = D65
    val = [ 0.0 for i in xrange(3) ]
    val[1] = (lab.l + 16.0) / 116.0
    val[0] = lab.a / 500.0 + val[1]
    val[2] = val[1] - lab.b / 200.0
    
    for i in xrange(3):
        if val[i]**3 > 0.008856:
            val[i] = val[i]**3
        else:
            val[i] = ( val[i] - 16.0/116.0 ) / 7.787
    
    result = [ (ref[i] * val[i]) for i in xrange(3) ]
    return Xyz( result[0], result[1], result[2] )

def xyzTorgb( xyz ):
    val = [ 0.0 for i in xrange(3) ]
    valX = xyz[0] / 100.0
    valY = xyz[1] / 100.0
    valZ = xyz[2] / 100.0
    
    val[0] = valX *  3.2406 + valY * -1.5372 + valZ * -0.4986
    val[1] = valX * -0.9689 + valY *  1.8758 + valZ *  0.0415
    val[2] = valX *  0.0557 + valY * -0.2040 + valZ *  1.0570
    
    for i in xrange(3):
        if val[i] > 0.0031308 :
            val[i] = 1.055 * ( val[i] ** ( 1.0 / 2.4 ) ) - 0.055
        else:
            val[i] = 12.92 * val[i]
        val[i] = val[i] * 255.0
        
    return Rgb( val[0], val[1], val[2] )

def colorTolab( color ):
    rgb = Rgb( color[0], color[1], color[2] )
    xyz = rgbToxyz( rgb )
    return xyzTolab( xyz )
        
def deltae94( lab1, lab2 ):
    c1 = sqrt( lab1.a ** 2 + lab1.b ** 2 )
    c2 = sqrt( lab2.a ** 2 + lab2.b ** 2 )
    dc = c1 - c2
    dl = lab1.l - lab2.l
    da = lab1.a - lab2.a
    db = lab1.b - lab2.b
    ds = da**2 + db**2 - dc**2
    if ds < 0:
        ds = -ds
    dh = sqrt( ds )
    first  = dl
    second = dc / (1.0 + 0.045 * c1 )
    third  = dh / (1.0 + 0.015 * c1 )
    delresult = sqrt( first**2 + second**2 + third**2 )
    return delresult