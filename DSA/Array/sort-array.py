class Solution:
    def sortcolors(self, nums:list[int]) -> None:

        left = 0
        right = len(nums)-1
        i = 0

        def swapper(a, b):
            nums[a], nums[b] = nums[b], nums[a]

        while i <= right:
            if nums[i] == 0:
                    swapper(left,i)
                    i = i +1
            elif nums[i] == 2:
                    swapper(right,i)
                    right = right -1
                    # i -=1
            else:
                 i+=1

                  
#Test
sol = Solution()
nums = [2,0,2,1,1,0]
sol.sortcolors(nums) 
print(nums)