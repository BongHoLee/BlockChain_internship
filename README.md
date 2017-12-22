# ip camera - ipfs - blockchain 


해당 프로그램은 ipcamera를 이용하여 찍은 영상 데이터를 encryption 하여 ipfs에 add 후 metaData를 blockChain에 올리기 위한 프로그램.

현재까지 진행사항은 ipfs add 이후 encryption 및 ipfs add, DataBase insert 과정까지 완료.

외부 모듈로는 whatchdog(영상 데이터 저장 디렉토리를 모니터링 하기 위함) / geocoder (ipCamera의 위치를 확인) / Crypto (데이터 encryption 및 private_key와 public_key 할당)
등이 있다.

코드가 조악하여 많은 개선이 필요하고 이후 blockchain에 배포하기 위한 설계도 필요함.

예상 소요 시간은 1월 중순까지 프로토타입이 완성 될 듯 함.
