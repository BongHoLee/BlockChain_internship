
#########################
주석은 모두 영어로 기재했습니다. (부족한 영어로 구글번역의 도움을 받아서 최대한 열심히 작성했지만 조잡합니다 ㅠㅠ)
그리고 문서는 한글로 기재했습니다.
시행착오 및 설명들을 최대한 세밀하게 기재했습니다.
#########################




-	Camera_ : 영상 clip들이 저장되는 디렉토리입니다. 필요에 따라 위치를 외부 디렉토리로 바꿀 수 있습니다.
-	encCamera_ : Camera_ 내의 clip들이 암호화 되어 저장되는 위치입니다. 마찬가지로 필요에 따라 위치를 외부 디렉토리로 변경 가능합니다.
-	otherSc : 당장 프로그램을 실행하는데에 관련이 없는 script들을 저장했습니다. Dec.py의 경우 암호화되어 저장된 clip들을 복호화 하는 test를 수행하였고 ipfsdec.py 역시 마찬가지 입니다. 이후에 복호화 하는데에 혹시라도 필요할까봐 따로 저장해두었습니다.
      -deploy.py : smart contract를 블록체인에 deploy하는 코드입니다. 사실 smart contract의 deploy 테스트는 web 컴파일러를 사용하기를 추천드립니다.
                   해당 스크립트를 실행시키시면 transcation address, abi가 출력되게끔 만들었습니다. main.py 및 mysql.py에 복사/붙여넣기 하셔서 그대로 사용하시면 될 것 같습니다.
      -metaData.sol : 현재 smart contract 코드입니다.

-	keyDir : 암호화에 필요한 private key, publice key가 텍스트 형식으로 저장되어있습니다. Aes key의 경우 영상 clip 하나당 생성되는데다 private key로 enc_AES key를 복호화 가능하기 때문에 따로 저장하지 않습니다.
-	그 외의 EncDec.py 부터 updateDir.py까지는 프로그램을 실행하기 위한 스크립트입니다.

그 다음으로 프로그램을 실행하기위한 script에 대해 정리하겠습니다.
-	Main.py : 이름 그대로 프로그램을 실행하기 위한 메인 스크립트 입니다. 해당 스크립트에서 여러 기능들을 스레드화 하여 구동합니다.
-	EncDec.py : main 스크립트가 실행하는데에 암호화 과정에서 호출하는 스크립트 입니다. 즉 library로써 main.py에 import됩니다.
-	updateDir.py : main 스크립트가 실행하는데에 머클 디렉토리화 수행 과정에서 호출하는 스크립트입니다. EncDec.py와 마찬가지로 library로써 main.py에 import 됩니다.
-	mysql.py : 현재 main프로그램과는 상관이 없습니다. 다만 Mac mini에서 smart contract에 저장된 메타데이터를 mysql database table에 저장하는 코드입니다. 독립적으로써 Mac mini에서만 실행합니다.
-	test.db : sqlite의 데이터베이스 파일입니다. 1분간격 영상의 메타데이터를 저장하기 위한 metaData 테이블, 머클 디렉토리 데이터를 저장하는 Camera1, Camera2, Camera3(카메라 이름으로써 임의로 설정했습니다)테이블이 존재합니다.
-	Filelog.txt : 일전에 모니터링 프로그램을 만들 때에 영상이 제대로 저장되는지 log를 남기기 위한 텍스트 파일입니다. 현재는 database table에 저장하기 때문에 큰 필요성은 없습니다.


해당 프로그램은 Mac book에서 테스트 이후 Rasspberry pi로 이식합니다.
현재 코드는 Mac book에서 작성하고 테스트되었기 때문에 영상 clip이 저장되는 디렉토리 등의 path가 Raspberry pi의 환경과 다릅니다.
Raspberry pi로 이식한 뒤에는 path설정을 환경에 맞게 재구성 해주어야합니다.
main.py, EncDec.py 두개 스크립트의 상단에 정의된 path만 변경해주시면 됩니다.


설치해야할 모듈

**모듈을 설치하시기 전에 주의*******************************************************************************************
watchdog, geocoder, web3, py-solc와 같은 모듈을 설치하시고 난 뒤 uninstall pycryptodome를 수행후 pycrypto 모듈을 설치해주세요
pycryptodome 모듈이 존재하면 현재 구현된 암호화 및 복호화 관련 코드가 수행이 안됩니다.
pycryptodome의 경우 web3를 설치하는 과정에서 같이 설치가 됩니다. 따라서 수동으로 지워주셔야 합니다.
*****************************************************************************************************************
1. pip install watchdog
2. pip insatll geocoder
3. pip install py-solc
4. pip install Web3
5. pip uninsatll pycryptodome           -> pycryptodome 삭제
6. pip install pycrypto                 -> pycrypto 설치
