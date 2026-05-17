nums = [1,2,3,4,5,6,7,8,9,10]
total = 0

for i in nums:
    if (i % 2 == 0):
        print(f'짝수 발견: {i}')
        total += i


print(f'짝수 합계: {total}')