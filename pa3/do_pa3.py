###############################################################################
# Finishes PA 3
# author: Billy Jun, Xiaocheng Li
# date: Jan 31, 2016
###############################################################################

## Utility code for PA3
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from cluster_graph import *
from factors import *
import pdb


def loadLDPC(name):
    """
    :param - name: the name of the file containing LDPC matrices
  
    return values:
    G: generator matrix
    H: parity check matrix
    """
    A = sio.loadmat(name)
    G = A['G']
    H = A['H']
    return G, H

def loadImage(fname, iname):
    '''
    :param - fname: the file name containing the image
    :param - iname: the name of the image
    (We will provide the code using this function, so you don't need to worry too much about it)  
  
    return: image data in matrix form
    '''
    img = sio.loadmat(fname)
    return img[iname]


def applyChannelNoise(y, p):
    '''
    :param y - codeword with 2N entries
    :param p channel noise probability
  
    return corrupt message yhat  
    yhat_i is obtained by flipping y_i with probability p 
    '''
    ###############################################################################
    # TODO: Your code here! 

    
    
    ###############################################################################
    return yhat


def encodeMessage(x, G):
    '''
    :param - x orginal message
    :param[in] G generator matrix
    :return codeword y=Gx mod 2
    '''
    return np.mod(np.dot(G, x), 2)


def constructClusterGraph(yhat, H, p):
    '''
    :param - yhat: observed codeword
    :param - H parity check matrix
    :param - p channel noise probability

    return G clusterGraph
   
    You should consider two kinds of factors:
    - M unary factors 
    - N each parity check factors
    '''
    N = H.shape[0]
    M = H.shape[1]
    G = ClusterGraph(M)
    domain = [0, 1]

    G.yhat = yhat


    # Unary factors first
    G.nbr = [[] if index < M else np.where(H[index-M]==1)[0] for index in range(M+N)]
    G.varToFac = [[i] for i in range(M)]

    for i in range(N):
        for var in np.where(H[i]==1)[0]:
            G.varToFac[var].append(i)

    for i in range(M):
        for j in range(N):
            if H[j][i] == 1:
                G.nbr[i].append(j+M) # because the parity check factors are above

    #insides = [[index] if index < M else np.where(H[index-M]==1)[0] for index in range(M+N)]
    G.sepset = [[[] for b in range(M+N)] for a in range(M+N)]
    G.factor = []
    G.M = M
    G.N = N

    for i in range(M):

        if yhat[i] == 1:
            vals = [p, 1.-p]
        if yhat[i] == 0:
            vals = [1.-p, p]
        G.factor.append(Factor(None, [i], [2], np.array(vals)))
    for i in range(N):
        scope = np.where(H[i]==1)[0]

        val = np.zeros([2]*scope.size)
        for index, value in np.ndenumerate(val):
            s = 0
            for i in index:
                s += i
            if s%2 == 1:
                val[index] = 1.

        G.factor.append(Factor(None, scope, [2]*scope.size, (val)).normalize())

    ##############################################################
    # To do: your code starts here



    for a in range(M+N):
        for b in range(M+N):
            if a < M and b < M: # unary variables have no friedns
                continue
            else: #possible neighbors
                for _, nei in enumerate(G.nbr[a]):
                    for _, nei2 in enumerate(G.nbr[b]):
                        if nei == nei2:
                            G.sepset[a][b].append(nei)
                            # super bad way to check for shared messages
                            break

    ##############################################################
    return G

def do_part_a():
    yhat = np.array([[1, 1, 1, 1, 1]]).reshape(5,1)
    H = np.array([ \
        [0, 1, 1, 0, 1], \
        [0, 1, 0, 1, 1], \
        [1, 1, 0, 1, 0], \
        [1, 0, 1, 1, 0], \
        [1, 0, 1, 0, 1]])
    p = 0.95
    G = constructClusterGraph(yhat, H, p)
    ##############################################################
    # To do: your code starts here 
    # Design two invalid codewords ytest1, ytest2 and one valid codewords ytest3.
    # Report their weights respectively.
    ytest1 = [1, 1, 1, 1, 1]
    ytest2 = [1, 0, 1, 0, 1]
    ytest3 = [0, 0, 0, 0, 0]
    ##############################################################
    print(
        G.evaluateWeight(ytest1), \
        G.evaluateWeight(ytest2), \
        G.evaluateWeight(ytest3))

def do_part_c():
    '''
    In part b, we provide you an all-zero initialization of message x, you should
    apply noise on y to get yhat, znd then do loopy BP to obatin the
    marginal probabilities of the unobserved y_i's.
    '''
    G, H = loadLDPC('ldpc36-128.mat')
    p = 0.05
    N = G.shape[1]
    
    ##############################################################
    # To do: your code starts here
    x = np.zeros((N, 1), dtype='int32')
    ran = np.random.rand(N)
    x[ran<p] = 1
    x[0] = 1

    y = encodeMessage(x, G)


    graph = constructClusterGraph(y, H, p)

    graph.runParallelLoopyBP(5)

    prob = np.zeros(N)
    X = np.arange(N)

    for i in range(N):
        prob[i] = graph.estimateMarginalProbability(i)[1]


    plt.plot(X, prob)
    plt.show()

    ##############################################################

def do_part_de(numTrials, p, iterations=50):
    '''
    param - numTrials: how many trials we repreat the experiments
    param - error: the transmission error probability
    param - iterations: number of Loopy BP iterations we run for each trial
    '''

    loops = 10
    G, H = loadLDPC('ldpc36-128.mat')
    N = G.shape[1]

    ##############################################################
    # To do: your code starts here

    x = np.zeros((N, 1), dtype='int32')
    ran = np.random.rand(N)
    x[ran<p] = 1

    y = encodeMessage(x, G)

    graph = constructClusterGraph(y, H, p)

    X = np.arange(loops)
    ham = np.array(graph.runParallelLoopyBP(loops))

    print ham

    plt.plot(X, ham)
    plt.show()

    ##############################################################

def do_part_fg(error):
    '''
    param - error: the transmission error probability
    '''
    G, H = loadLDPC('ldpc36-1600.mat')
    img = loadImage('images.mat', 'cs242')
    ##############################################################
    # To do: your code starts here
    # You should flattern img first and treat it as the message x in the previous parts.


    ################################################################

np.random.seed(10)

#print('Doing part (a): Should see 0.0, 0.0, >0.0')
#do_part_a()

#print('Doing part (c)')
#do_part_c()
print('Doing part (d)')
do_part_de(10, 0.06)
print('Doing part (e)')
#do_part_de(10, 0.08)
#do_part_de(10, 0.10)
print('Doing part (f)')
#do_part_fg(0.06)
print('Doing part (g)')
#do_part_fg(0.10)

