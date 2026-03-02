class Solution():
    def substr(self,haystack:str,needle:str) -> int:

        if needle == "":
            return False
        
        for i in range(len(haystack)-len(needle)+1):
            if haystack[i:i+len(needle)] == needle:
                return i
            
        return -1
                
#Test
sol = Solution()
haystack = "sadbutsad"
needle = "sad"
print(sol.substr(haystack,needle))