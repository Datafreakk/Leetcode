class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]: 
         
         intervals.sort(key= lambda i :i[0])
         output = [intervals[0]]

         intervals_from_second = intervals[1:]

         for start,end in intervals_from_second: 
              if start <= output[-1][1]:
                   output[-1][1] = max(end,output[-1][1])
              else:
                   output.append([start,end])
         return output
    


    #Test
sol = Solution()
intervals = [[1,3],[2,6],[8,10],[15,18]]
print(sol.merge(intervals))