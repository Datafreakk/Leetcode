class Solution:
    def findDisasspaerednumber(self, nums:list[list[int]]) -> list[int]: 
       
       for n in nums:
           i =  abs(n)-1
           nums[i] = -1 * abs(nums[i])

           res= []
           for i,n in enumerate(nums):
               if n > 0:
                   res.append(i+1)


       return res



#Test
sol = Solution()
nums = [4,3,2,7,8,2,3,1]
print(sol.findDisasspaerednumber(nums))