class solution:
    # def ISpalindrome(self, n:int) -> bool:
    #     s = str(n)
    #     return s == s[::-1]
    #     # print (s)
    #     # return s

     def ISpalindrome(self, n:int) -> bool:
          if n < 0  or  (n % 10 == 0 and n != 0):
               return False
          
          reversedhalf = 0
          while n > reversedhalf:
               reversedhalf = (reversedhalf * 10) + (n % 10)
               n = n // 10
          return  n == reversedhalf  or n == reversedhalf // 10
           

          

sol = solution()
print(sol.ISpalindrome(121))



