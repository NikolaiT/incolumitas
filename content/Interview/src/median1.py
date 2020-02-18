class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        """
        :type nums1: List[int]
        :type nums2: List[int]
        :rtype: float
        
        Median of [1,3] and [2] is 2.0
        Median of [1,2] and [3,4] is (2+3)/2 = 2.5
        
        Idea: look for the area that is overlapping in 
        both arrays
        
        [1,2,3,4,5]
            [1,4,6,8,12,21]
            
        Rough Idea: Locate median of each array with binary search
        
        The median of a sorted array of length N is
            a_0 ... a_N
            Case: N is even: ( a_((N/2)-1) + a_(N/2) ) / 2
            Case: N is odd: a_(N//2)
        
        Observation: Get median of both sorted arrays and then return
        (median_a + median_b)/2
        Is this possible?
        No, this is not mathematically correct.
        """
        def get_median(l):
            if not l:
                return
            n = len(l)
            if n % 2 == 0:
                return ( l[(n//2)-1] + l[n//2] ) / 2
            else:
                return l[n//2]
            
        ma = get_median(nums1)
        mb = get_median(nums2)
        
        if ma and mb:
            return (ma+mb)/2
        
        if ma:
            return ma
        
        if mb:
            return mb
        
        
        
        
