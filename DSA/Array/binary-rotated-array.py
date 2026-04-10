class Solution:
    def Search(self, nums:list[int], target:int): 
         left = 0
         right = len(nums)-1
         
         while (left<=right):
              mid = (left +right) // 2

              if nums[mid] == target:
                  return mid

              if (nums[left]<= nums[mid] ):
                #    //left sorted array
                 if(nums[left]<= target < nums[mid]):
                     right = mid-1
                 else:
                     left = mid +1
              else:
                  if(nums[mid]< target <= nums[right]):
                      left = mid + 1
                  else:
                      right = mid - 1
         return -1

# Test
nums= [4,5,6,7,0,1,2]
target = 6
sol = Solution()
print(sol.Search(nums,target))