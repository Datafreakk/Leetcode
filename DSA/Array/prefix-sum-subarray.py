from collections import defaultdict

class Solution:
    def subarray_nums(self,nums:list[list[int]], k:int):
         prefixsum = 0
         sub_array_count = 0
         prefix_count = defaultdict(int)
         prefix_count[0] = 1

         for num in nums:
              prefixsum = prefixsum + num
              needed_sum = prefixsum-k

              if needed_sum in prefix_count:
                   sub_array_count = sub_array_count + prefix_count[needed_sum]

              prefix_count[prefixsum]+=1
         return sub_array_count

test = Solution()
k = 3
nums = [1, -1, 2, 3]
print(test.subarray_nums(nums,k))


# Neetcode
# class Solution:
#     def subarraySum(self, nums: List[int], k: int) -> int:
#         count = 0
#         prefix_sum = 0
#         prefix_count = {0: 1}  

#         for num in nums:
#             prefix_sum += num
#             count += prefix_count.get(prefix_sum - k, 0)
#             prefix_count[prefix_sum] = prefix_count.get(prefix_sum, 0) + 1

#         return count