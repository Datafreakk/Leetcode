class Solution:
    def searchMatrix(self, matrix: list[list[int]], target:int): 
         
         rows = len(matrix)
         col = len(matrix[0])

         top = 0
         bottom = len(matrix) -1

         while (top <= bottom):
              row = (top + bottom) // 2
              if target > matrix[row][-1]:
                   top = row +1
              elif target < matrix[row][0]:
                   bottom = row -1
              else:
                   break
        
         if top > bottom:
              return False
         
         left = 0
         right = len(matrix[0])-1
         row = (top + bottom) // 2
         while(left <= right):
              m = (left +right) // 2
              if  target == matrix[row][m]:
                   return True
              elif target > matrix[row][m]:
                   left = m +1
              else:
                   right = m -1
         return False
    
    # Test
nums= [
  [1,  5,  7,  9],
  [20, 25, 30, 35],
  [40, 45, 50, 55]
]
sol = Solution()
print(sol.searchMatrix(nums,9))