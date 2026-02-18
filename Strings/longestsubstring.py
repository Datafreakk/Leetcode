class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        left = 0
        charSet = set()
        res = 0

        for r in range(len(s)):
            while s[r] in charSet:
                charSet.remove(s[left])
                left = left + 1
            charSet.add(s[r])

            res = max(res, r - left +1)
        return res 

            

#Test
s = "pwwkew"
sol = Solution()
print(sol.lengthOfLongestSubstring(s) )