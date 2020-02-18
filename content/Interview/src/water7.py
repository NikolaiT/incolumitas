class Solution:
    def maxArea(self, height):
        """
        :type height: List[int]
        :rtype: int
        
        Idea: keep two pointers, one to the rightmost
        element and one to the leftmost element. Compute area and
        update if with max.
        Move the point for the element/line which is smaller one element
        inwards. We can do this, because all possible areas with the smaller
        element fixed would be smaller than what we currently have. 
        Proceed like this until the pointers approach each other.
        
        Runtime: 68 ms, faster than 79.66% of Python3 online submissions for Container With Most Water.

        Runtime: O(n)
        """
        n = len(height)-1
        l = 0
        r = n
        m = 0
        while l<r:
            m = max(m, min(height[l], height[r]) * (r-l))
            if height[l] >= height[r]:
                r -= 1
            else:
                l += 1
        return m
        
s = Solution()
print(s.maxArea([1,8,6,2,5,4,8,3,7]))
