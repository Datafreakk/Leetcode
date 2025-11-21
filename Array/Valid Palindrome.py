class Solution:
   def isPalindrome(self, string: str) ->bool:
      left = 0
      right = len(string)-1

      while(left < right):
           while left < right and not self.alphanUm(string[left]):
                left +=1
           while left < right and not self.alphanUm(string[right]):
                right -=1
           if string[left].lower() != string[right].lower():
                return False
           left +=1
           right -=1
      return True
                
         
   def alphanUm(self, c):
        return (('A' <= c <= 'Z') or 
                  ('a' <= c <= 'z') or 
                  ('0' <= c <= '9'))

#Test
sol = Solution()
s = "A man, a plan, a canal: Panama"
print(sol.isPalindrome(s))