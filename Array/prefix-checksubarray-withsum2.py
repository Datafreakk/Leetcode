class Solution:
    def checksubbaray(self, nums: list[list[int]], k:int):
         
         hasp_map_tracker = {0 : -1}
         running_sum = 0
     
         for i,v in enumerate(nums):
            running_sum+=v
            remainder = running_sum%k 

            if remainder not in hasp_map_tracker:
                hasp_map_tracker[remainder] = i 
            elif i - hasp_map_tracker[remainder] > 1:
                 return True
            
         return False
    

#Test
test = Solution()
nums = [23,2,6,1,4]
k = 6
print(test.checksubbaray(nums,k))