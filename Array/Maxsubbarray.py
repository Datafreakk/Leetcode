class Solution:
    def maxSubArray(self, nums: list[int]) -> int: 
        currentsum= 0

        maxsubarray = nums[0]

        for i in nums: 
            if currentsum < 0:
                currentsum = 0
            currentsum += i
            maxsubarray = max(currentsum, maxsubarray) 
        return maxsubarray
    
# #Test           
nums =  [5,4,-1,7,8]
sol = Solution()
print(sol.maxSubArray(nums))