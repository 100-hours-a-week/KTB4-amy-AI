#메뉴 보여주기
print('''1. 메뉴 선택
2. 조회
3. 수정
4. 삭제
5. 추가기능
6. 종료''')
num = int(input('메뉴를 선택해주세요: '))
memoTitle = []
memoContent = []

#6이 되면 종료가 되므로 입력받는 값이 6이 아닐때는 작동되도록 반복문 조건을 num != 6 으로 함
while num != 6:
    if num == 1:
        pass
    elif num == 2: #제목을 입력받아 내용의 인덱스 찾아서 출력하기
        print(memoTitle)
        tmp = input('조회할 메모의 제목을 입력해 주세요')
        tmp_index = memoTitle.index(tmp)
        print(memoTitle[tmp_index])
    elif num == 3: # 메모의 번호를 받아 수정, 인덱스와 번호는 세는 방법이 다르므로 -1
        try:
            tmp = int(input('수정할 메모의 번호를 입력해 주세요: '))
            tmp_Title = input('제목을 입력하여 주세요: ')
            tmp_Content = input('내용을 입력하여 주세요: ')

            memoTitle[tmp - 1] = tmp_Title
            memoContent[tmp - 1] = tmp_Content
        except:
            print('잘못된 입력입니다.')
    elif num == 4: # 메모의 번호를 받아 삭제, 인덱스와 번호는 세는 방법이 다르므로 -1, remove 메소드 사용
        try:
            tmp = int(input('삭제할 메모의 번호를 입력해 주세요: '))

            memoTitle.remove(tmp)
            memoContent.remove(tmp)
        except:
            print('잘못된 입력입니다.')
    elif num == 5:
        print('추가기능')
    else:
        print('잘못된 입력입니다. ')

    print('''1. 메뉴 선택
2. 조회
3. 수정
4. 삭제
5. 추가기능
6. 종료''')
    num = int(input('메뉴를 선택해주세요: '))