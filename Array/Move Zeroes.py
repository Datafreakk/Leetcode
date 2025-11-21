class Solution:
    def moveZeros(self, nums: list[int]) ->  None:

        left = 0
        for right in range(len(nums)):
            if nums[right]:
                nums[left], nums[right] = nums[right], nums[left]
                left +=1

        return nums
    
#Test
sol = Solution()
nums = [0,1,0,3,12]
print(sol.moveZeros(nums))
 