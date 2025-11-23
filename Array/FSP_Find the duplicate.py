# Find the Duplicate Number

import collections

# class Solution:
#     def findDuplicate(self, nums: list[int]) -> int:
#         count = collections.defaultdict(int)
#         for i in range(len(nums)):
#             count[nums[i]] += 1
#             if count[nums[i]] > 1:
#                 return nums[i]

        # max_value = max(count.values())
        # for key, values in count.items():
        #     if values == max_value:
        #         return key


class Solution:
    def findDuplicate(self, nums: list[int]) -> int:
        slow = 0
        fast = 0
         # Phase 1: detetct cycle 
        while True:
            slow = nums[slow]
            fast = nums[nums[fast]]
            if slow == fast:
                break
        
         # Phase 2: find entrance to cycle
        slow2 = 0
        while True:
            slow2 = nums[slow2]
            slow = nums[slow]
            if slow == slow2:
                break

        return slow2
    


         
#Test
sol = Solution()
nums = [1,3,4,2,2]
print(sol.findDuplicate(nums))