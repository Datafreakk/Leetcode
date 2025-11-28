# 
# 
# 
# 1.Move indexes  and also check not zero
# 2.loop each value and check value and return misisng  else n +1

class Solution():
    def firstMissingPositive(self, nums:list[int]): 
        n = len(nums)
        
        for i in range(n):
            while 1 <= nums[i] <= n  and nums[i] != nums[nums[i]-1]:
                correct_index  = nums[i]-1
                nums[i], nums[correct_index ] = nums[correct_index ] , nums[i]
                
        for  i in range(n): 
            if nums[i]!= i +1:
                return i + 1
    
        return n +1

#Test           
nums = [6, 8, 2, -1]
sol = Solution()
print(sol.firstMissingPositive(nums))  
                
            
                
        
        
        
        
        
    