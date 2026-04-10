import collections

class Solution:
    def totalFruit(self, fruits: list[int]) -> int: 
        left = 0
        total =0
        result = 0
        count = collections.defaultdict(int)

        for r in range(len(fruits)): 
            count[fruits[r]] += 1
            total += 1 

            while(len(count)>2):
                count[fruits[left]] -=1
                total -=1

                if not count[fruits[left]]:
                    count.pop(fruits[left])
                left += 1
            result = max(result, total)

        return result



        
#Test
sol = Solution()
fruits = [0,1,2,2]
print(sol.totalFruit(fruits))
           



# logic
# 1.Make a dictionary with counting key:value
# 2.ensure count of hashmap is 2 and remove extra