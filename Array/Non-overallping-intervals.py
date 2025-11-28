class Solution:
    def eraseOveralpIntervals(self, intervals: list[list[int]]) -> int:
         
        #  intervals.sort()

        #  intervals_count = 0
        #  prev_end = intervals[0][1]
        #  for start , end in intervals[1:]:
        #       if start >= prev_end:
        #            prev_end = end
        #       else:
        #            intervals_count += 1
        #            prev_end = min(end, prev_end)
        #  return intervals_count
                           
        intervals.sort(key = lambda i :i[1])

        intervals_count = 0
        prev_end = intervals[0][1]
        for i in range(1 ,len(intervals)):
              start,end = intervals[i]

              if start < prev_end:
                    intervals_count += 1
              else:
                   prev_end = end
                   
        return intervals_count
    
                   



# Test
sol = Solution()
intervals = [[1,2],[1,2],[1,2]]
print(sol.eraseOveralpIntervals(intervals))