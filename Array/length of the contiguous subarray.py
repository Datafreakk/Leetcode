#class Solution:
    # def maxSubArray(self, nums: list[int]) -> int:
    #     max_sum = float('-inf')
    #     n = len(nums)
    #     
    #     for i in range(n):
    #         current_sum = 0
    #         for j in range(i, n):
    #            current_sum +=nums[j]
    #            if current_sum > max_sum:
    #              max_sum = current_sum
    #     return max_sum
                 

#optimsied
# 1.if current sum is negative ignore it
# 2.add current sum with nth element  and cala max of subarray and current array

class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        current_sum  = 0
        max_sum   = nums[0]
        for i in nums: 
            if current_sum  < 0:
                current_sum  = 0
            current_sum  += i
            max_sum = max(current_sum ,max_sum)
        return max_sum
    

    
            
    
#Test           
num =  [3, -1, 0, 2, 100]
sol = Solution()
print(sol.maxSubArray(num))