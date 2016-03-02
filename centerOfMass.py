import sys
import math
from Scientific.IO import PDB
try:
    import numpy as N
except:
    import Numeric as N

def pymol_centerofmass(filename, start, stop):
    import pymol
    from pymol import cgo
    from pymol import cmd

    cm = centerofmass(filename, start, stop)

    center = [cgo.SPHERE, cm[0], cm[1], cm[2], 0.5]
    com = [cgo.COLOR, 1.0, 1.0, 1.0, cgo.SPHERE]+list(cm) + [3.0] ## white sphere with 3A radius
    cmd.load(filename)
    cmd.load_cgo(com, "CoM")
    
    #cmd.load_cgo(center, 'center')

def centerofmass(filename, startA, startB, cut, stop):

    Ndomain_rangeA = [startA, cut] # HTH domain (N-terminal)
    Ndomain_rangeB = [startB, cut] # HTH domain (N-terminal)
    Cdomain_range = [cut+1, stop] # LBD domain (C-terminal) 

    pdb = PDB.PDBFile(filename)

    a = (None,)
    fields = []
    while a[0] != 'END':
        a = pdb.readLine()
        fields.append(a)

    # point A
    domainAN = [line for line in fields if (line[0] == 'ATOM' 
                 or line[0] == 'HETATM') 
                 and (line[1]['residue_number'] > Ndomain_rangeA[0] 
                 and line[1]['residue_number'] < Ndomain_rangeA[1]
                 and line[1]['chain_id'] == 'A')]

    # point B
    domainAC = [line for line in fields if (line[0] == 'ATOM' 
                 or line[0] == 'HETATM') 
                 and (line[1]['residue_number'] > Cdomain_range[0] 
                 and line[1]['residue_number'] < Cdomain_range[1]
                 and line[1]['chain_id'] == 'A')]

    # point C
    domainBN = [line for line in fields if (line[0] == 'ATOM' 
                 or line[0] == 'HETATM') 
                 and (line[1]['residue_number'] > Ndomain_rangeB[0] 
                 and line[1]['residue_number'] < Ndomain_rangeB[1]
                 and line[1]['chain_id'] == 'B')]

    # point D
    domainBC = [line for line in fields if (line[0] == 'ATOM' 
                 or line[0] == 'HETATM') 
                 and (line[1]['residue_number'] > Cdomain_range[0] 
                 and line[1]['residue_number'] < Cdomain_range[1]
                 and line[1]['chain_id'] == 'B')]

    casAN = [line[1]['position'].array for line in domainAN \
                      if (line[1]['name'].strip() == "CA" 
                       and line[1]['alternate'] in ["","A"])]

    casAC = [line[1]['position'].array for line in domainAC \
                      if (line[1]['name'].strip() == "CA" 
                       and line[1]['alternate'] in ["","A"])]

    casBN = [line[1]['position'].array for line in domainBN \
                      if (line[1]['name'].strip() == "CA" 
                       and line[1]['alternate'] in ["","A"])]

    casBC = [line[1]['position'].array for line in domainBC \
                      if (line[1]['name'].strip() == "CA" 
                       and line[1]['alternate'] in ["","A"])]

    cmAN = sum(casAN)/len(casAN)
    cmAC = sum(casAC)/len(casAC)
    cmBN = sum(casBN)/len(casBN)
    cmBC = sum(casBC)/len(casBC)

    return (cmAN, cmAC, cmBN, cmBC)

#############################################################################
# Multiply a number (float) by a 3D vector
#############################################################################
def numbertimesvector(a, P):
    return [a*P[0], a*P[1], a*P[2]]

#############################################################################
# Add two 3D vectors
#############################################################################
def vectorplusvector(A, B):
    return [A[0]+B[0], A[1]+B[1], A[2]+B[2]]

#############################################################################
# Calculate the point exactly in the middle between 2 points in 3D space
#############################################################################
def getmidpoint(A, B):
    return vectorplusvector(numbertimesvector(0.5, A), numbertimesvector(0.5, B))

#############################################################################
# Calculate dot product of two vectors
#############################################################################
def dotproduct(V, U):
    return V[0]*U[0] + V[1]*U[1] + V[2]*U[2]

#############################################################################
# Calculate the norm of a vector
#############################################################################
def norm(V):
    return math.sqrt(dotproduct(V, V))

#############################################################################
# Calculate vector connecting two points in space
# The vector is B-A
#############################################################################
def getrelvect(A, B):
    return vectorplusvector(B, numbertimesvector(-1.0, A))

#############################################################################
# Calculate distance between two points
#############################################################################
def distance(A, B):
    return norm(getrelvect(A, B))

#############################################################################
# Calculate the angle (in degrees) between two 3D vectors
# Using the fact that cosine of an angle between two vectors is
# the ratio of their dot product to the product of their norms
# The angle is always within 0..180 degrees
#############################################################################
def getangle(V, U):
    return math.acos(dotproduct(V, U)/(norm(V)*norm(U)))*180.0/math.pi

#############################################################################
# Calculate the angle (in degrees) between three points
# The angle is measured at the middle point
#############################################################################
def getangleat(A, B, C):
    return getangle(getrelvect(B, A), getrelvect(B, C))

#############################################################################
# Calculate the value of a determinant for a 3x3 matrix
#############################################################################
def det(row0, row1, row2):
    return row0[0]*row1[1]*row2[2] \
          +row0[1]*row1[2]*row2[0] \
          +row0[2]*row1[0]*row2[1] \
          -row0[2]*row1[1]*row2[0] \
          -row0[0]*row1[2]*row2[1] \
          -row0[1]*row1[0]*row2[2]

#############################################################################
# Calculate the coefficients of a plane
# Planes have equation Ax + By + Cz + D = 0
# This function calculates list [A, B, C, D] using the forumalae based on
# determinants
#############################################################################
def getplane(P1, P2, P3):
    A = det([1.0, P1[1], P1[2]],
            [1.0, P2[1], P2[2]],
            [1.0, P3[1], P3[2]])
    B = det([P1[0], 1.0, P1[2]],
            [P2[0], 1.0, P2[2]],
            [P3[0], 1.0, P3[2]])
    C = det([P1[0], P1[1], 1.0],
            [P2[0], P2[1], 1.0],
            [P3[0], P3[1], 1.0])
    D = -det([P1[0], P1[1], P1[2]],
             [P2[0], P2[1], P2[2]],
             [P3[0], P3[1], P3[2]])
    # Normalize the coefficients so that A^2 + B^2 + C^2 = 1
    n = norm([A, B, C])
    A = A/n
    B = B/n
    C = C/n
    D = D/n
    return [A, B, C, D]

#############################################################################
# Calculate the distance from a point to a plane
# Plane is specified as Ax + By + Cz + D = 0 and argument p is [A, B, C, D]
# Point is A=[x, y, z]
# Works for normalized planes only
#############################################################################
def planedist(A, p):
    return abs(p[0]*A[0] + p[1]*A[1] + p[2]*A[2] + p[3])

#############################################################################
# Produce report for 4 CoM (Center of Mass) points
# Each point represents CoM of one domain of a tetR
#############################################################################
def report(A, B, C, D):
    print "BEGIN REPORT"
    print "A is " + str(A)
    print "B is " + str(B)
    print "C is " + str(C)
    print "D is " + str(D)
    P = getmidpoint(A, C)
    Q = getmidpoint(B, D)
    print "P is " + str(P)
    print "Q is " + str(Q)
    print "dAB = " + str(distance(A, B))
    print "dBC = " + str(distance(B, C))
    print "dCD = " + str(distance(C, D))
    print "dDA = " + str(distance(D, A))
    print "dAC = " + str(distance(A, C))
    print "dBD = " + str(distance(B, D))
    print "dPQ = " + str(distance(P, Q))
    print "rACPQ = " + str(distance(A, C)/distance(P, Q))
    print "aA = " + str(getangleat(B, A, C))
    print "aB = " + str(getangleat(A, C, D))
    print "aC = " + str(getangleat(C, D, B))
    print "aD = " + str(getangleat(D, B, A))
    # Separation (distance) between points and planes generating by the remaining points
    # For example, the first is the distance between point A and plane spanned by points B, C and D
    print "sA = " + str(planedist(A, getplane(B, C, D)))
    print "sB = " + str(planedist(B, getplane(A, C, D)))
    print "sC = " + str(planedist(C, getplane(A, B, D)))
    print "sD = " + str(planedist(D, getplane(A, B, C)))
    print "END REPORT"

#############################################################################
# Main script
#############################################################################

if __name__ == '__main__':
    filename = sys.argv[1]
    startA = int(sys.argv[2])
    startB = int(sys.argv[3])
    cut = int(sys.argv[4])
    stop = int(sys.argv[5])
    
    COMs = centerofmass(filename, startA, startB, cut, stop)
    #pymol_centerofmass(filename, start, stop)
    report(COMs[0], COMs[1], COMs[2], COMs[3])

