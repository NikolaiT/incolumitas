class Solution:
    def maxArea(self, height):
        """
        :type height: List[int]
        :rtype: int
        
        Input: [1,8,6,2,5,4,8,3,7]
        Output: 49
        
        Sorted: [1, 2, 3, 4, 5, 6, 7, 8, 8]
        
        f(a_i, a_j) = min(a_i, a_j) * (j-i)
        j>i, j,i in [0,n], looking for max f(a_i, a_j)
        how many pairs (i,j) are possible such that j>i ?
        
        [1,8,6,2,5,4,8,3,7] => [0 .. 8], (0,1), (0,2), (0,n), (1,2), (1,3), ..., (1,n)
        => n + n-1 + n-2 ... n-n ~ O(n*n/2) ~ O(n^2) => too much
        
        Whats the highest possible area? 
        max(a_i) * (n-1)
        
        Therefore the elements should be high and the indices of those elements should be maximally 
        far apart.
        
        Heuristics wont work all the time. Special case: 
        [1,2,3,4,5,6,7,8,9,10,11,12,13]
        
        When we sort there are the difference of element and index, we
        receive values that are all equal.
        
        What if we approach the problem like merge sort?
        Split in half until we have 1 (e,i) left and update the max container
        by the merge operation and keep track of max seen so far???
        [1,8,6,2,5,4,8,3,7]
        [1,8,6,2] [5,4,8,3,7]
        [1,8] [6,2] [5,4,] [8,3,7]
         1 8  6 2    5 3   [8,3] 7
                            8 3
        """
        n = len(height)-1
        lut = dict()
        for i,e in enumerate(height):
            m = max(e-i, e-(n-i))
            if m in lut:
                lut[m].append(i)
            else:
                lut[m] = [i,]
            
        print(lut)

a = range(100)
b = [1,8,6,2,5,4,8,3,7]
s = Solution()
print(s.maxArea(b))
