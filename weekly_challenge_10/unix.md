## 기동 직후
![img](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.10.05%E2%80%AFPM.png)
- ps 명령어를 통하여 현재 서버가 정상적으로 띄워졌음을 확인
- 이후 free를 통하여 개인프로젝트가 메모리르 어느정도 사용하는지도 확인하였다.
![img](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.11.28%E2%80%AFPM.png)
- 그냥 top 했을때의 모습, 단순히 프로젝트를 띄워놓기만 한 상황이기에 cpu 사용량이 크게 차이 나지는 않지만 개인프로젝트(24298)만 cpu가 사용되고 있음을 알 수 있다.
![img](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.10.45%E2%80%AFPM.png)
- 24298을 지정해서 top 했을때의 모습

## 부하
![img.png](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.15.14%E2%80%AFPM.png)
- 부하를 주자 확연히 다른 프로세스들과는 달리 cpu 사용률이 치솟았음을 알 수 있다

## 종료
![](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.17.34%E2%80%AFPM.png)
![](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.18.39%E2%80%AFPM.png)
- 메모리 사용량이 줄어들었음이 확실히 보임, 또한 top를 하였을때 작동중인 프로세스가 없음을 통해 종료되었음을 알 수 있다.

---
## wireshark
![](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-21%20at%208.51.27%E2%80%AFPM.png)
![](https://github.com/100-hours-a-week/KTB4-amy-AI/blob/main/weekly_challenge_10/Screenshot%202026-07-22%20at%209.43.22%E2%80%AFAM.png)

---
## 회고
단순히 서버를 리눅스에 띄우는 것부터 고난이었다. 현재 AWS 신규 가입자용 무료 요금제를 쓰고 있고 혹시 몰라 가장 저렴한 서버를 사용했는데 내가 사용할 수 있는 메모리는 1gb였다. 문제는 내가 개인프로젝트 임베딩 모델로 제미나이를 쓰는 게 아닌 로컬 모델을 쓰고 있다는 사실이었는데 아니나 다를까, 개인프로젝트를 실행시키는 족족 무한 로딩에 걸린 상태였다. 어쩔 수 없이 LLM의 도움을 받았는데 스와핑을 추천하여 구현까지 해 보였다 혹시 몰라 터미널을 하나 더 띄워놓고 free를 입력해 가며 여유 공간을 보았는데 무난하게 실행되는 걸 확인했다. 스와핑 기술은 볼 때마다 신기한것 같다 부족한 메모리 공간을 디스크에서 뜯어온다니…. 이후 부하를 준 상태 그냥 실행만 시켜놓은 상태 종료한 상태 전부 비교해 봤을 때 확연히 다른 모습을 보여주었다. 이 외에도 여러 리눅스 명령어를 입력해 보며 개념을 상기시킬 좋은 기회였다. 또 항상 TCP와 같은 네트워크 통신 요소들을 확인할 수 없음에 아쉬웠는데 와이어샤크를 이용하니 HTTP FLOW까지 확인 가능하다는 사실이 놀라웠다. 네트워크 분야는 확실히 무지에 가까운 것 같다. 더 정진해야겠다.