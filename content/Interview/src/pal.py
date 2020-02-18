"""
This solution takes at least O(n^2 * n/2) = O(n^3)
This is too bad. O(N^2) must be possible.
"""

test = "jglknendplocymmvwtoxvebkekzfdhykknufqdkntnqvgfbahsljkobhbxkvyictzkqjqydczuxjkgecdyhixdttxfqmgksrkyvopwprsgoszftuhawflzjyuyrujrxluhzjvbflxgcovilthvuihzttzithnsqbdxtafxrfrblulsakrahulwthhbjcslceewxfxtavljpimaqqlcbrdgtgjryjytgxljxtravwdlnrrauxplempnbfeusgtqzjtzshwieutxdytlrrqvyemlyzolhbkzhyfyttevqnfvmpqjngcnazmaagwihxrhmcibyfkccyrqwnzlzqeuenhwlzhbxqxerfifzncimwqsfatudjihtumrtjtggzleovihifxufvwqeimbxvzlxwcsknksogsbwwdlwulnetdysvsfkonggeedtshxqkgbhoscjgpiel"
test2 = "abababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababababa"
test3 = "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"

import math

class Solution:
    def checkPal(self, i, k, s):
        """
        Check whether substr s[i:k]
        is a palindrome
        """
        #print(i,k)
        is_pal = True
        for j in range(math.ceil((k-i)/2)):
            #print('\t', i+j,k-j)
            if s[i+j] != s[k-j]:
                return False
        return is_pal
            
    def longestPalindrome(self, s):
        """
        :type s: str
        :rtype: str
        """
        # palindrome has the following properties
        # 1. string is mirrored in the middle
        # 2. n = len(s), [0] == s[n], s[i] == s[n-i] for all i in n/2
        n = len(s)
        if n <= 1:
            return s
        palindromes = dict()
        for i, c in enumerate(s):
            if palindromes and max(palindromes) >= n-i:
                break
            for k in reversed(range(i+1, n)):
                if self.checkPal(i, k, s):
                    palindromes[k+1-i] = s[i:k+1]
                    if (n-i) <= (k-i):
                        break
                    
        if not palindromes:
            return s[0]
        else:
            return palindromes[max(palindromes)]
            
if __name__ == '__main__':
    sol = Solution()
    longest = sol.longestPalindrome(test3)
    print(longest)
