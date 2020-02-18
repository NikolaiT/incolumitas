class Solution:
    def reverse(self, x):
        """
        :type x: int
        :rtype: int
        
        For the purpose of this problem, assume that your function returns 0 when the reversed integer overflows.
        
        Runtime: 52 ms, faster than 99.23% of Python3 online submissions for Reverse Integer.
        """
        s = str(x)
        sign = ('-' == s[0])
        
        if sign:
            s = s[1:]
        
        r = s[::-1]
        
        if sign:
            rint = int('-'+r)
        else:
            rint = int(r)
            
        if pow(2, 31)-1 < rint or -pow(2, 31) > rint:
            return 0
        return rint
