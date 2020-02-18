class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        """
        nums1 = [1, 3]
        nums2 = [2]
        The median is 2.0
        
        nums1 = [1, 2]
        nums2 = [3, 4]
        The median is (2 + 3)/2 = 2.5
        
        The next idea is too create the combined sorted array up to length (n+m)/2
        Then we know the median. This takes runtime O((n+m)/2)
        
        Runtime: 148 ms, faster than 33.17% of Python3 online submissions for Median of Two Sorted Arrays.
        """
        n = len(nums1)
        m = len(nums2)
        
        res = []
        i = 0
        k = 0
        
        while (k+i) <= (n+m)//2:
            a = nums1[i] if i < n else None
            b = nums2[k] if k < m else None
            
            if a is not None and b is not None:
                if a > b:
                    res.append(b)
                    k = k+1
                else:
                    res.append(a)
                    i = i+1
            elif a is not None:
                res.append(a)
                i = i+1
            elif b is not None:
                res.append(b)
                k = k+1
                
        if (n+m)%2 == 0:
            return (res[-1]+res[-2])/2
        else:
            return res[-1]
              
a = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]
b = [0,6]
s = Solution()
print(s.findMedianSortedArrays(a, b))
