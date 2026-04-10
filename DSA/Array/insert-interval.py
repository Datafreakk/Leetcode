class Solution:
    def insert(self, intervals:list[list[int]], newInterval:list[list[int]]) -> list[list[int]]: 
        res=[]

        for i in range(len(intervals)):
              if newInterval[1] < intervals[i][0]:
                 res.append(newInterval)
                 return res + intervals[i:]
              
              elif newInterval[0] > intervals[i][1]:
                   res.append(intervals[i])
              else:
               newInterval = [min(intervals[i][0],newInterval[0]),max(intervals[i][1],newInterval[1])]

        res.append(newInterval)
        return res

#Test
sol = Solution()
intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]]
newInterval = [4,8]
print(sol.insert(intervals,newInterval))