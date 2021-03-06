###############################################################################
# cluster graph data structure implementation (similar as the CliqueTree
# implementation in PA2)
# author: Billy Jun, Xiaocheng Li
# date: Jan 31st, 2016
###############################################################################

from factors import *
import numpy as np
import pdb
import copy
import matplotlib.pyplot as plt

class ClusterGraph:
    def __init__(self, numVar=0):
        '''
        var - list: index/names of variables
        domain - list: the i-th element represents the domain of the i-th variable; 
                     for this programming assignments, all the domains are [0,1]
        varToCliques - list of lists: the i-th element is a list with the indices 
                     of cliques/factors that contain the i-th variable
        nbr - list of lists: it has the same length with the number of cliques/factors,
                    if factor[i] and factor[j] shares variable(s), then j is in nbr[i]
                    and i is in nbr[j]
        factor: a list of Factors
        sepset: two dimensional array, sepset[i][j] is a list of variables shared by 
                factor[i] and factor[j]
        messages: a dictionary to store the messages, keys are (src, dst) pairs, values are 
                the Factors of sepset[src][dst]. Here src and dst are the indices for factors.
        '''

        self.numVar = numVar
        self.var = [None for _ in range(numVar)]
        self.domain = [None for _ in range(numVar)]
        self.varToCliques = [[] for _ in range(numVar)]
        self.nbr = []
        self.factor = []
        self.sepset = []
        self.messagesToVar = {}
        self.messagesToFac = {}
        self.ham = []
    
    def evaluateWeight(self, assignment):
        '''
        param - assignment: the full assignment of all the variables
        return: the multiplication of all the factors' values for this assigments
        '''
        a = np.array(assignment, copy=False)
        output = 1.0
        for i,f in enumerate(self.factor):
            print output
            output *= f.val.flatten()[assignment_to_indices([a[f.scope]], f.card)]
        return output

    # THIS IS WRONG
    def emptyFac(self, var):
        inMsg = Factor()
        inMsg.scope = [var]
        inMsg.card = [2]
        inMsg.val = np.ones(np.prod(inMsg.card))/2
        return inMsg

    def getInMessage(self, src, dst):
        '''
        param - src: the source factor/clique index
        param - dst: the destination factor/clique index
        return: Factor with var set as sepset[src][dst]
        
        In this function, the message will be initialized as an all-one vector if 
        it is not computed and used before. 
        '''
        if (src, dst) not in self.messages:
            inMsg = Factor()
            inMsg.scope = self.sepset[src][dst]
            inMsg.card = [len(self.domain[s]) for s in inMsg.scope]
            inMsg.val = np.ones(np.prod(inMsg.card))/2
            self.messages[(src, dst)] = inMsg
        return self.messages[(src, dst)]


    def no_help(self, iterations):
        self.to_fact = [[[1.,1.] for i in range(len(self.factor))] for j in range(self.numVar)]
        self.to_var = [[[1.,1.] for i in range(self.numVar)] for j in range(len(self.factor))]
        ham = []
        for iter in range(iterations):

            if iter in [0,1,2,3,5,10,20,30]:
                N = 1600
                img = np.zeros(N)
                for i in range(N):
                    prob = self.estimateMarginalProbability(i)[1]
                    img[i] = 1 if prob > .5 else 0

                print iter
                print np.sum(img!=self.X)

                #plt.imshow(img.reshape([40,40]))
                #plt.show()

                plt.imsave(str(self.p) + "_" + str(iter)+".png", img.reshape([40,40]))

            print "On iteration " + str(iter)

            next_to_fact = [[None for i in range(len(self.factor))] for j in range(self.numVar)]
            next_to_var = [[None for i in range(self.numVar)] for j in range(len(self.factor))]
           
            # to var
            for dest in range(self.numVar):
                for src in self.varToFac[dest]:
                    message = np.array([1.,1.])
                    for i, incoming in enumerate(self.factor[src].scope):
                        if incoming != dest:
                            message = np.multiply.outer(message, self.to_fact[incoming][src])

                    assert message.shape == self.factor[src].val.shape

                    total = np.multiply(message, self.factor[src].val)

                    arr = [np.sum(total[0]), np.sum(total[1])]
                    
                    # if src == 332 and dest == 0 and iter == 2:
                    #     print "HEre"
                    #     pdb.set_trace()

                    arr = arr/np.sum(arr)

                    next_to_var[src][dest] = copy.copy(arr)

            # to fac
            for dest, fact in enumerate(self.factor):
                for src in fact.scope:
                    message = np.array([1.,1.])
                    for i, incoming in enumerate(self.varToFac[src]):
                        if incoming != dest:
                            message = np.multiply(message, self.to_var[incoming][src])

                    assert message.shape == (2,)

                    message = message / np.sum(message)

                    next_to_fact[src][dest] = copy.copy(message)

            self.to_fact = copy.copy(next_to_fact)
            self.to_var = copy.copy(next_to_var)

        #pdb.set_trace()

            ans = 0
            for i in range(self.numVar):
                    #print self.yhat[i]
                if self.estimateMarginalProbability(i)[1] > self.estimateMarginalProbability(i)[0]:
                    ans += 1

            ham.append(ans)

        return ham


    def runParallelLoopyBP(self, iterations): 
        '''
        param - iterations: the number of iterations you do loopy BP
          
        In this method, you need to implement the loopy BP algorithm. The only values 
        you should update in this function is self.messages. 
        
        Warning: Don't forget to normalize the message at each time. You may find the normalize
        method in Factor useful.
        '''

        for i in range(self.numVar):
            for j in range(len(self.factor)):
                self.messagesToFac[(i,j)] = self.emptyFac(i)
                self.messagesToVar[(j,i)] = self.emptyFac(i)

        for iter in range(iterations):

        ###############################################################################
        # To do: your code here

            ans = 0
            for i in range(self.numVar):
                if iter > 0:
                    break
                #print self.yhat[i]
                if self.estimateMarginalProbability(i)[1] > 0.5:
                    ans += 1

            self.ham.append(ans)

            mtv = {}
            mtf = {}
            for findex, fact in enumerate(self.factor):

                messages = None

                friends = fact.scope
                for _, nbr in enumerate(friends):

                    # nbr is dest, findex is the source

                    #if iter == 1 and findex == 300:
                        #pdb.set_trace()

                    messages = None
                    for _, nbr2 in enumerate(friends):
                        if nbr2==nbr:
                            messages = self.emptyFac(nbr) if messages == None else messages.multiply(self.emptyFac(nbr))
                        messages = self.messagesToFac[(nbr2, findex)] if messages == None else messages.multiply(self.messagesToFac[(nbr2, findex)])
                    
                    assert fact.val.shape == messages.val.shape

                    total = fact if messages == None else fact.multiply(messages)

                    mtv[(findex,nbr)] = total.normalize().marginalize_all_but([nbr], "sum").normalize()
                    #print mtv[(findex,nbr)].val
                    #print self.messagesToVar[(findex,nbr)].val

                # for _, nbr in enumerate(friends):
                #     messages = self.messagesToVar[(findex,findex)]
                #     for b, nbr2 in enumerate(friends):
                #         if b == i:
                #             continue
                #         messages = messages.multiply(self.messagesToVar[(b,findex)])
                #     self.messagesToFac[(findex,nbr)] = messages


            # UPDATE ALL THE MESSAGES INTO FACTORS
            for var in range(self.numVar): # source

                messages = None
                friends = self.nbr[var]
                for i, nbr in enumerate(friends):
                    messages = self.messagesToVar[(nbr, var)] if messages == None else messages.multiply(self.messagesToVar[(nbr, var)])
                mtf[(var,var)] = messages.normalize()

                for i, nbr in enumerate(friends):
                    messages = self.messagesToVar[(var,var)]
                    for b, nbr2 in enumerate(friends):
                        if b == i:
                            messages.multiply(self.emptyFac(nbr))
                        messages = messages.multiply(self.messagesToVar[(nbr2,var)])

                    mtf[(var,nbr)] = messages.normalize()

            self.messagesToVar = mtv
            self.messagesToFac = mtf

        return self.ham

            # for s, src_fact in enumerate(self.factor):
            #     for d, dest_fact in enumerate(self.factor):
            #         messages = None
            #         for i, nbr in enumerate(self.nbr[src_fact]):
            #             if i != d:
            #                 messages = nbr if messages == None else messages.multiply(nbr)

            #         marginalize_all_but

            #         self.messages[(src_fact, dest_fact)] = 
           
        ###############################################################################
        

    def estimateMarginalProbability(self, var):
        '''
        param - var: a single variable index
        return: the marginal probability of the var
        
        example: 
        >>> cluster_graph.estimateMarginalProbability(0)
        >>> [0.2, 0.8]
    
        Since in this assignment, we only care about the marginal 
        probability of a single variable, you only need to implement the marginal 
        query of a single variable.     
        '''
        ###############################################################################
        # To do: your code here 

        one = 1.0
        zero = 1.0

        for i,f in enumerate(self.factor):
            if var not in f.scope:
                continue

            one *= self.to_var[i][var][1]
            zero *= self.to_var[i][var][0]
        return (np.array([zero, one]) / (one+zero))

        # everything = None
        # for friends in self.varToFac[var]:
        #     message = self.messagesToVar[(friends,var)]
        #     everything = message if everything == None else everything.multiply(message)

        # return [message.val[0], message.val[1]]
        
        
        ###############################################################################
    

    def getMarginalMAP(self):
        '''
        In this method, the return value output should be the marginal MAP 
        assignments for the variables. You may utilize the method
        estimateMarginalProbability.
        
        example: (N=2, 2*N=4)
        >>> cluster_graph.getMarginalMAP()
        >>> [0, 1, 0, 0]
        '''
        
        output = np.zeros(len(self.var))
        ###############################################################################
        # To do: your code here  

        
        
        ###############################################################################  
        return output
