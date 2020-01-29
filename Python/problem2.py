a = 1
b = 1
sum = 0

while b<=4000000:
	a,b = b, a+b
	if a%2 == 0:
		print(a)
		sum += a

print (sum)
print (a)
print (b)
