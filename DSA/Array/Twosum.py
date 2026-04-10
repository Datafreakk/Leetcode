class Solution:
    def twoSum(self, numbers: list[int], target: int) -> list[int]:
        left = 0
        right = len(numbers)-1

        while(left < right):
            Cursum = numbers[left] +numbers[right]

            if Cursum > target:
                right -= 1

            elif Cursum < target:
                left += 1
            else :
               return [left+1,right+1]
        return[]
    
#Test
sol = Solution()
numbers = [5,25,75]
target = 100
print(sol.twoSum(numbers, target))



