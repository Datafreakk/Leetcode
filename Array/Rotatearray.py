class Solution:
    
    def rotate(self, nums:list[int], k):
        n = len(nums)
        k = k % len(nums)
        
        self.reverse(nums, 0, n-1)
        self.reverse(nums, 0, k-1)
        self.reverse(nums,k,n-1)
        
    def reverse(self, nums:list[int], left, right):
         left = 0
         right = len(nums)-1
         while left < right:
             nums[left], nums[right] = nums[right], nums[left]
             left+=1
     
#Test
sol = Solution()
nums = [2,0,2,1,1,0]
sol.rotate(nums,3)
print(nums)