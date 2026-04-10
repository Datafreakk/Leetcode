
# class Solution:
#     def squareofsortedarray(self, num: list[int]) -> list[int]:
#         left = 0
#         right = len(num)-1
#         result = []

#         while(left <= right):
#             if(abs(num[left]) > abs(num[right])):
#                 result.append(num[left]**2)
#                 left += 1
#             else:
#                 result.append(num[right]**2)
#                 right -= 1
#         result.reverse()
#         print(result)

#         return result
    
# #Test           
# num = [ -4,-1,0,3,10]
# sol = Solution()
# sol.squareofsortedarray(num)

class Solution:
    def squareofsortedarray(self, num: list[int]) -> list[int]:
        left = 0
        n = len(num)
        right = n-1
        result = [0] * n

        pos = n-1 
        while(left <= right):
            if(abs(num[left]) > abs(num[right])):
                result[pos] = num[left]**2
                left += 1
            else:
                result[pos] = num[right]**2
                right -= 1
            pos -=1
        print(result)

        return result
    
 #Test           
num = [ -4,-1,0,3,10]
sol = Solution()
sol.squareofsortedarray(num)