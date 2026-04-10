class Solution:
    def minSubArrayLen(self, target: int, nums: list[int]) -> int:
        left = 0
        total = 0
        min_len = float('inf')

        for right in range(len(nums)):
            total += nums[right]
            while (total >= target):
                min_len = min(min_len, right-left + 1 )
                total = total - nums[left]
                left +=1
        return min_len if min_len != float('inf') else 0 



# #Test           
nums =  [2,3,1,2,4,3]
sol = Solution()
target = 7
print(sol.minSubArrayLen(target, nums))