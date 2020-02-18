class Solution:
    def isPalindrome(self, x):
        """
        :type x: int
        :rtype: bool
        
        Runtime: 264 ms, faster than 89.26% of Python3 online submissions for Palindrome Number.
        """
        s = str(x)
        i,j = 0, len(s)-1
        
        while s[i] == s[j]:
            if i == j or (i+1==j):
                return True
            i += 1
            j -= 1
        return False
