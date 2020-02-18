test = "jglknendplocymmvwtoxvebkekzfdhykknufqdkntnqvgfbahsljkobhbxkvyictzkqjqydczuxjkgecdyhixdttxfqmgksrkyvopwprsgoszftuhawflzjyuyrujrxluhzjvbflxgcovilthvuihzttzithnsqbdxtafxrfrblulsakrahulwthhbjcslceewxfxtavljpimaqqlcbrdgtgjryjytgxljxtravwdlnrrauxplempnbfeusgtqzjtzshwieutxdytlrrqvyemlyzolhbkzhyfyttevqnfvmpqjngcnazmaagwihxrhmcibyfkccyrqwnzlzqeuenhwlzhbxqxerfifzncimwqsfatudjihtumrtjtggzleovihifxufvwqeimbxvzlxwcsknksogsbwwdlwulnetdysvsfkonggeedtshxqkgbhoscjgpiel"


class Solution:
    def longestPalindrome(self, s):
        """
        :type s: str
        :rtype: str
        """
        # when s[0] != s[-1], then
        # s[1:-1] or s[0:-2] might be still a 
        # palindrome
        n = len(s)
        to_check = set()
        already_checked = set()
        to_check.add((0, n-1))
        same = dict()
        
        def maybe_add(t):
            if t not in already_checked:
                to_check.add(t)
                already_checked.add(t)
        
        while to_check:
            i, j = to_check.pop()
            if s[i] != s[j]:
                if i+1 < j:
                    maybe_add((i+1, j))
                if i < j-1:
                    maybe_add((i, j-1))
            else:
                same[i] = j
                if i+1 <= j-1 and j-1 >= 0:
                    maybe_add((i+1, j-1))
                if i-1 >= 0 and j+1 <= n-1:
                    maybe_add((i-1, j+1))
                    
        longest = dict()
        print(same)
                    
        for i, j in same.items():
            k = i
            l = j
            longest[(k,l)] = [(k,l), ]
            while True:
                k = k + 1
                l = l - 1
                can = (k, l)
                #if can[0] == can[1] or can[0]+1 == can[1]:
                    #print('found:', longest[(i,j)])
                if can in same:
                    print('one more')
                    longest[(i,j)].append(can)
                else:
                    break
                
        #print(longest)


s = Solution()
s.longestPalindrome(test)
