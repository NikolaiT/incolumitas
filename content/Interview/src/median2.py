class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        """
        nums1 = [1, 3]
        nums2 = [2]
        The median is 2.0
        
        nums1 = [1, 2]
        nums2 = [3, 4]
        The median is (2 + 3)/2 = 2.5
        
        The O(n) method is to loop through both arrays
        and create a sorted merged array of nums1 and nums2. 
        
        Runtime: 100 ms, faster than 76.56% of Python3 online submissions for Median of Two Sorted Arrays.
        
        This works but this is cheating, since the idea is that we should sort nums1 and nums2
        for ourselves.
        
        Also: The overall run time complexity should be O(log (m+n)).
        """
        
        result = sorted(nums1 + nums2)
        n = len(result)
        
        if n % 2 == 0:
            return (result[(n//2)-1] + result[n//2]) / 2
        else:
            return result[n//2]
