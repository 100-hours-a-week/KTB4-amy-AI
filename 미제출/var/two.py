num = int(input('번호를 선택해주세요'))
nums=[]

while num != 6:
    if num == 1:
        tmp = input('텍스트 입력:')
        nums.append(tmp)
    elif num == 2:
        print(nums[-1])
    elif num == 3:
        nums[-1] = input('수정 텍스트 입력: ')
    elif num == 4:
        nums.pop()
    elif num == 5:
        print(nums)

    num = int(input('번호를 선택해주세요'))