m = 0
l = None
# Python program for implementation of MergeSort 
def mergeSort(arr):
    if len(arr) > 1:
        mid = len(arr)//2 #Finding the mid of the array 
        L = arr[:mid] # Dividing the array elements  
        R = arr[mid:] # into 2 halves 
  
        mergeSort(L) # Sorting the first half 
        mergeSort(R) # Sorting the second half 
  
        i = j = k = 0
          
        # Copy data to temp arrays L[] and R[] 
        while i < len(L) and j < len(R):
            global m,l
            test = min(L[i][0], R[j][0]) * (R[j][1]-L[i][1])
            if test > m:
                m = test
                l = L[i], R[j]
            
            if L[i] < R[j]:
                arr[k] = L[i] 
                i+=1
            else: 
                arr[k] = R[j] 
                j+=1
            k+=1
        
        # Checking if any element was left 
        while i < len(L):
            test = min(L[i][0], R[j][0]) * (R[j][1]-L[i][1])
            arr[k] = L[i] 
            i+=1
            k+=1
          
        while j < len(R):
            arr[k] = R[j] 
            j+=1
            k+=1
  
# Code to print the list 
def printList(arr): 
    for i in range(len(arr)):         
        print(arr[i],end=" ") 
    print() 
  
# driver code to test the above code 
if __name__ == '__main__':
    arr = range(1000)
    data = [(e,i) for i,e in enumerate(arr)]
    print ("Given array is", end="\n")
    printList(data) 
    mergeSort(data)
    print("Sorted array is: ", end="\n") 
    print('max area is {}'.format(m))
    printList(data) 
  
# This code is contributed by Mayank Khanna 
