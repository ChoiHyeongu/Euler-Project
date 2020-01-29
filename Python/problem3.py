# def getMaxPrimeFactor(n):
#     for i in range(2, n):
#         if n==1 : 
#             break
#         while n%i == 0:
#             if n // i == 1:
#                 print (n)
#             n //= i
            
# getMaxPrimeFactor(600851475143)

Num=1
def FindBiggestPrimeFactor(N):
    for i in range(2,N+1):
        print("N%i=",N%i)
        if N%i==0:
            Num=i
            N//=i
            if N==1:
                print("NUM: ", Num)
                break
                print("NO BREAK")
            else:
                FindBiggestPrimeFactor(N)
        else:
            continue

FindBiggestPrimeFactor(100)