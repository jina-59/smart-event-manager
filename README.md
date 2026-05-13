1. Review Form Page (review_form.html)
사용자가 별점과 후기를 남기는 페이지

포함 요소:
- 해당 이벤트 제목 및 날짜 (Read-only)
- 별점 선택: 1점~5점 (별 모양 아이콘 클릭 방식)
- 텍스트 입력창: 후기를 자유롭게 쓸 수 있는 큰 입력 칸
- 버튼: [Submit Review] 및 [Cancel] 버튼

------------------------------------------

2. My Reviews Page (my_reviews.html)
내가 쓴 리뷰들만 모아서 관리하는 페이지

포함 요소:
- 리뷰 카드 리스트: 이벤트명, 내가 준 별점, 작성한 내용, 작성 날짜
- 관리 버튼: 각 리뷰 옆에 [Edit] 및 [Delete] 버튼
- 빈 상태 안내: 작성한 리뷰가 없을 때 "작성한 리뷰가 없습니다"라는 메시지 노출

--------------------------------------------

3. Booking Detail Page (booking_detail.html)
마이페이지 'Recent Bookings'에서 항목을 눌렀을 때 나오는 상세 내역 페이지

포함 요소:
- 예약 정보: 예약 번호(ID), 결제 일시, 티켓 종류, 수량, 총 결제 금액
- 이벤트 정보: 포스터 이미지, 제목, 장소
- 상태 표시: 'Confirmed', 'Completed' 등 현재 예약 상태 배지
- 액션 버튼: 하단에 [Write a Review] 버튼 (이미 썼다면 [View My Review]로 변경 가능하게 설계)

--------------------------------------------

4. Profile Settings Page (profile.html)
개인정보를 수정하는 페이지

포함 요소:
- 입력 필드: 이름, 이메일, 비밀번호 변경 칸
- 저장 버튼: [Update Profile] 버튼
- 계정 관리: 최하단에 작게 [Delete Account] 링크나 버튼

---------------------------------------------

5. Recent Bookings 리스트 클릭 이벤트 추가
- 내용: 마이페이지의 'Recent Bookings' 테이블에서 이벤트 이름(Event Name)이나 행 전체(Table Row)에 클릭이 가능하도록 <a> 태그나 스타일을 적용.
- 디자인 포인트: 마우스를 올렸을 때(Hover) 배경색이 살짝 변하거나 손가락 모양 커서가 나타나서 '클릭할 수 있다'는 느낌.
- 연결 페이지: 클릭 시 아까 말한 Booking Detail Page(booking_detail.html)로 이동.

----------------------------------------------


6. Sign Up Page (signup.html)
새로운 사용자가 계정을 생성하는 페이지

포함 요소:
- 입력 필드: 사용자 아이디(Username), 이메일, 비밀번호, 비밀번호 확인
- 추가 정보 (선택): 이름(Full Name), 전화번호 등
- 버튼: [Create Account] 버튼
- 로그인 연결: "이미 계정이 있나요? [Login]" 링크

  event_form.html 수정 필요
기능: 사용자가 [+ Add Ticket Type] 버튼을 누르면 입력 칸(티켓 이름, 가격, 수량)이 한 줄씩 새로 생김.

포함 요소:
- Ticket Name: (예: Standard, VIP, Student)
- Price (€): 각 티켓의 개별 가격
- Quantity: 해당 티켓의 할당 수량
- Delete : 잘못 만든 줄을 삭제하는 버튼



5/13

point?
Review 개수 연동 안됨 (5개 이벤트 참석했는데 3개만 리뷰 남긴 경우)


새로 만들 페이지 : my ticket - 전체내가 예약한 내역 랑 과거 페스트
My review 에 위에 대시바 ?가 사라짐


My page에서 자신에 대한 정보에 대한 설정 필요

데이터베이스에서 비밀번호 중복됨 이거 세팅 다시할걸 !

Main page - Learn more(삭제)
Featured Event(Top event로 변경 ?) booking 제일 많은 세개만 나두고 view all 눌렀을때 전체가 이벤트가 보이기

View_All : 예매할 이벤트가 달별로 나오게

대시바에 지금은 눌러도 이동하는게 없음 - 카톡 확인

my admin
작은 팝업창 ? 대시보드 나오게

포인트-필요엇음
