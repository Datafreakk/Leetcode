class Solution:
    def canAtti2Meetings(self, intervals:list[list[int]]):
        intervals.sort(key = lambda i : i[0])
        for i in range (1,len(intervals)):
            i1 = intervals[i-1]
            i2 = intervals[i]
            if i2[0] < i1[1]:
                return False
        return  True
            

 #Test           
intervals = [(0,30),(5,10),(15,20)]
sol = Solution()
sol.canAtti2Meetings(intervals)