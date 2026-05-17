print('''1. 제목 입력
2. 내용 입력
3. 조회
4. 종료
''')

userSelect = int(input('메뉴를 선택하세요: '))

while userSelect != 4:
    if userSelect == 1:
        memoTitle = input('제목을 입력하세요: ')
    elif userSelect == 2:
        memoContent = input('내용을 입력하세요: ')
    elif userSelect == 3:
        print(memoTitle)
        print(memoContent)
    else:
        print('잘못된 입력입니다')

    userSelect = int(input('메뉴를 선택하세요: '))