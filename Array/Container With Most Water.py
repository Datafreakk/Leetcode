#Brute force
# class Solution:
#     def maxArea(self, height: list[int]) -> int:

#         result = 0
        
#         for l in range(len(height)):
#             for r in range(l+1,len(height)):
#                 area = (r-l ) * min (height[l],height[r])
#                 result = max(area,result)
        
#         return result
    

#Linear solution
class Solution:
    def maxArea(self, height: list[int]) -> int:

        l = 0
        r = len(height)-1
        result = 0

        while(l < r):
            area = (r-l) * min(height[l],height[r])
            result = max(area,result)

            if height[l] < height[r]:
                l += 1
            else:
              r -= 1
        return result 


#Test
height = [1,8,6,2,5,4,8,3,7]
sol = Solution()
print(sol.maxArea(height))