class Solution:
    def maxArea(self, height):
        """
        :type height: List[int]
        :rtype: int
        
        Idea: lower a horizontal line with width n down
        the array. In each iteration keep track of the 
        lowest and highest indices of elements that reach
        to the line or beyond. Muliply the difference of
        this extrema indices with the current level
        of the horizontal line.
        
        Runtime: 76 ms, faster than 50.66% of Python3 online submissions for Container With Most Water.
        Runtime: O(n * log(n))
        """
        n = len(height)-1
        d = dict()
        i = 0
        for e in height:
            if e not in d:
                d[e] = [i,]
            else:
                d[e].append(i)
            i += 1
                
        # we sort here n indices
        # O(n * log(n))
        for key in d:
            d[key].sort()

        sorted_keys = sorted(d.keys(), reverse=True)
        m = 0
        highest = 0
        lowest = n
        for k in sorted_keys:
            highest = max(d[k][-1], highest)
            lowest = min(d[k][0], lowest)
            test = k * (highest-lowest)
            if test >= m:
                m = test
            if m > (k * n):
                return m
                
        return m
              
        
a = [1,8,6,2,5,4,8,3,7]
b = range(10000)
s = Solution()
print(s.maxArea(b))
                
