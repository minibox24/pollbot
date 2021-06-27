# Pollbot
디스코드 버튼을 이용한 투표봇입니다.

기본적으로는 Sqlite3을 이용하지만,
투표한 유저가 적을 경우에는 버튼의 custom_id에 데이터를 저장하는 방식을 선택하였습니다.

만약 봇의 소스를 사용하신다면, 반드시 유저가 쉽게 볼 수 있는 장소에 출처를 남겨주세요.

## 예시
![image](https://user-images.githubusercontent.com/61264156/123548691-cd0f4000-d7a0-11eb-8f0d-ffa001b741a7.png)

## 실행
run.py에 토큰 작성 후,
```bash
pip install discord
pip install tortoise-orm

python run.py
```

## 커맨드
`!투표 "타이틀" "옵션 1" "옵션 2"` 투표 메시지를 생성합니다.
`!개표` 커맨드를 사용한 메시지가 투표 메시지의 답장이라면, 해당 투표에 참여한 유저들을 출력합니다.
`!종료` DB를 정리 후, 프로세스를 종료합니다.
