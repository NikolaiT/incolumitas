def ith_digit(x, i):
    """
    Returns the i-th digit 
    from a number with n digits.
    """
    a = x//pow(10,i)
    return a%10

class Solution:
    def isPalindrome(self, x):
        """
        :type x: int
        :rtype: bool
        Runtime: 368 ms, faster than 45.19% of Python3 online submissions for Palindrome Number.
        """
        if x<0:
            return False
            
        # get length of digit
        n = 1
        while x//pow(10,n) > 0:
            n += 1
        
        i = 0
        j = n-1
        while ith_digit(x,i) == ith_digit(x,j):
            if i == j or (i+1==j):
                return True
            i += 1
            j -= 1
        return False

s = Solution()
print(s.isPalindrome(56765))
print(s.isPalindrome(10))
print(s.isPalindrome(1011))
print(s.isPalindrome(10111101))
