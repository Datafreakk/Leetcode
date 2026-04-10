class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        count = {}
        left = 0
        right = 0
        maxf = 0
        res = 0
        
        for right in range(len(s)):
            count[s[right]] = 1 + count.get(s[right],0)
            maxf = max(maxf, count[s[right]])

            while( right - left + 1 ) - maxf > k:
                count[s[left]]-=1
                left = left + 1
            res = max(res, right - left + 1)
        return res
        
#Test
s = "ABAB"
k = 2
sol = Solution()
print(sol.characterReplacement(s,k) )