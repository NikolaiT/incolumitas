def binary_search(lst, value):
    count = len(lst)
    first = 0

    while count:
        it = first
        step = count // 2
        it += step
        if value > lst[it]:
            it += 1
            first = it
            count -= step + 1
        else:
            count = step

    return first
    
def get_median_offset(mi, offset):
    """
    mi = 3, offset = 2 -> mi = 4
    mi = (1,2), offset = -1 -> mi = 1
    """
    if type(mi) == tuple:
        if offset % 2 == 1:
            # result is skalar median
            # [3,4], 3, return 3.5+1.5
            return int ( (mi[0]+mi[1])/2 + offset/2 )
        else:
            # result is tuple
            # [3,4], 2, return [4,5]
            return (mi[0]+offset//2, mi[1]+offset//2)
    else:
        if offset % 2 == 1:
            # result is tuple
            # 3, offset=3, return [4,5]
            return (mi+offset//2,mi+offset//2+1)
        else:
            # result is skalar
            return mi+offset//2

class Solution:
    def findMedianSortedArrays(self, nums1, nums2):
        """
        nums1 = [1, 3]
        nums2 = [2]
        The median is 2.0
        
        nums1 = [1, 2]
        nums2 = [3, 4]
        The median is (2 + 3)/2 = 2.5
        
        The next idea is too locate the area of both arrays where they are overlapping.
        
        nums1 = [1, 2, 3, 4, 5, 6, 12]
        nums2 = [4, 6, 8, 16]
        overlapping = [4,5,6]
        
        When we know the elements that are overlapping, we also know 
        the median element of both arrays, since we can each determine
        how many elements are smaller and larger than the indices of the 
        boundaries of the overlapping area.
        Is this necessariliy true?
        
        [1,2,3,4,5]
        [0,0,0]
        overlapping = []
        => no info
        
        Algorithm idea. Get the median element of the larger array.
        See if element occurs in the smaller array.
        [1,2,3,4,5]
        [0,0,0]
        
        is 3 in [0,0,0]?
        where would it be?  [0,0,0,3]
        Search position with binary search (log n)
        => 3 elements are smaller than 3
        => in combined array, median shifts (3-0)/2 to the left
        => What is the median in the combined array? 
         We can only know after we have inserted all smaller
         than median elements into the combined array.
         To do so, this takes m/2*log(n) time
         [0,0,0,1,2,3,4,5]
         new median: 1.5
         
         Notice: We don't have to insert ALL smaller elments! Maybe we don't 
         even have to insert any of them to compute the combined median!
         We only need to know whether some of the smaller elements become
         a part of the new median!!!
         
         How can we know? By determining the position of the largest of the smaller
         events. If the position is greater or equal to the new median element, keep inserting,
         if not, we can print the new median and stop inserting smaller values.
         This is probably very efficient.
         
         
        Runtime: 164 ms, faster than 21.07% of Python3 online
        submissions for Median of Two Sorted Arrays.
        """
        def get_median(l):
            if not l:
                return
            n = len(l)
            if n % 2 == 0:
                return ( l[(n//2)-1] + l[n//2] ) / 2, ((n//2)-1, n//2)
            else:
                return l[n//2], n//2
                
        if len(nums1) > len(nums2):
            larger, smaller = nums1, nums2
        elif len(nums1) < len(nums2):
            larger, smaller = nums2, nums1
        else:
            # make one larger than the other
            # by popping the largest element from one array
            e = nums2.pop()
            nums1.insert(binary_search(nums1, e), e)
            larger = nums1
            smaller  = nums2
            
        n = len(larger)
        m = len(smaller)
            
        median, mindex = get_median(larger)
        
        # find median position in smaller of the arrays
        # use binary search, since the array is sorted
        # [1,2,3,4,5,6,7,8]
        # search pos of 5
        pos = binary_search(smaller, median)
        smaller_half, larger_half = smaller[:pos], smaller[pos:]
        
        curr_median, index = get_median(larger)
        old_index = index
        
        def is_neighbor_index(a,b,n):
            n = max(n,1)
            if type(a) == tuple:
                return abs(a[0]-b) <= n or abs(a[1]-b) <= n
            else:
                return abs(a-b) <= n
                
        k = len(smaller_half)
        j = len(larger_half)
                
        while smaller_half:
            c = smaller_half.pop()
            c_index = binary_search(larger, c)
            if is_neighbor_index(index, c_index, len(smaller_half)//2+1) or c >= curr_median:
                k -= 1
                larger.insert(c_index, c)
            else:
                break
            curr_median, index = get_median(larger)
            
        while larger_half:
            d = larger_half.pop(0)
            d_index = binary_search(larger, d)
            if is_neighbor_index(index, d_index, len(larger_half)//2+1) or d <= curr_median:
                j -= 1
                larger.insert(d_index, d)
            else:
                break
            curr_median, index = get_median(larger)
        
        # given a list L with length n
        # and median index n//2 or (n//2)-1 and n//2
        # add x items to the left of list
        # add y items to the right of list
        # what is the median index now?
        #[1,2,3] x=3, y=1, median index = 1
        #[x,x,x,1,2,3,y], median index = 3
        # median index increases with (x+y)/2
        # other example: 
        # [4,50,100,200,300,400,1000,20000] median index = 3,4
        # add [0,1,2,3] to the left
        # [0,1,2,3,4,50,100,200,300,400,1000,20000] median index = 5,6
        # does it increase with x-y = 4-0 = 4 ? NO
        # it increases with (x+y)/2 = 2
        
        # but what if we have an array with
        # [1,2,3] and we know the median element must lie
        # in this array after it is increased by adding the 
        # array [4]
        # previously, median is 2 with index 1
        # after adding 4, median is 2.5 with indices 1,2
        # for a array with n places, there are 2n possible median places
        _, median_index = get_median(larger)
        delta = -k + j
        new_median = get_median_offset(median_index, delta)
            
        if type(new_median) == tuple:
            return (larger[new_median[0]] + larger[new_median[1]])/2
        else:
            return larger[new_median]
            
def test():
    test_items = [([0,1,2,3], [4,50,100,200,300,400,1000,20000]),
     ([4], [1,2,3]), ([4,5], [1,2,3]), ([5], [1,2,3,4]), ([1,3], [2]), ([4], [1,2,3,5,6]),
     ([5,6,7], [1,2,3,4,8])]
    for t in test_items:
        s = Solution()
        print('Testing: {}'.format(t))
        print(s.findMedianSortedArrays(*t))
    
if __name__ == '__main__':
    test()
