class Solution:
    def convert(self, s, numRows):
        """
        :type s: str
        :type numRows: int
        :rtype: str
        
        zigzag font means there are 
        always a column full of chars,
        then numRows-2 diagonal chars
        then again a column full of chars
        then again numRows-2 diagonal chars...
        
        So how many columns in total will we get?
        
        PAYPALISHIRING, n=14, numRows=3
        columns: 1 1 1 1 1 1 1 = 7
        chars:   3 1 3 1 3 1 2
        
        PAYPALISHIRING, n=14, numRows=4
        columns: 1 1 1 1 1 1 1 = 7
        chars:   4 1 1 4 1 1 2
        
        PAYPALISHIRING, n=14, numRows=5
        columns: 1 1 1 1 1 1 = 6
        chars:   5 1 1 1 5 1
        
        PAYPALISHIRING, n=14, numRows=6
        columns: 1 1 1 1 1 1 = 6
        chars:   6 1 1 1 1 4
        
        Runtime: 108 ms, faster than 59.59% of Python3 online submissions for ZigZag Conversion.
        Runtime: O(n * log(n))
        """
        indices = [None] * len(s)
        
        col = row = bt = tbt = 0
        for i,c in enumerate(s):
            indices[i] = (col,row,i)
            if bt>0:
                indices[i] = (col,bt,i)
                col += 1
                bt -= 1
                if bt == 0:
                    row = 0
                    continue

            if (i+1-tbt)%numRows == 0:
                col += 1
                row = 0
                bt = numRows-2
                tbt += bt
                continue
            row += 1
            
        sorted_rowwise = sorted(indices, key=lambda e: e[1])
        
        res = ''
        for e in sorted_rowwise:
            res +=s[e[2]]
        return res
        
        
s = Solution()
assert s.convert('PAYPALISHIRING', 3) == 'PAHNAPLSIIGYIR'
assert s.convert('PAYPALISHIRING', 4) == 'PINALSIGYAHRPI'
assert s.convert('ABC', 1) == 'ABC'
        
        
