class Solution:
    def findDuplicate(self, nums:list[int]) -> int: 

        for i in range(len(nums)):
            while nums[i] != i +1:
               target_index = nums[i]-1

               if nums[i] == nums[nums[i]-1]:
                   return nums[i]
               else:
                   nums[i], nums[target_index] = nums[target_index], nums[i]  # correct swap
             
        return -1
    
#Test
sol = Solution()
nums = [2, 1, 3, 4, 2]
print(sol.findDuplicate(nums))
