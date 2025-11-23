class Solution:
    def longestOnes(self, nums:list[int], k:int) -> int:
        max_window = 0
        num_zeros = 0 
        l = 0
    

        for r in range(len(nums)):
           if nums[r] == 0:
             num_zeros += 1

           while num_zeros > k:
             if nums[l] == 0:
                num_zeros -= 1 
             l = l +1
             window = r - l + 1
             max_window = max(max_window,window)
        return max_window
    
           
#Test
sol = Solution()
nums = [1,1,1,0,0,0,1,1,1,1,0]
k = 2
print(sol.longestOnes(nums,k))