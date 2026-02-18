class Solution:
    def numberofsubarrays(self, nums: list[int], target:int) -> int:

        left = 0
        middle = 0
        odd = 0
        res = 0

        for r in range(len(nums)):
            if nums[r] %2 == 1:
                odd = odd +  1
            
            while odd > target:
                if nums[left]%2 == 1:
                    odd-=1
                left = left +1
                middle = left

            if odd == target: 
                while(nums[middle]%2 ==0):
                    middle = middle + 1

                res += middle - left +1
        return res


test = Solution()
nums = [2, 2, 1, 2, 1]
k = 2
print(test.numberofsubarrays(nums,k))