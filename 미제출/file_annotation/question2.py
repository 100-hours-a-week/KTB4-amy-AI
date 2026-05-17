#변수 선언
firstNumber = 10
secondNumber = 5
operator = '+'

#조건문 연산
if operator == '+': #만약 연산 기호가 + 면 더하기 연산
    result = firstNumber + secondNumber
elif operator == '-': # 만약 - 라면 빼기 연산
    result = firstNumber - secondNumber
elif operator == '*': # * 이라면 곱하기 연산
    result = firstNumber * secondNumber
elif operator == '/': #/ 라면 나누기 연산 (정수 나누기가 아님)
    result = firstNumber / secondNumber
else: # 연산기호가 아닌 다른걸 입력시 출력
    result = "유효하지 않은 연산자입니다."

print(f"결과: {result}")