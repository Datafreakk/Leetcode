class Solution:
    def binarysearch(self, nums:list[list[int]], target:int):
         left = 0
         right = len(nums)-1

         while(left<=right):
              mid = (left +right) // 2

              if(nums[mid] == target):
                   return mid
              
              if (nums[mid]<target):
                   left = mid + 1
              else:
                   right = mid - 1

             
         return -1
                

# Test
nums=[-1,0,3,5,9,12]
target = 9
sol = Solution()
print(sol.binarysearch(nums,target))               
            

                   